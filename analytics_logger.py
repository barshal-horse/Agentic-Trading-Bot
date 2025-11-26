# analytics_logger.py
import json
import os
from datetime import datetime
import pandas as pd

def log_trade_execution(ticker: str, action: str, shares: int, price: float, result: str):
    """Log detailed trade execution for analytics."""
    
    trade_data = {
        'timestamp': datetime.now().isoformat(),
        'ticker': ticker,
        'action': action,
        'shares': shares,
        'price': price,
        'result': result,
        'investment': shares * price,
        'pnl': calculate_trade_pnl(ticker, action, shares, price)
    }
    
    # Ensure directory exists
    os.makedirs('trading_logs', exist_ok=True)
    
    # Load existing trades
    trades_file = 'trading_logs/trades.json'
    if os.path.exists(trades_file):
        with open(trades_file, 'r') as f:
            trades = json.load(f)
    else:
        trades = []
    
    # Add new trade
    trades.append(trade_data)
    
    # Keep only last 1000 trades
    if len(trades) > 1000:
        trades = trades[-1000:]
    
    # Save updated trades
    with open(trades_file, 'w') as f:
        json.dump(trades, f, indent=2)

def calculate_trade_pnl(ticker: str, action: str, shares: int, price: float) -> float:
    """Calculate P&L for a trade (simplified version)."""
    # Note: In a real system, you'd track entry prices and calculate actual P&L
    # This is a simplified version for demonstration
    
    if action.upper() == 'BUY':
        return -shares * price  # Negative for buys (cost)
    elif action.upper() == 'SELL':
        return shares * price   # Positive for sells (revenue)
    else:
        return 0.0

def log_decision_analytics(decision_data: dict):
    """Enhanced decision logging for analytics."""
    
    # Ensure directory exists
    os.makedirs('trading_logs', exist_ok=True)
    
    # Load existing decisions
    decisions_file = 'trading_logs/decisions.json'
    if os.path.exists(decisions_file):
        with open(decisions_file, 'r') as f:
            decisions = json.load(f)
    else:
        decisions = []
    
    # Add new decision
    decisions.append(decision_data)
    
    # Keep only last 2000 decisions
    if len(decisions) > 2000:
        decisions = decisions[-2000:]
    
    # Save updated decisions
    with open(decisions_file, 'w') as f:
        json.dump(decisions, f, indent=2)

def get_analytics_data() -> dict:
    """Load analytics data from logs."""
    data = {
        'trades': [],
        'decisions': []
    }
    
    try:
        if os.path.exists('trading_logs/trades.json'):
            with open('trading_logs/trades.json', 'r') as f:
                data['trades'] = json.load(f)
    except Exception as e:
        print(f"Error loading trades: {e}")
    
    try:
        if os.path.exists('trading_logs/decisions.json'):
            with open('trading_logs/decisions.json', 'r') as f:
                data['decisions'] = json.load(f)
    except Exception as e:
        print(f"Error loading decisions: {e}")
    
    return data