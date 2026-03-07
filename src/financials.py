from edgar import set_identity, Company
import pandas as pd
from typing import Optional, List, Dict
import logging

# Set identity for SEC API
set_identity("Jarvis Analytics jarvis@fiscalai.tech")

def get_historical_financials(ticker: str, limit: int = 5) -> Optional[Dict]:
    """
    Fetches historical Income Statement data using high-level edgartools methods.
    """
    try:
        company = Company(ticker)
        facts = company.get_facts()
        
        if not facts:
            return None
            
        # Try multiple tags for Revenue and Net Income
        def get_robust_ts(concepts: List[str]) -> pd.DataFrame:
            for concept in concepts:
                try:
                    df = facts.time_series(concept)
                    if df is not None and not df.empty:
                        return df
                except:
                    continue
            return pd.DataFrame()

        df_rev = get_robust_ts(['revenue', 'us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax', 'us-gaap:Revenues'])
        df_ni = get_robust_ts(['net_income', 'us-gaap:NetIncomeLoss', 'us-gaap:ProfitLoss'])
        df_ocf = get_robust_ts(['us-gaap:NetCashProvidedByUsedInOperatingActivities'])
        df_inv = get_robust_ts(['us-gaap:InventoryNet', 'us-gaap:InventoryGross'])
        df_rec = get_robust_ts(['us-gaap:AccountsReceivableNetCurrent'])
        
        # New for ROIC
        df_op = get_robust_ts(['us-gaap:OperatingIncomeLoss'])
        df_assets = get_robust_ts(['us-gaap:Assets'])
        df_liabs_c = get_robust_ts(['us-gaap:LiabilitiesCurrent'])
        
        results = {}
        
        # Helper to process time series dataframe
        def process_ts_df(df, key):
            if df is not None and not df.empty:
                val_col = 'numeric_value' if 'numeric_value' in df.columns else 'val'
                
                df_copy = df.copy()
                df_copy['year'] = pd.to_datetime(df_copy['period_end']).dt.year.astype(str)
                yr_df = df_copy.sort_values('period_end').drop_duplicates('year', keep='last')
                
                for _, row in yr_df.tail(limit).iterrows():
                    year = row['year']
                    date_str = str(row['period_end'])
                    if year not in results: results[year] = {"year": year, "date": date_str}
                    results[year][key] = float(row[val_col])

        process_ts_df(df_rev, "revenue")
        process_ts_df(df_ni, "net_income")
        process_ts_df(df_ocf, "operating_cash_flow")
        process_ts_df(df_inv, "inventory")
        process_ts_df(df_rec, "receivables")
        process_ts_df(df_op, "operating_income")
        process_ts_df(df_assets, "assets")
        process_ts_df(df_liabs_c, "current_liabilities")
        
        # Convert dict to sorted list
        trend_list = sorted(results.values(), key=lambda x: x['year'])
        
        import yfinance as yf
        try:
            yf_ticker = yf.Ticker(ticker)
            info = yf_ticker.info
            beta = info.get('beta', 1.1)
            if beta is None: beta = 1.1
            shares_out = info.get('sharesOutstanding', 0)
            total_debt = info.get('totalDebt', 0)
            total_cash = info.get('totalCash', 0)
            current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        except:
            beta = 1.1
            shares_out = 0
            total_debt = 0
            total_cash = 0
            current_price = 0
            
        # Simplified WACC: Cost of Equity = Risk Free (4.0%) + Beta * ERP (5.5%)
        # Ignoring debt for simple proxy, so WACC ~ Ke
        wacc = 0.04 + (float(beta) * 0.055)
        
        # Calculate ROIC per year
        for t in trend_list:
            t['wacc'] = wacc * 100 # as percentage
            if 'operating_income' in t and 'assets' in t and 'current_liabilities' in t:
                nopat = t['operating_income'] * 0.79 # Assuming 21% tax rate
                invested_capital = t['assets'] - t['current_liabilities']
                if invested_capital > 0:
                    t['roic'] = (nopat / invested_capital) * 100
                else:
                    t['roic'] = 0.0
            else:
                t['roic'] = 0.0
                
        # Advanced Valuation (DCF Modeling)
        valuation = None
        if len(trend_list) > 0 and shares_out > 0 and current_price > 0:
            latest = trend_list[-1]
            ocf = latest.get('operating_cash_flow', 0)
            
            if ocf > 0:
                fcf = ocf * 0.8 # Crude proxy for FCF: OCF - CapEx
                
                # Growth rate: average of last up to 3 years revenue growth, capped at 15% and floored at 2%
                growth_rates = []
                for i in range(1, min(4, len(trend_list))):
                    prev_idx = -(i+1)
                    curr_idx = -i
                    if len(trend_list) >= abs(prev_idx):
                        prev_rev = trend_list[prev_idx].get('revenue', 1)
                        curr_rev = trend_list[curr_idx].get('revenue', 1)
                        if prev_rev > 0:
                            growth_rates.append((curr_rev - prev_rev) / prev_rev)
                
                avg_growth = sum(growth_rates) / len(growth_rates) if growth_rates else 0.05
                proj_growth = max(0.02, min(0.15, avg_growth))
                
                term_growth = 0.025 # 2.5% perpetual growth
                discount_rate = wacc
                
                # Project 5 years
                discounted_fcfs = []
                current_fcf = fcf
                for i in range(1, 6):
                    current_fcf *= (1 + proj_growth)
                    pv_fcf = current_fcf / ((1 + discount_rate) ** i)
                    discounted_fcfs.append(pv_fcf)
                
                sum_pv_fcfs = sum(discounted_fcfs)
                
                # Terminal Value
                terminal_value = (current_fcf * (1 + term_growth)) / max(0.001, (discount_rate - term_growth))
                pv_tv = terminal_value / ((1 + discount_rate) ** 5)
                
                enterprise_value = sum_pv_fcfs + pv_tv
                equity_value = enterprise_value + total_cash - total_debt
                
                intrinsic_value = equity_value / shares_out
                
                margin_of_safety = (intrinsic_value - current_price) / current_price
                
                valuation = {
                    "fcf": fcf,
                    "wacc": wacc,
                    "projected_growth_rate": proj_growth,
                    "terminal_growth_rate": term_growth,
                    "enterprise_value": enterprise_value,
                    "equity_value": equity_value,
                    "shares_outstanding": shares_out,
                    "intrinsic_value": intrinsic_value,
                    "current_price": current_price,
                    "margin_of_safety": margin_of_safety
                }
        
        # Red Flag Detection Logic
        red_flags = []
        if len(trend_list) >= 2:
            latest = trend_list[-1]
            prev = trend_list[-2]
            
            # 1. Cash Flow Divergence: Net Income up, but OCF down
            ni_growth = latest.get('net_income', 0) - prev.get('net_income', 0)
            ocf_growth = latest.get('operating_cash_flow', 0) - prev.get('operating_cash_flow', 0)
            
            if ni_growth > 0 and ocf_growth < 0:
                red_flags.append({
                    "type": "Cash Flow Divergence",
                    "severity": "High",
                    "description": f"Net Income grew by ${(ni_growth/1e9):.1f}B, while Operating Cash Flow declined by ${(abs(ocf_growth)/1e9):.1f}B. This divergence requires investigation into earnings quality."
                })
                
            # 2. Inventory / Receivables Spike vs Sales
            rev_growth_pct = (latest.get('revenue', 1) - prev.get('revenue', 1)) / max(prev.get('revenue', 1), 1)
            
            inv_latest = latest.get('inventory', 0)
            inv_prev = prev.get('inventory', 0)
            if inv_prev > 0:
                inv_growth_pct = (inv_latest - inv_prev) / inv_prev
                if inv_growth_pct > (rev_growth_pct + 0.15): # Inventory grew 15% faster than sales
                    red_flags.append({
                        "type": "Inventory Bloat",
                        "severity": "Medium",
                        "description": f"Inventory grew by {(inv_growth_pct*100):.1f}%, significantly outpacing Revenue growth of {(rev_growth_pct*100):.1f}%. May indicate slowing demand."
                    })
                    
            rec_latest = latest.get('receivables', 0)
            rec_prev = prev.get('receivables', 0)
            if rec_prev > 0:
                rec_growth_pct = (rec_latest - rec_prev) / rec_prev
                if rec_growth_pct > (rev_growth_pct + 0.15):
                    red_flags.append({
                        "type": "Receivables Spike",
                        "severity": "Medium",
                        "description": f"Accounts Receivable grew by {(rec_growth_pct*100):.1f}%, outpacing Revenue growth. Company may be struggling to collect cash from customers."
                    })

        return {
            "ticker": ticker,
            "company_name": company.name,
            "cik": company.cik,
            "trends": trend_list,
            "red_flags": red_flags,
            "valuation": valuation
        }
        
    except Exception as e:
        logging.error(f"Error fetching financials for {ticker}: {e}")
        return None

if __name__ == "__main__":
    # Test
    print(get_historical_financials("AAPL"))
