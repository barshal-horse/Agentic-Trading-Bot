# app.py
import streamlit as st

st.set_page_config(
    page_title="AI Financial Trading Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🚀 AI Financial Trading Platform")
st.subheader("Professional-Grade Automated Trading & Analysis")

st.markdown("""
### 🌟 Platform Features:

**🤖 Smart Trading Systems**
- **Single Stock Analysis**: Deep research on individual stocks
- **Automated Multi-Stock Trading**: AI-powered portfolio management
- **Advanced Analytics**: Performance tracking and insights

**📊 Professional Tools**
- Real-time market data and news
- Technical and fundamental analysis
- Risk management and position sizing
- Interactive charts and dashboards

**🎯 Navigation**
- **📈 Financial Analyst**: Research individual stocks
- **🤖 Paper Trading**: Manual single-stock trading
- **🚀 Automated Trading**: Multi-stock automated system
- **📊 Analytics**: Performance insights and metrics
- **ℹ️ About**: Project information
""")

st.markdown("---")

st.success("🚀 **Live Features**: Multi-stock automated trading, advanced analytics, and real-time risk management!")

# Quick stats preview
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Supported Stocks", "50+", "US Markets")

with col2:
    st.metric("Analysis Tools", "15+", "Real-time")

with col3:
    st.metric("Risk Controls", "8", "Active")

st.markdown("---")
st.caption("Built with Streamlit, LangGraph, Alpaca API, and Google Gemini • Educational Use Only")