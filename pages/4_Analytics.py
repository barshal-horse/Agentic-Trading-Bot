# pages/4_Analytics.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json
import os
from analytics_logger import get_analytics_data

st.set_page_config(page_title="Trading Analytics", layout="wide")

st.title("📊 Trading Analytics & Performance Dashboard")
st.markdown("Deep insights into your trading bot's performance, decisions, and profitability")

# Load analytics data
analytics_data = get_analytics_data()

def calculate_performance_metrics(trades, decisions):
    """Calculate comprehensive performance metrics"""
    if not trades:
        return {
            'total_trades': 0,
            'win_rate': 0,
            'total_pnl': 0,
            'avg_trade_pnl': 0,
            'best_trade': 0,
            'worst_trade': 0,
            'sharpe_ratio': 0,
            'max_drawdown': 0
        }
    
    # Convert to DataFrame
    trades_df = pd.DataFrame(trades)
    
    # Basic metrics
    total_trades = len(trades_df)
    winning_trades = len(trades_df[trades_df['pnl'] > 0])
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    # PnL metrics
    total_pnl = trades_df['pnl'].sum()
    avg_trade_pnl = trades_df['pnl'].mean()
    best_trade = trades_df['pnl'].max()
    worst_trade = trades_df['pnl'].min()
    
    # Risk metrics (simplified)
    returns = trades_df['pnl'] / trades_df['investment'] if 'investment' in trades_df.columns else trades_df['pnl']
    sharpe_ratio = returns.mean() / returns.std() if returns.std() > 0 else 0
    
    return {
        'total_trades': total_trades,
        'win_rate': win_rate,
        'total_pnl': total_pnl,
        'avg_trade_pnl': avg_trade_pnl,
        'best_trade': best_trade,
        'worst_trade': worst_trade,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': 0  # Simplified for demo
    }

# Performance Overview
st.markdown("---")
st.subheader("📈 Performance Overview")

metrics = calculate_performance_metrics(
    analytics_data['trades'],
    analytics_data['decisions']
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Trades", metrics['total_trades'])
    st.metric("Win Rate", f"{metrics['win_rate']:.1f}%")

with col2:
    st.metric("Total P&L", f"${metrics['total_pnl']:+.2f}")
    st.metric("Avg Trade P&L", f"${metrics['avg_trade_pnl']:+.2f}")

with col3:
    st.metric("Best Trade", f"${metrics['best_trade']:+.2f}")
    st.metric("Worst Trade", f"${metrics['worst_trade']:+.2f}")

with col4:
    st.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
    st.metric("Max Drawdown", f"{metrics['max_drawdown']:.2f}%")

# Charts Section
st.markdown("---")
st.subheader("📊 Performance Charts")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    # P&L Over Time Chart
    st.write("**P&L Over Time**")
    
    if analytics_data['trades']:
        trades_df = pd.DataFrame(analytics_data['trades'])
        trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'])
        trades_df = trades_df.sort_values('timestamp')
        trades_df['cumulative_pnl'] = trades_df['pnl'].cumsum()
        
        fig = px.line(trades_df, x='timestamp', y='cumulative_pnl', 
                     title="Cumulative P&L Over Time")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No trade data available yet")

with chart_col2:
    # Win/Loss Distribution
    st.write("**Trade Outcome Distribution**")
    
    if analytics_data['trades']:
        trades_df = pd.DataFrame(analytics_data['trades'])
        outcome_counts = trades_df['pnl'].apply(lambda x: 'Win' if x > 0 else 'Loss' if x < 0 else 'Break Even').value_counts()
        
        fig = px.pie(values=outcome_counts.values, names=outcome_counts.index,
                    title="Win/Loss Distribution")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No trade data available yet")

# Decision Analytics
st.markdown("---")
st.subheader("🤖 AI Decision Analytics")

decisions_col1, decisions_col2 = st.columns(2)

with decisions_col1:
    # Decision Confidence Analysis
    st.write("**Decision Confidence Levels**")
    
    if analytics_data['decisions']:
        decisions_df = pd.DataFrame(analytics_data['decisions'])
        confidence_counts = decisions_df['confidence'].value_counts()
        
        fig = px.bar(x=confidence_counts.index, y=confidence_counts.values,
                    title="Decision Confidence Distribution",
                    color=confidence_counts.values)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No decision data available yet")

with decisions_col2:
    # Action Distribution
    st.write("**Trading Action Distribution**")
    
    if analytics_data['decisions']:
        decisions_df = pd.DataFrame(analytics_data['decisions'])
        action_counts = decisions_df['action'].value_counts()
        
        fig = px.pie(values=action_counts.values, names=action_counts.index,
                    title="Trading Actions Taken")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No decision data available yet")

# Trading Behavior Analysis
st.markdown("---")
st.subheader("🔍 Trading Behavior Analysis")

behavior_col1, behavior_col2 = st.columns(2)

with behavior_col1:
    # Time-based Analysis
    st.write("**Trading Activity by Hour**")
    
    if analytics_data['decisions']:
        decisions_df = pd.DataFrame(analytics_data['decisions'])
        decisions_df['hour'] = pd.to_datetime(decisions_df['timestamp']).dt.hour
        hour_counts = decisions_df['hour'].value_counts().sort_index()
        
        fig = px.line(x=hour_counts.index, y=hour_counts.values,
                     title="Trading Activity Throughout Day",
                     labels={'x': 'Hour of Day', 'y': 'Number of Decisions'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No decision data available yet")

with behavior_col2:
    # Stock Performance
    st.write("**Performance by Stock**")
    
    if analytics_data['trades']:
        trades_df = pd.DataFrame(analytics_data['trades'])
        stock_performance = trades_df.groupby('ticker')['pnl'].agg(['sum', 'count', 'mean']).round(2)
        stock_performance = stock_performance.rename(columns={'sum': 'Total P&L', 'count': 'Trades', 'mean': 'Avg P&L'})
        
        st.dataframe(stock_performance, use_container_width=True)
    else:
        st.info("No trade data available yet")

# Data Management
st.markdown("---")
st.subheader("📁 Data Management")

col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 Refresh Analytics Data", use_container_width=True):
        st.rerun()

with col2:
    # Export functionality
    if st.button("📤 Export Analytics Report", use_container_width=True):
        report_data = {
            'performance_metrics': metrics,
            'summary': f"Analytics report generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            'total_decisions_analyzed': len(analytics_data['decisions']),
            'total_trades_analyzed': len(analytics_data['trades'])
        }
        
        # Convert to JSON for download
        st.download_button(
            label="Download JSON Report",
            data=json.dumps(report_data, indent=2),
            file_name=f"trading_analytics_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            use_container_width=True
        )

# Footer
st.markdown("---")
st.caption("💡 Analytics update automatically. Data is stored locally in the 'trading_logs' folder.")