# tools.py

import os
import yfinance as yf
from langchain.tools import tool
from newsapi import NewsApiClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.tools.tavily_search import TavilySearchResults

# --- Tool 1: Stock Information Fetcher ---
@tool
def get_stock_info(ticker: str) -> dict:
    """
    Gets key financial information for a given stock ticker from Yahoo Finance.
    Returns a dictionary with info like company name, business summary, and key financial ratios.
    """
    try:
        stock = yf.Ticker(ticker)
        # The .info dictionary can be very large; let's select key fields to avoid overwhelming the context
        key_info = {
            "longName": stock.info.get("longName"),
            "businessSummary": stock.info.get("businessSummary"),
            "marketCap": stock.info.get("marketCap"),
            "trailingPE": stock.info.get("trailingPE"),
            "forwardPE": stock.info.get("forwardPE"),
            "debtToEquity": stock.info.get("debtToEquity"),
            "returnOnEquity": stock.info.get("returnOnEquity"),
            "totalRevenue": stock.info.get("totalRevenue"),
        }
        return key_info
    except Exception as e:
        return f"Error fetching stock info for {ticker}: {e}"


# --- Tool 2: Financial News Summarizer and Analyzer ---
# Initialize NewsAPI client from environment variable
newsapi = NewsApiClient(api_key=os.environ['NEWS_API_KEY'])

@tool
def get_financial_news(company_name: str, max_articles: int = 5) -> str:
    """
    Fetches, summarizes, and analyzes the sentiment of the latest financial news for a company.
    Use the company's full name (e.g., 'NVIDIA Corporation') for best results.
    """
    try:
        # Fetch news articles
        all_articles = newsapi.get_everything(q=company_name, language='en', sort_by='publishedAt', page_size=max_articles)
        
        # Concatenate article content for processing
        articles_text = ""
        for article in all_articles['articles']:
            articles_text += f"Title: {article['title']}\nContent: {article.get('description', 'N/A')}\n\n"

        # Use Gemini to summarize and analyze sentiment
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0)
        
        prompt = PromptTemplate(
            template="""
            You are a highly skilled financial news analyst. Here is a block of recent news articles about {company_name}:
            ---
            {articles}
            ---
            Based ONLY on the information in these articles, please provide:
            1. A concise summary of the key news points.
            2. An overall sentiment analysis (Positive, Neutral, or Negative) with a brief justification.
            """,
            input_variables=["company_name", "articles"]
        )
        chain = LLMChain(llm=llm, prompt=prompt)
        summary = chain.run(company_name=company_name, articles=articles_text)
        return summary
    except Exception as e:
        return f"Error fetching or processing news for {company_name}: {e}"


# --- Tool 3: General Web Search ---
@tool
def web_search(query: str) -> str:
    """
    Performs a web search using the Tavily Search API to find information on competitors, market trends, etc.
    This is useful for finding information not covered by other specialized tools.
    """
    try:
        tavily_tool = TavilySearchResults()
        return tavily_tool.invoke({"query": query})
    except Exception as e:
        return f"Error performing web search for query '{query}': {e}"