# momentum_scanner.py
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import os
from newsapi import NewsApiClient

def get_active_stocks(count=15):
    """Get actively trading stocks with momentum and news"""
    print("🔍 Scanning for active momentum stocks...")
    
    # Pre-defined universe of liquid, popular stocks
    stock_universe = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "AMD",
        "NFLX", "ADBE", "CRM", "INTC", "QCOM", "AVGO", "TXN", "MU",
        "SPY", "QQQ", "IWM", "DIA", "V", "MA", "JPM", "BAC",
        "WMT", "TGT", "COST", "HD", "LOW", "NKE", "MCD", "SBUX",
        "XOM", "CVX", "COP", "SLB", "BA", "CAT", "DE", "UNH",
        "JNJ", "PFE", "MRK", "ABT", "LLY", "TMO", "DHR"
    ]
    
    active_stocks = []
    
    for ticker in stock_universe[:25]:  # Check first 25 for speed
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d", interval="5m")
            
            if len(hist) < 2:
                continue
                
            # Calculate momentum indicators
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2]
            price_change_pct = ((current_price - prev_price) / prev_price) * 100
            
            volume = hist['Volume'].iloc[-1]
            avg_volume = hist['Volume'].mean()
            volume_ratio = volume / avg_volume if avg_volume > 0 else 1
            
            # Momentum criteria
            is_active = (
                abs(price_change_pct) > 0.1 or  # Price moving
                volume_ratio > 1.2 or           # High volume
                current_price > hist['Close'].mean()  # Above average
            )
            
            if is_active:
                active_stocks.append({
                    'ticker': ticker,
                    'price': current_price,
                    'change_pct': price_change_pct,
                    'volume_ratio': volume_ratio,
                    'momentum_score': abs(price_change_pct) + volume_ratio
                })
                
        except Exception as e:
            continue
    
    # Sort by momentum and return top stocks
    active_stocks.sort(key=lambda x: x['momentum_score'], reverse=True)
    selected = [stock['ticker'] for stock in active_stocks[:count]]
    
    print(f"🎯 Selected {len(selected)} active stocks: {selected}")
    return selected

def get_high_volume_stocks(count=12):
    """Get stocks with unusually high volume"""
    print("🔍 Scanning for high-volume stocks...")
    
    volume_stocks = [
        "AAPL", "TSLA", "NVDA", "AMD", "META", "AMZN", 
        "MSFT", "GOOGL", "SPY", "QQQ", "NFLX", "MRNA"
    ]
    
    high_volume = []
    
    for ticker in volume_stocks:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d", interval="5m")
            
            if len(hist) < 10:
                continue
                
            current_volume = hist['Volume'].iloc[-1]
            avg_volume = hist['Volume'].tail(10).mean()
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            if volume_ratio > 1.5:  # 50% above average volume
                high_volume.append({
                    'ticker': ticker,
                    'volume_ratio': volume_ratio,
                    'price': hist['Close'].iloc[-1]
                })
                
        except Exception:
            continue
    
    high_volume.sort(key=lambda x: x['volume_ratio'], reverse=True)
    selected = [stock['ticker'] for stock in high_volume[:count]]
    
    print(f"📊 Found {len(selected)} high-volume stocks: {selected}")
    return selected

def get_stocks_in_news(count=10):
    """Get stocks currently in news"""
    print("📰 Scanning for stocks in news...")
    
    try:
        newsapi = NewsApiClient(api_key=os.environ.get('NEWS_API_KEY', ''))
        
        # Common stock keywords
        stock_keywords = ["Apple", "Tesla", "Nvidia", "Microsoft", "Amazon", "Google", 
                         "Meta", "Netflix", "AMD", "Intel", "Qualcomm", "Salesforce"]
        
        news_stocks = set()
        
        for keyword in stock_keywords:
            try:
                articles = newsapi.get_everything(
                    q=keyword,
                    language='en',
                    sort_by='publishedAt',
                    page_size=3
                )
                
                if articles and articles.get('articles'):
                    # Map company names to tickers
                    company_to_ticker = {
                        "Apple": "AAPL", "Tesla": "TSLA", "Nvidia": "NVDA",
                        "Microsoft": "MSFT", "Amazon": "AMZN", "Google": "GOOGL",
                        "Meta": "META", "Netflix": "NFLX", "AMD": "AMD",
                        "Intel": "INTC", "Qualcomm": "QCOM", "Salesforce": "CRM"
                    }
                    
                    if keyword in company_to_ticker:
                        news_stocks.add(company_to_ticker[keyword])
                        
            except Exception:
                continue
        
        selected = list(news_stocks)[:count]
        print(f"📰 Found {len(selected)} stocks in news: {selected}")
        return selected
        
    except Exception as e:
        print(f"❌ News scan failed: {e}")
        return []

def get_dynamic_watchlist():
    """Combine all methods to get best trading candidates"""
    print("🔄 Generating dynamic watchlist...")
    
    # Get stocks from multiple sources
    momentum_stocks = get_active_stocks(8)
    volume_stocks = get_high_volume_stocks(6)
    news_stocks = get_stocks_in_news(6)
    
    # Combine and deduplicate
    all_stocks = list(set(momentum_stocks + volume_stocks + news_stocks))
    
    # Ensure we have enough stocks
    if len(all_stocks) < 8:
        # Add some default liquid stocks
        default_stocks = ["AAPL", "MSFT", "TSLA", "NVDA", "AMZN", "META", "GOOGL", "SPY"]
        for stock in default_stocks:
            if stock not in all_stocks and len(all_stocks) < 12:
                all_stocks.append(stock)
    
    print(f"🎯 Final dynamic watchlist ({len(all_stocks)} stocks): {all_stocks}")
    return all_stocks