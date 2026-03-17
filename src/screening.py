import pandas as pd
import numpy as np

def generate_screening_report(all_metrics, top_n=10):
    """
    Phase 5: Generates ranking tables and filters from the analyzed stocks.
    Works with both normalized (frontend-friendly) and backend column names.
    """
    if not all_metrics:
        return "No data available for screening."
        
    df = pd.DataFrame(all_metrics)
    
    # Map normalized column names back to internal names for analysis
    # (metrics are returned normalized from analyze_stock_data)
    col_map = {
        "1Y Return": "1Y_total_return",
        "Volatility": "volatility",
        "Max Drawdown": "max_drawdown",
        "Dividend Yield": "dividend_yield",
        "Profit Margin": "profit_margins",
    }
    
    # Use normalized names if present, fall back to internal names
    df_display = df.copy()
    
    # Ensure numeric columns are numeric for sorting
    numeric_cols_to_check = [
        'Market Cap (B)', '1Y Return', 'Volatility', 'Max Drawdown',
        '1Y_total_return', '3Y_total_return', '5Y_total_return',
        'volatility', 'max_drawdown'
    ]
    
    for col in numeric_cols_to_check:
        if col in df_display.columns:
            df_display[col] = pd.to_numeric(df_display[col], errors='coerce')

    report = []
    report.append("="*60)
    report.append(f"{'BATCH SCREENING & RANKING':^60}")
    report.append("="*60)

    # 1. Top Performers (1Y Return) - use normalized name with fallback
    return_col = "1Y Return" if "1Y Return" in df_display.columns else "1Y_total_return"
    if return_col in df_display.columns:
        report.append(f"\nTOP {top_n} BY 1-YEAR RETURN:")
        top_return = df_display.sort_values(by=return_col, ascending=False).head(top_n)
        for _, row in top_return.iterrows():
            val = row[return_col]
            if pd.notna(val):
                report.append(f"  {row['ticker']:<10}: {val:.2%}")

    # 2. Most Stable (Lowest Volatility)
    vol_col = "Volatility" if "Volatility" in df_display.columns else "volatility"
    if vol_col in df_display.columns:
        report.append(f"\nTOP {top_n} MOST STABLE (LOW VOLATILITY):")
        low_vol = df_display.sort_values(by=vol_col, ascending=True).head(top_n)
        for _, row in low_vol.iterrows():
            val = row[vol_col]
            if pd.notna(val):
                report.append(f"  {row['ticker']:<10}: {val:.2%}")

    # 3. Best Value/Momentum (Return / Volatility "Sharpe-like" ratio)
    if return_col in df_display.columns and vol_col in df_display.columns:
        # Safe division: replace zero volatility with NaN to avoid division errors
        volatility_safe = df_display[vol_col].replace(0, np.nan)
        df_display['return_per_risk'] = df_display[return_col] / volatility_safe
        report.append(f"\nTOP {top_n} BY RETURN-TO-RISK RATIO:")
        top_ratio = df_display.sort_values(by='return_per_risk', ascending=False, na_position='last').head(top_n)
        for _, row in top_ratio.iterrows():
            val = row['return_per_risk']
            if pd.notna(val) and not np.isinf(val):  # Check for both NaN and infinity
                report.append(f"  {row['ticker']:<10}: {val:.2f}")

    # 4. Dividends (Highest Yield)
    div_col = "Dividend Yield" if "Dividend Yield" in df_display.columns else "dividend_yield"
    if div_col in df_display.columns:
        report.append(f"\nTOP {top_n} HIGHEST DIVIDEND YIELD:")
        top_div = df_display.sort_values(by=div_col, ascending=False, na_position='last').head(top_n)
        for _, row in top_div.iterrows():
            val = row[div_col]
            if pd.notna(val):
                report.append(f"  {row['ticker']:<10}: {val:.2%}")

    # 5. Profitability (Profit Margins)
    profit_col = "Profit Margin" if "Profit Margin" in df_display.columns else "profit_margins"
    if profit_col in df_display.columns:
        report.append(f"\nTOP {top_n} MOST PROFITABLE (NET MARGINS):")
        top_prof = df_display.sort_values(by=profit_col, ascending=False, na_position='last').head(top_n)
        for _, row in top_prof.iterrows():
            val = row[profit_col]
            if pd.notna(val):
                report.append(f"  {row['ticker']:<10}: {val:.2%}")

    # 6. Filters (e.g., Growth stocks in uptrend)
    report.append("\n" + "-"*60)
    report.append("SCREENING FILTERS:")
    
    # Filter: Up-trending Mega Caps
    if 'insights' in df_display.columns and 'Market Cap (B)' in df_display.columns:
        # Check if "Strong long-term uptrend" is in the insights list
        mega_uptrend = df_display[
            (df_display['Market Cap (B)'] > 100) & 
            (df_display['insights'].apply(lambda x: any("Strong long-term uptrend" in s for s in x if isinstance(x, list))))
        ]
        report.append(f"  Mega-Cap Stocks in Uptrend: {', '.join(mega_uptrend['ticker'].tolist()) or 'None'}")

    # Filter: High Risk / High Reward (Return > 20% and Vol > 30%)
    if return_col in df_display.columns and vol_col in df_display.columns:
        high_risk = df_display[(df_display[return_col] > 0.20) & (df_display[vol_col] > 0.30)]
        report.append(f"  High-Risk / High-Reward:   {', '.join(high_risk['ticker'].tolist()) or 'None'}")

    report.append("="*60)
    return "\n".join(report)

def save_screening_results(all_metrics, filename="output/screening_results.csv"):
    """
    Saves the combined metrics to a CSV for external analysis.
    """
    if not all_metrics:
        return
    df = pd.DataFrame(all_metrics)
    # Drop insights from CSV as it's a list and makes CSV messy
    if 'insights' in df.columns:
        df = df.drop(columns=['insights'])
    df.to_csv(filename, index=False)
    print(f"Full screening data saved to {filename}")
