import pandas as pd

def generate_screening_report(all_metrics, top_n=10):
    """
    Phase 5: Generates ranking tables and filters from the analyzed stocks.
    """
    if not all_metrics:
        return "No data available for screening."
        
    df = pd.DataFrame(all_metrics)
    
    # Ensure numeric columns are numeric for sorting
    numeric_cols = [
        '1Y_total_return', '3Y_total_return', '5Y_total_return',
        '1Y_annualized_return', '3Y_annualized_return', '5Y_annualized_return',
        'volatility', 'max_drawdown', 'Market Cap (B)'
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    report = []
    report.append("="*60)
    report.append(f"{'BATCH SCREENING & RANKING':^60}")
    report.append("="*60)

    # 1. Top Performers (1Y Return)
    if '1Y_total_return' in df.columns:
        report.append(f"\nTOP {top_n} BY 1-YEAR RETURN:")
        top_return = df.sort_values(by='1Y_total_return', ascending=False).head(top_n)
        for _, row in top_return.iterrows():
            report.append(f"  {row['ticker']:<10}: {row['1Y_total_return']:.2%}")

    # 2. Most Stable (Lowest Volatility)
    if 'volatility' in df.columns:
        report.append(f"\nTOP {top_n} MOST STABLE (LOW VOLATILITY):")
        low_vol = df.sort_values(by='volatility', ascending=True).head(top_n)
        for _, row in low_vol.iterrows():
            report.append(f"  {row['ticker']:<10}: {row['volatility']:.2%}")

    # 3. Best Value/Momentum (Return / Volatility "Sharpe-like" ratio)
    if '1Y_total_return' in df.columns and 'volatility' in df.columns:
        df['return_per_risk'] = df['1Y_total_return'] / df['volatility']
        report.append(f"\nTOP {top_n} BY RETURN-TO-RISK RATIO:")
        top_ratio = df.sort_values(by='return_per_risk', ascending=False).head(top_n)
        for _, row in top_ratio.iterrows():
            report.append(f"  {row['ticker']:<10}: {row['return_per_risk']:.2f}")

    # 4. Filters (e.g., Growth stocks in uptrend)
    report.append("\n" + "-"*60)
    report.append("SCREENING FILTERS:")
    
    # Filter: Up-trending Mega Caps
    if 'insights' in df.columns and 'Market Cap (B)' in df.columns:
        # Check if "Strong long-term uptrend" is in the insights list
        mega_uptrend = df[
            (df['Market Cap (B)'] > 100) & 
            (df['insights'].apply(lambda x: any("Strong long-term uptrend" in s for s in x if isinstance(x, list))))
        ]
        report.append(f"  Mega-Cap Stocks in Uptrend: {', '.join(mega_uptrend['ticker'].tolist()) or 'None'}")

    # Filter: High Risk / High Reward (Return > 20% and Vol > 30%)
    if '1Y_total_return' in df.columns and 'volatility' in df.columns:
        high_risk = df[(df['1Y_total_return'] > 0.20) & (df['volatility'] > 0.30)]
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
