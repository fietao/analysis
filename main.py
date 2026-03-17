# main.py
import pandas as pd
import time 
from src.config import TICKERS, start_date, end_date
from src.data_loader import download_stock_data, get_stock_info
from src.config import DEV_MODE, DEV_TICKERS_LIMIT
from src.analytics import analyze_stock_data
from src.visualizer import create_visualizations, plot_risk_return_scatter
from src.screening import generate_screening_report, save_screening_results
from src.document_processor import process_filing
from pathlib import Path

def main():
    all_data = []
    failed_tickers = []
    all_metrics_list = [] # Store for scatter plot
    
    # Selection of tickers to run
    tickers_to_run = TICKERS
    if DEV_MODE:
        tickers_to_run = TICKERS[:DEV_TICKERS_LIMIT]
        print(f"[DEV_MODE] Processing {len(tickers_to_run)}/{len(TICKERS)} tickers")
    else:
        print(f"[PRODUCTION] Processing all {len(TICKERS)} tickers")
        
    Path("ticker_data").mkdir(exist_ok=True)
    Path("output/charts").mkdir(parents=True, exist_ok=True)
    Path("input/filings").mkdir(parents=True, exist_ok=True)
    
    # Download benchmark data (SPY)
    print("Downloading benchmark (SPY)...")
    spy_df = download_stock_data("SPY", start_date, end_date)
    
    # Metadata cache
    stock_info = {}
    filing_insights = {}
    
    for ticker in tickers_to_run:
        print(f"Processing {ticker}...")
        
        # Fetch metadata
        info = get_stock_info(ticker)
        if info:
            stock_info[ticker] = info
            
        # Phase 7: Document Analysis
        filing_data = process_filing(ticker)
        if filing_data:
            filing_insights[ticker] = filing_data

        csv_path = f"ticker_data/{ticker}.csv"
        
        if Path(csv_path).exists():
            print(f"  Loading existing data...")
            df = pd.read_csv(csv_path)
            all_data.append(df)
        else:
            df = download_stock_data(ticker, start_date, end_date)
            if df is not None: 
                df.to_csv(csv_path, index=False)
                all_data.append(df)
            else:
                print(f"  Failed to download data.")
                failed_tickers.append(ticker)
                continue
        
        # Generate Individual Charts (Phase 4)
        create_visualizations(df, ticker, benchmark_df=spy_df)
            
    if failed_tickers:
        print(f"Failed to download data for {failed_tickers}")    
        with open("failed_tickers.txt", "w") as f:
            f.write("\n".join(failed_tickers))
            
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df = combined_df.sort_values(by=["ticker", "Date"])
        combined_df.to_csv("all_stocks.csv", index=False)
        print("\nData saved to all_stocks.csv\n")
        
        # --- PHASE 2 & 3: ANALYTICS & INSIGHTS ---
        print("="*60)
        print(f"{'STOCK ANALYSIS REPORT':^60}")
        print("="*60)
        
        for ticker in tickers_to_run:
            ticker_df = combined_df[combined_df['ticker'] == ticker]
            
            if not ticker_df.empty:
                metrics = analyze_stock_data(ticker_df)
                metrics['ticker'] = ticker
                
                # Add market cap and fundamentals to metrics for screening and printing
                if ticker in stock_info:
                    info = stock_info[ticker]
                    
                    # Store raw info keys for screening.py
                    metrics['market_cap'] = info.get('market_cap')
                    metrics['forward_pe'] = info.get('forward_pe')
                    metrics['dividend_yield'] = info.get('dividend_yield')
                    metrics['profit_margins'] = info.get('profit_margins')
                    metrics['revenue_growth'] = info.get('revenue_growth')

                    # Prepare display versions for individual report
                    if info.get('market_cap'):
                        metrics['Market Cap (B)'] = info['market_cap'] / 1e9
                    if info.get('forward_pe'):
                        metrics['Forward PE'] = info['forward_pe']
                    if info.get('dividend_yield'):
                        metrics['Div Yield'] = info['dividend_yield']
                    if info.get('profit_margins'):
                        metrics['Profit Margin'] = info['profit_margins']
                    if info.get('revenue_growth'):
                        metrics['Rev Growth'] = info['revenue_growth']
                
                all_metrics_list.append(metrics.copy())
                
                # Set up display
                if ticker in stock_info:
                    print(f"\n{stock_info[ticker].get('name', ticker)} ({ticker})")
                else:
                    print(f"\n{ticker}:")
                
                # Separate insights from raw metrics for cleaner printing
                insights = metrics.pop('insights', [])
                
                # Hide internal/duplicate keys from printing
                internal_keys = ['ticker', 'market_cap', 'forward_pe', 'dividend_yield', 'profit_margins', 'revenue_growth']
                
                for key, val in metrics.items():
                    if val is not None and key not in internal_keys:
                        # Format logic
                        if any(x in key for x in ['return', 'volatility', 'max_drawdown', 'Yield', 'Margin', 'Growth']):
                            print(f"  {key:25}: {val:.2%}")
                        elif 'Market Cap' in key:
                            print(f"  {key:25}: ${val:,.2f}B")
                        else:
                            print(f"  {key:25}: {val:.2f}")
                
                if insights:
                    print(f"\n  Analyst Notes:")
                    for note in insights:
                        print(f"  - {note}")

                # Display Filing Insights (Phase 7)
                if ticker in filing_insights:
                    print(f"\n  Filing Analysis ({filing_insights[ticker]['filename']}):")
                    for section, content in filing_insights[ticker]['sections'].items():
                        print(f"  [{section}]")
                        print(f"    {content[:300]}...")
        
        # Final Summary Chart (Phase 4)
        plot_risk_return_scatter(all_metrics_list)
        
        # --- PHASE 5: SCREENING & RANKING ---
        screening_report = generate_screening_report(all_metrics_list)
        print("\n" + screening_report)
        
        save_screening_results(all_metrics_list)
        
        print("\n" + "="*60)
        print(f"Charts saved in output/charts/")
    else:
        print("No data downloaded")

if __name__ == "__main__":
    main()
