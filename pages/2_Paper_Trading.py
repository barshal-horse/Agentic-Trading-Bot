# pages/2_Paper_Trading.py
import streamlit as st
from agent_logic import run_paper_trading_agent_cycle, get_current_portfolio_summary
import pandas as pd

st.set_page_config(layout="wide")

st.title("🤖 Paper Trading Bot")
st.markdown("Manual single-stock trading with AI-powered analysis")
st.warning("⚠️ **Disclaimer:** Paper trading with fake money for educational purposes ONLY.", icon="⚖️")
st.markdown("---")

# Initialize session state
if 'trading_logs' not in st.session_state:
    st.session_state.trading_logs = []
if 'trading_ticker' not in st.session_state:
    st.session_state.trading_ticker = "AAPL"

# Controls
st.session_state.trading_ticker = st.text_input("Stock Ticker:", value=st.session_state.trading_ticker).upper()

if st.button("▶️ Run One Trading Cycle", use_container_width=True):
    with st.spinner(f"Agent is analyzing {st.session_state.trading_ticker}..."):
        log_output = run_paper_trading_agent_cycle(st.session_state.trading_ticker)
        st.session_state.trading_logs.insert(0, log_output)
        st.rerun()

st.markdown("---")

# Portfolio Display
st.subheader("💰 Portfolio Summary")
portfolio_data = get_current_portfolio_summary()
if "error" in portfolio_data:
    st.error(portfolio_data["error"])
else:
    col1, col2, col3 = st.columns(3)
    col1.metric("Cash", f"${portfolio_data['cash']:,.2f}")
    col2.metric("Equity", f"${portfolio_data['equity']:,.2f}")
    col3.metric("Buying Power", f"${portfolio_data['buying_power']:,.2f}")
    
    st.write("**Current Holdings:**")
    if portfolio_data["positions"]:
        df = pd.DataFrame(portfolio_data["positions"])
        st.dataframe(df.set_index('symbol'), use_container_width=True)
    else:
        st.info("No current holdings.")

# Trading Logs
st.markdown("---")
st.subheader("📋 Trading Logs")

if st.button("Clear Logs", use_container_width=True):
    st.session_state.trading_logs = []
    st.rerun()

for i, log in enumerate(st.session_state.trading_logs):
    with st.expander(f"Trading Cycle {i+1} - {st.session_state.trading_ticker}", expanded=i==0):
        st.code(log)

if not st.session_state.trading_logs:
    st.info("No trading cycles run yet. Click 'Run One Trading Cycle' to start.")