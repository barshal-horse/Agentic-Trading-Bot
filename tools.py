# tools.py
import os
import yfinance as yf
from langchain.tools import tool
from newsapi import NewsApiClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# Alpaca imports
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

# Global clients
trading_client = None
market_data_client = None

@tool
def get_stock_info(ticker: str) -> dict:
    """Gets key financial information for a given stock ticker."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "ticker": ticker,
            "company_name": info.get("longName", "N/A"),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "market_cap": info.get("marketCap", 0),
            "pe_ratio": info.get("trailingPE", 0),
            "volume": info.get("volume", 0),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh", 0),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow", 0),
        }
    except Exception as e:
        return {"error": f"Failed to get stock info: {str(e)}"}

@tool
def get_financial_news(company_name: str) -> str:
    """Fetches and summarizes the latest financial news for a company."""
    try:
        newsapi = NewsApiClient(api_key=os.environ.get('NEWS_API_KEY', ''))
        all_articles = newsapi.get_everything(
            q=company_name, 
            language='en', 
            sort_by='publishedAt', 
            page_size=5
        )
        
        if not all_articles or not all_articles.get('articles'):
            return f"No recent news found for {company_name}."

        articles_text = "\n\n".join([
            f"Title: {a['title']}\nContent: {a.get('description','')}" 
            for a in all_articles['articles']
        ])

        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
        prompt = PromptTemplate(
            template="""Summarize these news articles about {company_name} and provide:
            1. Overall sentiment (Positive/Neutral/Negative)
            2. Key themes or topics
            3. Potential market impact
            
            Articles:
            {articles}
            
            Keep the summary concise and focused on trading implications.""",
            input_variables=["company_name", "articles"]
        )
        
        chain = prompt | llm
        summary = chain.invoke({"company_name": company_name, "articles": articles_text})
        return summary.content
        
    except Exception as e:
        return f"Error getting news: {str(e)}"

@tool
def get_current_price(ticker: str) -> float:
    """Gets the current real-time price of a stock."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        return float(hist['Close'].iloc[-1])
    except Exception as e:
        return f"Error getting price: {str(e)}"

@tool
def place_market_order(ticker: str, qty: int, side: str) -> str:
    """Places a market order (buy or sell) via the Alpaca API."""
    if not trading_client:
        return "Alpaca Trading client not initialized."
    
    if side.lower() not in ['buy', 'sell']:
        return "Invalid side. Must be 'buy' or 'sell'."
    
    try:
        market_order_data = MarketOrderRequest(
            symbol=ticker,
            qty=qty,
            side=OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL,
            time_in_force=TimeInForce.DAY
        )
        
        order = trading_client.submit_order(market_order_data)
        return f"✅ {side.upper()} order executed: {qty} shares of {ticker}. Order ID: {order.id}"
        
    except Exception as e:
        return f"❌ Order failed: {str(e)}"

@tool
def get_asset_holdings(ticker: str) -> str:
    """Checks the Alpaca account for current holdings of a specific stock."""
    if not trading_client:
        return "Alpaca Trading client not initialized."
    
    try:
        positions = trading_client.get_all_positions()
        for position in positions:
            if position.symbol == ticker:
                return f"Holdings: {position.qty} shares (Market Value: ${position.market_value})"
        return "No current holdings."
    except Exception as e:
        return f"Error checking holdings: {str(e)}"

# REMOVE the @tool decorator from this function so it can be called directly
def get_portfolio_summary() -> dict:
    """Gets complete portfolio summary from Alpaca."""
    if not trading_client:
        return {"error": "Alpaca Trading client not initialized."}
    
    try:
        account = trading_client.get_account()
        positions = trading_client.get_all_positions()
        
        return {
            "cash": float(account.cash),
            "portfolio_value": float(account.portfolio_value),
            "equity": float(account.equity),
            "buying_power": float(account.buying_power),
            "positions": [
                {
                    "symbol": p.symbol,
                    "qty": float(p.qty),
                    "market_value": float(p.market_value),
                    "current_price": float(p.current_price)
                } for p in positions
            ]
        }
    except Exception as e:
        return {"error": f"Portfolio summary error: {str(e)}"}