import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path

def plot_price_with_ma(df, ticker, output_dir):
    """
    Plots price with 50 and 200 day moving averages.
    """
    df = df.copy()
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
    
    df = df.sort_index()
    
    # Calculate MAs for plotting
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['MA200'] = df['Close'].rolling(window=200).mean()
    
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Close'], label='Close Price', alpha=0.8, color='blue')
    plt.plot(df.index, df['MA50'], label='50-Day MA', alpha=0.9, color='orange')
    plt.plot(df.index, df['MA200'], label='200-Day MA', alpha=0.9, color='red')
    
    plt.title(f"{ticker} Price and Moving Averages")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    output_path = Path(output_dir) / f"{ticker}_price_ma.png"
    plt.savefig(output_path)
    plt.close()
    return output_path

def plot_drawdown(df, ticker, output_dir):
    """
    Plots the drawdown curve.
    """
    df = df.copy()
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
    
    rolling_max = df['Close'].cummax()
    drawdown = (df['Close'] - rolling_max) / rolling_max
    
    plt.figure(figsize=(12, 4))
    plt.fill_between(df.index, drawdown, 0, color='red', alpha=0.3)
    plt.plot(df.index, drawdown, color='red', alpha=0.8)
    
    plt.title(f"{ticker} Historical Drawdown")
    plt.ylabel("Drawdown %")
    plt.grid(True, alpha=0.3)
    
    # Format Y tags as percentages
    plt.gca().set_yticklabels(['{:.0%}'.format(x) for x in plt.gca().get_yticks()])
    
    output_path = Path(output_dir) / f"{ticker}_drawdown.png"
    plt.savefig(output_path)
    plt.close()
    return output_path

def plot_comparison(df, benchmark_df, ticker, benchmark_ticker, output_dir):
    """
    Plots cumulative returns of stock vs benchmark.
    """
    df = df.copy()
    bdf = benchmark_df.copy()
    
    for d in [df, bdf]:
        if 'Date' in d.columns:
            d['Date'] = pd.to_datetime(d['Date'])
            d.set_index('Date', inplace=True)
        d.sort_index(inplace=True)
    
    # Align dates
    combined = pd.DataFrame({
        ticker: df['Close'],
        benchmark_ticker: bdf['Close']
    }).dropna()
    
    # Calculate cumulative returns: (Price / Start Price) - 1
    cum_returns = (combined / combined.iloc[0]) - 1
    
    plt.figure(figsize=(12, 6))
    plt.plot(cum_returns.index, cum_returns[ticker], label=ticker, color='blue')
    plt.plot(cum_returns.index, cum_returns[benchmark_ticker], label=benchmark_ticker, color='gray', linestyle='--')
    
    plt.title(f"Cumulative Returns: {ticker} vs {benchmark_ticker}")
    plt.ylabel("Return %")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.gca().set_yticklabels(['{:.0%}'.format(x) for x in plt.gca().get_yticks()])
    
    output_path = Path(output_dir) / f"{ticker}_vs_{benchmark_ticker}.png"
    plt.savefig(output_path)
    plt.close()
    return output_path

def create_visualizations(df, ticker, benchmark_df=None, benchmark_ticker="SPY", output_dir="output/charts"):
    """
    Main entry point for generating all charts for a stock.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    paths = {}
    print(f"  Generating charts for {ticker}...")
    paths['price_ma'] = plot_price_with_ma(df, ticker, output_dir)
    paths['drawdown'] = plot_drawdown(df, ticker, output_dir)
    
    if benchmark_df is not None:
        paths['comparison'] = plot_comparison(df, benchmark_df, ticker, benchmark_ticker, output_dir)
    
    return paths

def plot_risk_return_scatter(all_metrics, output_dir="output/charts"):
    """
    Plots a scatter chart of Return vs Volatility for all analyzed stocks.
    all_metrics should be a list of dicts with 'ticker', '1Y_total_return', and 'volatility'.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    tickers = [m['ticker'] for m in all_metrics if m.get('volatility') and m.get('1Y_total_return')]
    vols = [m['volatility'] for m in all_metrics if m.get('volatility') and m.get('1Y_total_return')]
    rets = [m['1Y_total_return'] for m in all_metrics if m.get('volatility') and m.get('1Y_total_return')]
    
    if not tickers:
        print("No data for Risk-Return scatter plot.")
        return None
        
    plt.figure(figsize=(10, 8))
    plt.scatter(vols, rets, color='blue', alpha=0.6)
    
    for i, txt in enumerate(tickers):
        plt.annotate(txt, (vols[i], rets[i]), xytext=(5, 5), textcoords='offset points')
        
    plt.title("Risk vs Return (1Y)")
    plt.xlabel("Volatility (Annualized SD)")
    plt.ylabel("1-Year Total Return")
    plt.grid(True, alpha=0.3)
    
    # Format Y tags as percentages
    plt.gca().set_yticklabels(['{:.0%}'.format(x) for x in plt.gca().get_yticks()])
    
    output_path = Path(output_dir) / "risk_return_scatter.png"
    plt.savefig(output_path)
    plt.close()
    return output_path
