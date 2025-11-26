# hft_scalper.py
import os
import time
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

import tools
from momentum_scanner import get_dynamic_watchlist
from analytics_logger import log_trade_execution, log_decision_analytics

# Alpaca setup
from alpaca.trading.client import TradingClient

try:
    api_key = os.environ.get('APCA_API_KEY_ID')
    secret_key = os.environ.get('APCA_API_SECRET_KEY')
    if api_key and secret_key:
        tools.trading_client = TradingClient(api_key, secret_key, paper=True)
        print("✅ Alpaca client initialized for HFT trading")
    else:
        print("❌ Alpaca keys missing")
except Exception as e:
    print(f"❌ Alpaca init error: {e}")

# HFT Trading Parameters
HFT_PARAMS = {
    "position_size_pct": 10,           # 10% of portfolio per trade
    "max_positions": 6,                # 6 concurrent positions (60% portfolio)
    "profit_target_pct": 0.4,          # 0.4% profit target
    "stop_loss_pct": 0.3,              # 0.3% stop loss
    "max_hold_minutes": 2,             # Force exit after 2 minutes
    "max_daily_trades": 30,            # High frequency
}

# Track active positions
active_positions = {}
daily_trades = {
    "date": datetime.now().date(),
    "trades_count": 0,
    "last_trade_time": None
}

def reset_daily_trades():
    """Reset daily trade counter if new day"""
    today = datetime.now().date()
    if daily_trades["date"] != today:
        daily_trades["date"] = today
        daily_trades["trades_count"] = 0
        daily_trades["last_trade_time"] = None
        active_positions.clear()

def calculate_position_size():
    """Calculate 10% position size"""
    portfolio = tools.get_portfolio_summary()
    if "error" in portfolio:
        return 1000  # Fallback
    
    portfolio_value = portfolio["portfolio_value"]
    position_size = portfolio_value * (HFT_PARAMS["position_size_pct"] / 100)
    return max(100, position_size)  # Minimum $100

