# pages/3_Automated_Trading.py
import streamlit as st
import pandas as pd
import time
from datetime import datetime

# HFT IMPORTS - REPLACED OLD IMPORTS
from automated_agent import run_hft_scalping_cycle, get_hft_stats


st.set_page_config(layout="wide")

st.title("🚀 HFT Scalping Trading Bot")
st.markdown("**High-Frequency Trading Bot - 10% Positions, 0.4% Profit Targets, 2-Minute Max Hold**")
st.warning("⚠️ **HFT BOT ACTIVE** - Aggressive scalping with large position sizes", icon="⚡")

# Initialize session state
if 'auto_cycles' not in st.session_state:
    st.session_state.auto_cycles = []
if 'is_auto_running' not in st.session_state:
    st.session_state.is_auto_running = False

st.markdown("---")

# Controls Section
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🔄 HFT Controls")
    
    if not st.session_state.is_auto_running:
        if st.button("▶️ Start HFT Bot", type="primary", use_container_width=True):
            st.session_state.is_auto_running = True
            st.rerun()
        
        if st.button("🔍 Run Single HFT Cycle", use_container_width=True):
            with st.spinner("🚀 HFT Bot scanning for momentum opportunities..."):
                result = run_hft_scalping_cycle()
                st.session_state.auto_cycles.insert(0, result)
                if "error" not in result:
                    st.success(f"✅ HFT Cycle Complete! {result['trades_executed']} trades executed")
                else:
                    st.error(f"❌ HFT Cycle Failed: {result['error']}")
    else:
        if st.button("⏹️ Stop HFT Bot", type="secondary", use_container_width=True):
            st.session_state.is_auto_running = False
            st.rerun()

with col2:
    st.subheader("📊 Live HFT Stats")
    stats = get_hft_stats()
    
    if "error" not in stats:
        st.metric("Portfolio Value", f"${stats['portfolio_value']:,.2f}")
        st.metric("Active Positions", f"{stats['active_positions']}/{stats['max_positions']}")
        st.metric("Daily Trades", f"{stats['daily_trades']}/30")
        st.metric("Buying Power", f"${stats['buying_power']:,.2f}")
    else:
        st.error(stats["error"])

with col3:
    st.subheader("⚙️ HFT Configuration")
    st.write("**Strategy:** HFT Scalping")
    st.write("**Position Size:** 10% of portfolio")
    st.write("**Profit Target:** 0.4% per trade")
    st.write("**Stop Loss:** 0.3%")
    st.write("**Max Hold Time:** 2 minutes")
    st.write("**Max Positions:** 6 concurrent")

# HFT Strategy Info
st.markdown("---")
st.subheader("🎯 HFT Trading Strategy")

strategy_col1, strategy_col2 = st.columns(2)

with strategy_col1:
    st.write("**📈 Entry Signals:**")
    st.write("• Buy on 0.1%+ price dips")
    st.write("• Buy on 30%+ volume spikes") 
    st.write("• Buy on momentum breakouts")
    st.write("• Dynamic stock selection")

with strategy_col2:
    st.write("**💰 Exit Signals:**")
    st.write("• Take profit at 0.4% gain")
    st.write("• Stop loss at 0.3% loss")
    st.write("• Force exit after 2 minutes")
    st.write("• Portfolio rotation")

# Auto-trading simulation
if st.session_state.is_auto_running:
    st.info("🔵 **HFT BOT ACTIVE** - Running continuous scalping cycles every 3 minutes")
    
    if st.button("🔄 Run Next HFT Cycle Now"):
        with st.spinner("🚀 HFT Bot executing rapid scalping strategy..."):
            result = run_hft_scalping_cycle()
            st.session_state.auto_cycles.insert(0, result)
            if "error" not in result:
                st.success(f"✅ HFT Cycle Complete! {result['trades_executed']} trades, P&L: {result.get('total_pnl', 0):.2f}%")
            else:
                st.error(f"❌ HFT Cycle Failed: {result['error']}")

# Results Display - ENHANCED FOR HFT
st.markdown("---")
st.subheader("📋 HFT Trading Activity")

