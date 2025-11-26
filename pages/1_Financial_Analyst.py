# pages/1_Financial_Analyst.py
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

st.set_page_config(page_title="Financial Analyst", layout="wide")

st.title("📈 Financial Analyst")
st.markdown("Quick stock analysis with essential metrics and technical indicators")

# Initialize session state
if 'analysis_ticker' not in st.session_state:
    st.session_state.analysis_ticker = "AAPL"
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = None

# Simple controls
col1, col2 = st.columns([2, 1])
with col1:
    st.session_state.analysis_ticker = st.text_input(
        "Stock Ticker:", 
        value=st.session_state.analysis_ticker
    ).upper()

with col2:
    period = st.selectbox("Period:", ["1mo", "3mo", "6mo", "1y"], index=1)

# Main analysis function
def quick_analysis(ticker, period):
    """Quick but comprehensive stock analysis"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        
        if hist.empty:
            return None, "No data found"
        
        # Calculate basic indicators
        hist['SMA_20'] = hist['Close'].rolling(20).mean()
        hist['SMA_50'] = hist['Close'].rolling(50).mean()
        hist['RSI'] = calculate_rsi(hist['Close'])
        
        # Get key info
        info = stock.info
        current_price = hist['Close'].iloc[-1]
        prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
        change = current_price - prev_price
        change_pct = (change / prev_price) * 100
        
        return {
            'ticker': ticker,
            'current_price': current_price,
            'change': change,
            'change_pct': change_pct,
            'historical': hist,
            'company_name': info.get('longName', ticker),
            'market_cap': info.get('marketCap', 'N/A'),
            'pe_ratio': info.get('trailingPE', 'N/A'),
            'volume': hist['Volume'].iloc[-1],
            'rsi': hist['RSI'].iloc[-1]
        }, None
        
    except Exception as e:
        return None, f"Error: {str(e)}"

def calculate_rsi(prices, window=14):
    """Calculate RSI indicator"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Run analysis
if st.button("🔍 Analyze Stock", type="primary", use_container_width=True):
    with st.spinner(f"Analyzing {st.session_state.analysis_ticker}..."):
        data, error = quick_analysis(st.session_state.analysis_ticker, period)
        if error:
            st.error(error)
        else:
            st.session_state.analysis_data = data
            st.success("Analysis complete!")

# Display results
if st.session_state.analysis_data:
    data = st.session_state.analysis_data
    
    # Key metrics
    st.subheader("📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        delta_color = "normal" if data['change'] >= 0 else "inverse"
        st.metric(
            "Current Price", 
            f"${data['current_price']:.2f}",
            f"{data['change_pct']:+.2f}%",
            delta_color=delta_color
        )
    
    with col2:
        st.metric("RSI", f"{data['rsi']:.1f}")
    
    with col3:
        market_cap = data['market_cap']
        if isinstance(market_cap, (int, float)):
            st.metric("Market Cap", f"${market_cap/1e9:.1f}B")
        else:
            st.metric("Market Cap", "N/A")
    
    with col4:
        pe = data['pe_ratio']
        st.metric("P/E Ratio", f"{pe:.1f}" if isinstance(pe, (int, float)) else "N/A")

    # Price chart
    st.subheader("📈 Price Chart")
    fig = go.Figure()
    
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=data['historical'].index,
        open=data['historical']['Open'],
        high=data['historical']['High'],
        low=data['historical']['Low'],
        close=data['historical']['Close'],
        name='Price'
    ))
    
    # Moving averages
    fig.add_trace(go.Scatter(
        x=data['historical'].index,
        y=data['historical']['SMA_20'],
        line=dict(color='orange', width=1),
        name='SMA 20'
    ))
    
    fig.add_trace(go.Scatter(
        x=data['historical'].index,
        y=data['historical']['SMA_50'],
        line=dict(color='blue', width=1),
        name='SMA 50'
    ))
    
    fig.update_layout(
        height=400,
        xaxis_rangeslider_visible=False,
        title=f"{data['ticker']} Price Chart"
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # Technical signals
    st.subheader("🎯 Technical Signals")
    
    col5, col6 = st.columns(2)
    
    with col5:
        # RSI analysis
        rsi = data['rsi']
        if rsi > 70:
            st.error("RSI: Overbought (>70)")
        elif rsi < 30:
            st.success("RSI: Oversold (<30)")
        else:
            st.info(f"RSI: Neutral ({rsi:.1f})")
        
        # Moving average analysis
        current_price = data['current_price']
        sma_20 = data['historical']['SMA_20'].iloc[-1]
        if current_price > sma_20:
            st.success("Price above 20-day MA")
        else:
            st.warning("Price below 20-day MA")
    
    with col6:
        # Volume analysis
        avg_volume = data['historical']['Volume'].tail(20).mean()
        current_volume = data['volume']
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        if volume_ratio > 1.5:
            st.info(f"Volume: High ({volume_ratio:.1f}x avg)")
        else:
            st.info(f"Volume: Normal ({volume_ratio:.1f}x avg)")
        
        # Trend analysis
        price_trend = "Up" if data['change'] > 0 else "Down"
        st.metric("Daily Trend", price_trend)

    # Quick insights
    st.subheader("💡 Quick Insights")
    
    insights = []
    rsi = data['rsi']
    price_vs_ma = data['current_price'] > data['historical']['SMA_20'].iloc[-1]
    
    if rsi < 30 and price_vs_ma:
        insights.append("Oversold but above 20-day MA - potential buying opportunity")
    elif rsi > 70 and not price_vs_ma:
        insights.append("Overbought and below 20-day MA - caution advised")
    elif data['change_pct'] > 3:
        insights.append("Strong upward momentum today")
    elif data['change_pct'] < -3:
        insights.append("Significant downward pressure")
    else:
        insights.append("Neutral market conditions - monitor for breakout")
    
    for insight in insights:
        st.write(f"• {insight}")

else:
    # Welcome state
    st.info("👆 Enter a stock ticker and click 'Analyze Stock' to get started")
    
    # Sample preview
    st.subheader("Example Analysis Includes:")
    
    col7, col8 = st.columns(2)
    
    with col7:
        st.write("**Technical Analysis**")
        st.write("• Real-time price charts")
        st.write("• RSI indicators")
        st.write("• Moving averages")
        st.write("• Volume analysis")
    
    with col8:
        st.write("**Investment Insights**")
        st.write("• Overbought/oversold signals")
        st.write("• Trend analysis")
        st.write("• Quick recommendations")
        st.write("• Risk assessment")

# Footer
st.markdown("---")
st.caption("Data provided by Yahoo Finance • Analysis for educational purposes only")