# agent_logic.py
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
import tools

# Alpaca setup
from alpaca.trading.client import TradingClient

try:
    api_key = os.environ.get('APCA_API_KEY_ID')
    secret_key = os.environ.get('APCA_API_SECRET_KEY')
    if api_key and secret_key:
        tools.trading_client = TradingClient(api_key, secret_key, paper=True)
        print("✅ Alpaca client initialized")
    else:
        print("❌ Alpaca keys missing")
except Exception as e:
    print(f"❌ Alpaca init error: {e}")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.8)  # Higher temp for more creativity

# Single agent toolset
trading_tools = [
    tools.get_current_price,
    tools.get_financial_news,
    tools.get_asset_holdings,
    tools.place_market_order,
]

def run_paper_trading_agent_cycle(ticker: str) -> str:
    """Runs one trading cycle for a single stock - AGGRESSIVE VERSION"""
    
    print(f"🔍 Analyzing {ticker}...")
    
    # VERY AGGRESSIVE PROMPT - Forces action
    prompt = f"""
    You are an AGGRESSIVE trading bot that MUST take action. You are trading {ticker}.
    
    Follow this EXACT process:
    1. Get current price of {ticker}
    2. Get recent news about {ticker}
    3. Check if we hold {ticker}
    4. MAKE A FIRM DECISION: BUY, SELL, or HOLD
    5. EXECUTE the decision immediately if appropriate
    
    **TRADING RULES - BE DECISIVE:**
    - If there's ANY positive news → BUY 1 share (unless we already hold it)
    - If there's ANY negative news → SELL 1 share (if we hold it)  
    - If news is mixed/neutral → BUY 1 share (momentum play)
    - Only HOLD if there's absolutely NO news available
    
    **CRITICAL: YOU MUST USE place_market_order TOOL WHEN DECIDING TO BUY OR SELL**
    Don't just analyze - TAKE ACTION. Execute trades!
    
    Remember: This is PAPER TRADING - no real money at risk.
    Be bold and make trading decisions.
    
    After executing (or deciding not to), provide a brief summary.
    """
    
    try:
        agent_executor = create_react_agent(llm, trading_tools)
        result = agent_executor.invoke({"messages": [("user", prompt)]})
        final_output = result['messages'][-1].content
        print(f"🤖 Agent decision: {final_output[:200]}...")
        return final_output
        
    except Exception as e:
        error_msg = f"❌ Trading cycle failed: {str(e)}"
        print(error_msg)
        return error_msg

def get_current_portfolio_summary() -> dict:
    """Gets portfolio summary for the UI."""
    return tools.get_portfolio_summary()