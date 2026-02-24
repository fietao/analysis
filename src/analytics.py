import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def calculate_annualized_return(total_return, years):
    """
    Converts a cumulative return to an annualized return.
    Formula: ((1 + total_return) ** (1/years)) - 1
    """
    if total_return is None or years <= 0:
        return None
    return ((1 + total_return) ** (1 / years)) - 1

def calculate_volatility(df):
    """
    Calculates annualized volatility (standard deviation of daily returns).
    Assumes 252 trading days in a year.
    """
    if df is None or len(df) < 5:
        return None
    
    # Calculate daily percentage change
    daily_returns = df['Close'].pct_change().dropna()
    
    # Standard deviation of daily returns * sqrt(252)
    daily_vol = daily_returns.std()
    annualized_vol = daily_vol * np.sqrt(252)
    
    return annualized_vol

def calculate_max_drawdown(df):
    """
    Calculates the maximum peak-to-trough decline.
    """
    if df is None or df.empty:
        return None
        
    # Calculate the running maximum
    rolling_max = df['Close'].cummax()
    # Calculate drawdown from peak
    drawdown = (df['Close'] - rolling_max) / rolling_max
    # Find the minimum (most negative) drawdown
    return drawdown.min()

def calculate_returns(df):
    """
    Calculates 1Y, 3Y, and 5Y total and annualized returns.
    """
    if df is None or df.empty:
        return None

    df = df.copy()
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
    
    df = df.sort_index()
    latest_date = df.index.max()
    latest_price = df['Close'].iloc[-1]

    metrics = {}

    for years in [1, 3, 5]:
        target_date = latest_date - pd.DateOffset(years=years)
        mask = df.index <= target_date
        
        if mask.any():
            start_price_date = df.index[mask].max()
            start_price = df.loc[start_price_date, 'Close']
            
            total_return = (latest_price - start_price) / start_price
            metrics[f'{years}Y_total_return'] = total_return
            
            # Annualize if more than 1 year (or just for all)
            ann_return = calculate_annualized_return(total_return, years)
            metrics[f'{years}Y_annualized_return'] = ann_return
        else:
            metrics[f'{years}Y_total_return'] = None
            metrics[f'{years}Y_annualized_return'] = None

    return metrics

def get_moving_averages(df):
    """Calculates 50 and 200 day moving averages."""
    if df is None or len(df) < 200:
        # Return what we can if 200 days aren't available
        df = df.copy()
        df['MA50'] = df['Close'].rolling(window=50).mean() if len(df) >= 50 else None
        df['MA200'] = df['Close'].rolling(window=200).mean() if len(df) >= 200 else None
    else:
        df = df.copy()
        df['MA50'] = df['Close'].rolling(window=50).mean()
        df['MA200'] = df['Close'].rolling(window=200).mean()
    
    latest = df.iloc[-1]
    return {
        'MA50': latest['MA50'],
        'MA200': latest['MA200']
    }

def generate_insights(metrics, current_price):
    """
    Phase 3: Rule-based interpretations of stock metrics.
    Translates raw numbers into human-readable analyst notes.
    """
    insights = []
    
    if not metrics:
        return ["No data available for insights."]

    # --- TREND ANALYSIS ---
    ma50 = metrics.get('MA50')
    ma200 = metrics.get('MA200')
    
    if ma50 and ma200:
        if current_price > ma50 > ma200:
            insights.append("Strong long-term uptrend")
        elif current_price < ma50 < ma200:
            insights.append("Clear long-term downtrend")
        elif current_price > ma200:
            insights.append("Bullish: Price above 200-day average")
        else:
            insights.append("Bearish: Price below 200-day average")

    # --- VOLATILITY ANALYSIS ---
    vol = metrics.get('volatility')
    if vol:
        if vol > 0.40:
            insights.append("Extremely high volatility (Speculative risk)")
        elif vol > 0.25:
            insights.append("High volatility")
        elif vol < 0.15:
            insights.append("Low volatility (Stable price action)")

    # --- DRAWDOWN ANALYSIS ---
    dd = metrics.get('max_drawdown')
    if dd:
        if dd < -0.40:
            insights.append("Historical record of severe drawdowns (-40%+)")
        elif dd < -0.20:
            insights.append("Moderate historical drawdowns")
        elif dd > -0.10:
            insights.append("Strong capital preservation (Small drawdowns)")

    # --- MOMENTUM & RETURNS ---
    ret1y = metrics.get('1Y_total_return')
    if ret1y is not None:
        if ret1y > 0.30:
            insights.append("Strong 1-year momentum")
        elif ret1y < -0.20:
            insights.append("Weak 1-year performance")

    # --- SCALE ---
    mcap_b = metrics.get('Market Cap (B)')
    if mcap_b:
        if mcap_b > 200:
            insights.append("Mega-cap industry leader")
        elif mcap_b < 2:
            insights.append("Small-cap stock (Higher growth/risk potential)")

    return insights

def analyze_stock_data(df):
    """Combines all metrics for a given stock DataFrame."""
    metrics = {}
    
    if df is not None and not df.empty:
        # Returns
        ret_metrics = calculate_returns(df)
        if ret_metrics:
            metrics.update(ret_metrics)
            
        # Volatility
        metrics['volatility'] = calculate_volatility(df)
        
        # Max Drawdown
        metrics['max_drawdown'] = calculate_max_drawdown(df)
            
        # Moving Averages
        ma_metrics = get_moving_averages(df)
        if ma_metrics:
            metrics.update(ma_metrics)
            
        # Insights (Phase 3)
        current_price = df['Close'].iloc[-1]
        metrics['insights'] = generate_insights(metrics, current_price)
            
    return metrics

