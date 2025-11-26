# trading_config.py

# Balanced watchlist with different sectors
DEFAULT_WATCHLIST = [
    "AAPL",    # Technology
    "MSFT",    # Technology  
    "JNJ",     # Healthcare (defensive)
    "JPM",     # Financials
    "XOM",     # Energy (cyclical)
    "WMT",     # Consumer Staples (defensive)
    "TSLA",    # Discretionary (volatile)
    "NVDA",    # Technology (volatile)
]

# More realistic parameters for active trading
TRADING_PARAMS = {
    "max_positions": 20,           # Increased to allow more diversification
    "position_size_pct": 2.0,     # Smaller position size for more positions
    "trade_frequency_mins": 3,    # More frequent trading
    "max_daily_trades": 30,       # Higher daily limit
    "min_confidence": "MEDIUM",   # Require medium confidence
}

# Technical analysis parameters
TECHNICAL_PARAMS = {
    "rsi_oversold": 30,
    "rsi_overbought": 70,
    "sma_short": 20,
    "sma_long": 50,
}