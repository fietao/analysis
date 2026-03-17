import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def normalize_metrics(metrics: dict) -> dict:
    """
    Normalizes backend Column names to frontend-friendly names.
    Maps internal column names to user-facing format for consistency across API/UI.
    
    Examples:
        1Y_total_return -> 1Y Return
        volatility -> Volatility  
        max_drawdown -> Max Drawdown
    """
    normalized = dict(metrics)
    
    # Return mappings
    if "1Y_total_return" in normalized:
        normalized["1Y Return"] = normalized.pop("1Y_total_return")
    if "3Y_total_return" in normalized:
        normalized["3Y Return"] = normalized.pop("3Y_total_return")
    if "5Y_total_return" in normalized:
        normalized["5Y Return"] = normalized.pop("5Y_total_return")
        
    if "1Y_annualized_return" in normalized:
        normalized["1Y Annualized Return"] = normalized.pop("1Y_annualized_return")
    if "3Y_annualized_return" in normalized:
        normalized["3Y Annualized Return"] = normalized.pop("3Y_annualized_return")
    if "5Y_annualized_return" in normalized:
        normalized["5Y Annualized Return"] = normalized.pop("5Y_annualized_return")
        
    # Risk metrics
    if "volatility" in normalized:
        normalized["Volatility"] = normalized.pop("volatility")
    if "max_drawdown" in normalized:
        normalized["Max Drawdown"] = normalized.pop("max_drawdown")
        
    # Dividend and profitability
    if "dividend_yield" in normalized:
        normalized["Dividend Yield"] = normalized.pop("dividend_yield")
    if "profit_margins" in normalized:
        normalized["Profit Margin"] = normalized.pop("profit_margins")
    if "revenue_growth" in normalized:
        normalized["Revenue Growth"] = normalized.pop("revenue_growth")
        
    return normalized

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
    Returns None if insufficient data (< 5 data points) or if std dev is 0.
    """
    if df is None or len(df) < 5:
        return None
    
    # Calculate daily percentage change
    daily_returns = df['Close'].pct_change().dropna()
    
    if len(daily_returns) < 2:
        return None
    
    # Standard deviation of daily returns * sqrt(252)
    daily_vol = daily_returns.std()
    
    # Handle zero volatility edge case
    if daily_vol == 0 or pd.isna(daily_vol):
        return 0.0
    
    annualized_vol = daily_vol * np.sqrt(252)
    return float(annualized_vol)

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
    """
    Calculates 50 and 200 day moving averages.
    Returns None if insufficient data for that MA, not NaN.
    """
    if df is None or len(df) < 5:
        return {'MA50': None, 'MA200': None}
    
    df = df.copy()
    
    # Calculate MAs if we have enough data
    if len(df) >= 50:
        df['MA50'] = df['Close'].rolling(window=50).mean()
        ma50 = df['MA50'].iloc[-1]
        ma50 = None if pd.isna(ma50) else float(ma50)
    else:
        ma50 = None
    
    if len(df) >= 200:
        df['MA200'] = df['Close'].rolling(window=200).mean()
        ma200 = df['MA200'].iloc[-1]
        ma200 = None if pd.isna(ma200) else float(ma200)
    else:
        ma200 = None
    
    return {
        'MA50': ma50,
        'MA200': ma200
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
            
        # Insights (Phase 3) - use raw metrics before normalization
        current_price = df['Close'].iloc[-1]
        metrics['insights'] = generate_insights(metrics, current_price)
    
    # Normalize column names for consistent API/UI display
    metrics = normalize_metrics(metrics)
    return metrics

