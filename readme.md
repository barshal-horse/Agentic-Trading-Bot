***

# 🚀 AI Agentic Financial Trading Platform

A comprehensive AI-powered trading dashboard that combines **Real-time Technical Analysis**, **LLM-based Market Reasoning**, and **Automated High-Frequency Scalping (HFT)** strategies. Built with Streamlit, LangChain, and the Alpaca Paper Trading API.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31%2B-ff4b4b)
![Alpaca](https://img.shields.io/badge/Alpaca-Paper_Trading-yellow)
![Gemini](https://img.shields.io/badge/AI-Google_Gemini-orange)

## 🌟 Key Features

### 1. 📈 AI Financial Analyst
*   Real-time stock data visualization (Candlestick charts).
*   Automated calculation of Technical Indicators (RSI, SMA-20, SMA-50, Volume Ratio).
*   AI-generated insights based on market conditions.

### 2. 🤖 Agentic Paper Trader
*   **LangGraph Agent:** Uses Google Gemini to reason through trading decisions.
*   **Tool-Use:** The agent autonomously fetches news, checks prices, and executes trades based on a "Buy/Sell/Hold" prompt.
*   **News Integration:** Analyzes sentiment from NewsAPI to inform decisions.

### 3. ⚡ Automated HFT Scalper
*   **High-Frequency Strategy:** Scans for momentum and small dips (0.1% drops) to execute rapid scalp trades.
*   **Dynamic Watchlist:** Automatically finds active, high-volume, and trending stocks.
*   **Risk Management:** Built-in stop-losses (-0.3%), profit targets (+0.4%), and time-based exits (2 minutes).

### 4. 📊 Performance Analytics
*   Track P&L (Profit & Loss) over time.
*   Analyze trade distribution (Wins vs. Losses).
*   Review detailed decision logs stored locally.

---

## 🛠️ Tech Stack

*   **Frontend:** Streamlit
*   **AI/LLM:** LangChain, LangGraph, Google Gemini (via `langchain-google-genai`)
*   **Brokerage API:** Alpaca Markets (Paper Trading)
*   **Data Sources:** Yahoo Finance (`yfinance`), NewsAPI
*   **Data Processing:** Pandas, NumPy
*   **Visualization:** Plotly

---

## ⚙️ Prerequisites

Before running the application, ensure you have:

1.  **Python 3.9+** installed.
2.  **Alpaca Paper Trading Account** (Free) -> [Sign up here](https://alpaca.markets/).
3.  **Google Gemini API Key** (Free tier available) -> [Get key here](https://aistudio.google.com/).
4.  **NewsAPI Key** (Free) -> [Get key here](https://newsapi.org/).

---

## 🚀 Installation

1.  **Clone the repository** (or download files):
    ```bash
    git clone https://github.com/yourusername/agentic-trading.git
    cd agentic-trading
    ```

2.  **Create a Virtual Environment** (Recommended):
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Mac/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables:**
    Create a file named `.env` in the root directory and add your keys:

    ```env
    # .env file
    
    # Google Gemini AI
    GOOGLE_API_KEY=your_google_api_key_here
    
    # Alpaca Paper Trading
    APCA_API_KEY_ID=your_alpaca_key_id
    APCA_API_SECRET_KEY=your_alpaca_secret_key
    
    # News Data
    NEWS_API_KEY=your_newsapi_key
    ```

---

## ▶️ Usage

1.  **Run the Application:**
    ```bash
    streamlit run app.py
    ```

2.  **Navigate the Interface:**
    *   **Home:** Project overview and status.
    *   **Financial Analyst:** Enter a ticker (e.g., AAPL) to see charts and indicators.
    *   **Paper Trading:** Manually trigger the AI Agent to analyze a specific stock and make a trade decision.
    *   **Automated Trading:** Start the HFT Scalper bot. **Warning:** This will execute trades automatically on your Alpaca Paper account.
    *   **Analytics:** View your trading history and performance metrics.

---

## 📂 Project Structure

```text
├── app.py                  # Main Streamlit entry point
├── agent_logic.py          # LangGraph/LangChain agent definitions
├── automated_agent.py      # HFT Scalping logic loop
├── analytics_logger.py     # JSON logging system for trades
├── momentum_scanner.py     # Logic to find active stocks
├── tools.py                # Tools for the AI (Alpaca, YFinance wrappers)
├── trading_config.py       # Configuration parameters
├── pages/                  # Streamlit Multi-Page structure
│   ├── 1_Financial_Analyst.py
│   ├── 2_Paper_Trading.py
│   ├── 3_Automated_Trading.py
│   └── 4_Analytics.py
├── trading_logs/           # Auto-generated folder for JSON logs
├── requirements.txt        # Python dependencies
└── .env                    # API Keys (Not included in repo)
```

---

## ⚠️ Disclaimer

**EDUCATIONAL USE ONLY.**

This software is for **Paper Trading (Simulated)** purposes only.
*   Do not use this with real money.
*   The HFT strategy provided is a basic example (0.1% mean reversion) and is not guaranteed to be profitable.
*   The creators are not responsible for any financial losses incurred.
*   Stock market data via `yfinance` is not real-time (15 min delay usually) and is not suitable for real-money HFT.

---

## 🤝 Contributing

Feel free to fork this project and submit Pull Requests.
Ideas for improvement:
*   Add a proper database (SQLite/PostgreSQL) instead of JSON logs.
*   Implement more advanced trading strategies (MACD, Bollinger Bands).
*   Add email notifications for trade execution.