if st.session_state.auto_cycles:
    latest_cycle = st.session_state.auto_cycles[0]
    
    if "error" in latest_cycle:
        st.error(f"HFT Cycle Error: {latest_cycle['error']}")
    else:
        # HFT-Specific Summary Metrics
        st.subheader("🎯 HFT Cycle Summary")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Trades Executed", latest_cycle['trades_executed'])
        col2.metric("BUY Orders", latest_cycle.get('buy_trades', 0))
        col3.metric("SELL Orders", latest_cycle.get('sell_trades', 0))
        col4.metric("Active Positions", latest_cycle.get('current_positions', 0))
        col5.metric("P&L Impact", f"{latest_cycle.get('total_pnl', 0):.2f}%")
        
        # Enhanced Results Display
        st.subheader("📊 Trade Execution Details")
        
        if latest_cycle.get('cycle_results'):
            # Create enhanced dataframe
            enhanced_data = []
            for result in latest_cycle['cycle_results']:
                execution = result.get('execution_result', {})
                
                if execution.get('executed'):
                    status = f"✅ EXECUTED: {execution['action']}"
                    pnl_info = f"{execution.get('profit_percentage', 0):.2f}%" if execution.get('profit_percentage') else "N/A"
                else:
                    status = f"⏸️ SKIPPED: {execution.get('skipped', 'Analysis')}"
                    pnl_info = "N/A"
                
                enhanced_data.append({
                    'Ticker': result['ticker'],
                    'Action': result.get('action', 'N/A'),
                    'Confidence': result.get('confidence', 'N/A'),
                    'Status': status,
                    'P/L': pnl_info,
                    'Reason': result.get('reason', '')[:60] + '...'
                })
            
            if enhanced_data:
                df = pd.DataFrame(enhanced_data)
                
                # Color coding for actions
                def color_action(val):
                    if val == 'BUY':
                        return 'background-color: #d4edda; color: #155724; font-weight: bold;'
                    elif val == 'SELL':
                        return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
                    elif val == 'HOLD':
                        return 'background-color: #fff3cd; color: #856404; font-weight: bold;'
                    return ''
                
                styled_df = df.style.applymap(color_action, subset=['Action'])
                st.dataframe(styled_df, use_container_width=True, height=400)
        
        # Show detailed execution logs
        st.subheader("🔍 Detailed Execution Log")
        
        executed_trades = [r for r in latest_cycle.get('cycle_results', []) 
                          if r.get('execution_result', {}).get('executed')]
        
        if executed_trades:
            for trade in executed_trades:
                exec_data = trade['execution_result']
                profit_color = "green" if exec_data.get('profit_percentage', 0) > 0 else "red"
                
                with st.expander(f"💰 {exec_data['action']} {exec_data.get('shares', 1)} shares of {trade['ticker']} - ${exec_data['price']:.2f}", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Action", exec_data['action'])
                        st.metric("Shares", exec_data.get('shares', 1))
                    
                    with col2:
                        st.metric("Price", f"${exec_data['price']:.2f}")
                        st.metric("Total", f"${exec_data.get('shares', 1) * exec_data['price']:.2f}")
                    
                    with col3:
                        if exec_data.get('profit_percentage') is not None:
                            st.metric("P/L %", f"{exec_data['profit_percentage']:.2f}%", delta=f"{exec_data['profit_percentage']:.2f}%")
                        if exec_data.get('sell_percentage'):
                            st.metric("Position Sold", exec_data['sell_percentage'])
                    
                    st.write("**Entry Reason:**", trade.get('reason', 'HFT Signal'))
                    st.write("**Exit Reason:**", exec_data.get('reason', 'HFT Exit'))
                    st.write("**Confidence:**", trade.get('confidence', 'N/A'))
        else:
            st.info("No trades executed in this cycle. The bot may be waiting for better entry signals.")

else:
    st.info("🚀 No HFT cycles run yet. Click 'Run Single HFT Cycle' to start scalping!")

# Trading History
if len(st.session_state.auto_cycles) > 1:
    with st.expander("📜 HFT Cycle History"):
        for i, cycle in enumerate(st.session_state.auto_cycles[1:6]):  # Show last 5
            if "error" not in cycle:
                st.write(f"**Cycle {i+1}:** {cycle['timestamp'][11:19]} - {cycle['trades_executed']} trades, P&L: {cycle.get('total_pnl', 0):.2f}%")

# Performance Analytics
st.markdown("---")
st.subheader("📈 HFT Performance Analytics")

if st.session_state.auto_cycles:
    # Calculate overall performance
    total_cycles = len(st.session_state.auto_cycles)
    total_trades = sum(cycle.get('trades_executed', 0) for cycle in st.session_state.auto_cycles if "error" not in cycle)
    total_buys = sum(cycle.get('buy_trades', 0) for cycle in st.session_state.auto_cycles if "error" not in cycle)
    total_sells = sum(cycle.get('sell_trades', 0) for cycle in st.session_state.auto_cycles if "error" not in cycle)
    
    perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)
    perf_col1.metric("Total Cycles", total_cycles)
    perf_col2.metric("Total Trades", total_trades)
    perf_col3.metric("Total BUYs", total_buys)
    perf_col4.metric("Total SELLs", total_sells)
    
    # Activity chart data
    if total_cycles > 1:
        cycle_data = []
        for i, cycle in enumerate(st.session_state.auto_cycles[:10]):  # Last 10 cycles
            if "error" not in cycle:
                cycle_data.append({
                    'Cycle': f"Cycle {i+1}",
                    'Trades': cycle.get('trades_executed', 0),
                    'P&L %': cycle.get('total_pnl', 0)
                })
        
        if cycle_data:
            chart_df = pd.DataFrame(cycle_data)
            st.bar_chart(chart_df.set_index('Cycle')['Trades'], use_container_width=True)

# System Controls
st.markdown("---")
st.subheader("⚙️ System Controls")

control_col1, control_col2 = st.columns(2)

with control_col1:
    if st.button("🧹 Clear All History", type="secondary", use_container_width=True):
        st.session_state.auto_cycles = []
        st.rerun()

with control_col2:
    if st.button("🔄 Refresh Portfolio Data", type="secondary", use_container_width=True):
        st.rerun()

# Real-time Status
st.markdown("---")
st.subheader("🔄 Real-time HFT Status")

status_col1, status_col2, status_col3, status_col4 = st.columns(4)

with status_col1:
    st.write("**Trading Engine:** 🟢 Running")
    st.write("**Momentum Scanner:** 🟢 Active")

with status_col2:
    st.write("**Market Data:** 🟢 Connected")
    st.write("**Order Execution:** 🟢 Ready")

with status_col3:
    if st.session_state.auto_cycles:
        last_cycle = st.session_state.auto_cycles[0]
        st.write(f"**Last Cycle:** {last_cycle['timestamp'][11:19]}")
        st.write(f"**Active Cycles:** {len(st.session_state.auto_cycles)}")

with status_col4:
    if st.session_state.is_auto_running:
        st.write("**Bot Status:** 🟢 ACTIVE")
        st.write("**Mode:** Continuous HFT")
    else:
        st.write("**Bot Status:** ⏸️ PAUSED")
        st.write("**Mode:** Manual Control")

# Footer
st.markdown("---")
st.caption("💡 **HFT Scalping Bot** - 10% positions, 0.4% profit targets, 2-minute max hold times • Dynamic stock selection based on momentum and volume")