def get_price_movement(ticker):
    """Get recent price movement for scalping signals"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d", interval="2m")
        
        if len(hist) < 5:
            return None
            
        current_price = hist['Close'].iloc[-1]
        prev_price = hist['Close'].iloc[-2]
        change_pct = ((current_price - prev_price) / prev_price) * 100
        
        # Volume analysis
        current_volume = hist['Volume'].iloc[-1]
        avg_volume = hist['Volume'].tail(5).mean()
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        return {
            'ticker': ticker,
            'price': current_price,
            'change_pct': change_pct,
            'volume_ratio': volume_ratio,
            'trend': 'up' if change_pct > 0 else 'down'
        }
    except Exception as e:
        print(f"❌ Price analysis failed for {ticker}: {e}")
        return None

def should_buy_stock(ticker):
    """HFT Buy Signal: Buy on small dips or momentum"""
    price_data = get_price_movement(ticker)
    if not price_data:
        return False
    
    # Buy signals for HFT
    buy_signals = [
        price_data['change_pct'] < -0.1,  # Small dip
        price_data['volume_ratio'] > 1.3,  # High volume
        price_data['change_pct'] > 0.05 and price_data['volume_ratio'] > 1.2  # Momentum
    ]
    
    return any(buy_signals)

def manage_active_positions():
    """Check all active positions for exit signals"""
    exits = []
    
    for ticker, position in list(active_positions.items()):
        try:
            current_data = get_price_movement(ticker)
            if not current_data:
                continue
                
            current_price = current_data['price']
            entry_price = position['entry_price']
            entry_time = position['entry_time']
            
            # Calculate P/L
            profit_pct = ((current_price - entry_price) / entry_price) * 100
            hold_time = (datetime.now() - entry_time).total_seconds() / 60  # minutes
            
            # Exit signals
            exit_reason = None
            if profit_pct >= HFT_PARAMS["profit_target_pct"]:
                exit_reason = f"Profit target: +{profit_pct:.2f}%"
            elif profit_pct <= -HFT_PARAMS["stop_loss_pct"]:
                exit_reason = f"Stop loss: {profit_pct:.2f}%"
            elif hold_time >= HFT_PARAMS["max_hold_minutes"]:
                exit_reason = f"Time limit: {hold_time:.1f}min"
            
            if exit_reason:
                exits.append({
                    'ticker': ticker,
                    'entry_price': entry_price,
                    'current_price': current_price,
                    'profit_pct': profit_pct,
                    'reason': exit_reason,
                    'shares': position['shares']
                })
                
        except Exception as e:
            print(f"❌ Error managing position {ticker}: {e}")
    
    return exits

def execute_hft_trade(ticker, action, shares, price, reason=""):
    """Execute HFT trade with aggressive sizing"""
    try:
        if action == "BUY":
            result = tools.place_market_order.func(ticker, shares, "buy")
            
            # Track active position
            active_positions[ticker] = {
                'entry_price': price,
                'shares': shares,
                'entry_time': datetime.now(),
                'reason': reason
            }
            
        elif action == "SELL":
            result = tools.place_market_order.func(ticker, shares, "sell")
            
            # Remove from active positions
            if ticker in active_positions:
                del active_positions[ticker]
        
        daily_trades["trades_count"] += 1
        daily_trades["last_trade_time"] = datetime.now()
        
        log_trade_execution(ticker, action, shares, price, result)
        return {"executed": True, "result": result}
        
    except Exception as e:
        return {"executed": False, "error": str(e)}

def run_hft_scalping_cycle():
    """Run one HFT scalping cycle"""
    print(f"🚀 STARTING HFT SCALPING CYCLE")
    print(f"🎯 Strategy: {HFT_PARAMS['position_size_pct']}% positions, {HFT_PARAMS['profit_target_pct']}% targets")
    
    reset_daily_trades()
    
    # Get dynamic watchlist
    watchlist = get_dynamic_watchlist()
    if not watchlist:
        print("❌ No stocks found for trading")
        return {"error": "No stocks available"}
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "trades_executed": 0,
        "buy_trades": 0,
        "sell_trades": 0,
        "total_pnl": 0,
        "cycle_results": []
    }
    
    # PHASE 1: Manage existing positions (SELL)
    print(f"\n🔍 PHASE 1: Managing {len(active_positions)} active positions...")
    exits = manage_active_positions()
    
    for exit_trade in exits:
        print(f"💰 EXIT SIGNAL: {exit_trade['ticker']} - {exit_trade['reason']}")
        
        execution = execute_hft_trade(
            exit_trade['ticker'], 
            "SELL", 
            exit_trade['shares'],
            exit_trade['current_price'],
            f"HFT Exit: {exit_trade['reason']}"
        )
        
        if execution["executed"]:
            results["trades_executed"] += 1
            results["sell_trades"] += 1
            results["total_pnl"] += exit_trade['profit_pct']
            print(f"✅ SELL EXECUTED: {exit_trade['ticker']} ({exit_trade['profit_pct']:.2f}%)")
    
    # PHASE 2: Find new entries (BUY)
    available_slots = HFT_PARAMS["max_positions"] - len(active_positions)
    if available_slots > 0:
        print(f"\n🔍 PHASE 2: Scanning for {available_slots} new entries...")
        
        position_size = calculate_position_size()
        
        for ticker in watchlist:
            if available_slots <= 0:
                break
                
            if ticker in active_positions:
                continue  # Already holding
                
            if should_buy_stock(ticker):
                price_data = get_price_movement(ticker)
                if not price_data:
                    continue
                    
                # Calculate shares for 10% position
                shares = max(1, int(position_size / price_data['price']))
                
                print(f"🎯 BUY SIGNAL: {ticker} @ ${price_data['price']:.2f} ({price_data['change_pct']:.2f}%)")
                
                execution = execute_hft_trade(
                    ticker, "BUY", shares, price_data['price'],
                    f"HFT Entry: {price_data['change_pct']:.2f}% move"
                )
                
                if execution["executed"]:
                    results["trades_executed"] += 1
                    results["buy_trades"] += 1
                    available_slots -= 1
                    print(f"✅ BUY EXECUTED: {ticker} - {shares} shares (${shares * price_data['price']:.2f})")
                
                time.sleep(0.5)  # Small delay between entries
    
    # Results summary
    portfolio = tools.get_portfolio_summary()
    current_value = portfolio["portfolio_value"] if "error" not in portfolio else 0
    
    print(f"\n=== HFT CYCLE COMPLETE ===")
    print(f"📊 Trades Executed: {results['trades_executed']}")
    print(f"🛒 BUY Orders: {results['buy_trades']}")
    print(f"💰 SELL Orders: {results['sell_trades']}")
    print(f"📈 Active Positions: {len(active_positions)}")
    print(f"💵 Portfolio: ${current_value:,.2f}")
    print(f"🎯 P&L Impact: {results['total_pnl']:.2f}%")
    
    return results

def get_hft_stats():
    """Get HFT trading statistics"""
    if not tools.trading_client:
        return {"error": "Trading client not available"}
    
    try:
        portfolio = tools.get_portfolio_summary()
        if "error" in portfolio:
            return portfolio
        
        return {
            "portfolio_value": portfolio["portfolio_value"],
            "cash": portfolio["cash"],
            "buying_power": portfolio["buying_power"],
            "active_positions": len(active_positions),
            "max_positions": HFT_PARAMS["max_positions"],
            "daily_trades": daily_trades["trades_count"],
            "last_trade_time": daily_trades["last_trade_time"],
            "position_size_pct": HFT_PARAMS["position_size_pct"],
            "strategy": "HFT_SCALPING"
        }
    except Exception as e:
        return {"error": str(e)}