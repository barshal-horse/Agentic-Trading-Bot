# main.py

import os
from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub

from tools import get_stock_info, get_financial_news, web_search

def main():
    """
    Main function to run the financial analyst agent.
    """
    load_dotenv()

    # --- 1. Initialize the LLM (Agent's Brain) ---
    # We use a powerful model for the agent's core reasoning.
    # "gemini-1.5-pro-latest" is excellent. "gemini-pro" is a solid free-tier alternative.
    print("Initializing Gemini LLM...")
    # main.py (The Fix)
    # tools.py (The Fix)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0)
    # --- 2. Define the Agent's Toolbox ---
    tools = [get_stock_info, get_financial_news, web_search]
    print("Tools loaded.")

    # --- 3. Create the Agent's Prompt ---
    # The prompt is the agent's instruction manual and personality.
    # We pull a standard ReAct (Reasoning and Acting) prompt from LangChain Hub.
    prompt = hub.pull("hwchase17/react")
    print("Agent prompt loaded.")

    # --- 4. Create the Agent ---
    # This binds the LLM, the tools, and the prompt together.
    agent = create_react_agent(llm, tools, prompt)
    print("Agent created.")

    # --- 5. Create the Agent Executor (The Runtime) ---
    # This will run the agent's reasoning loop until the task is complete.
    # verbose=True lets you see the agent's "thoughts" in the console.
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True, 
        handle_parsing_errors=True  # Helps with occasional LLM output format errors
    )
    print("Agent Executor created.")

    # --- 6. Define the Master Task ---
    # This is the high-level goal you give to the agent.
    task_prompt = """
    Generate a comprehensive financial analysis report for the company with the ticker {ticker}.

    Your process should be as follows:
    1. First, get the company's general stock information to understand its business. Use its full name for subsequent searches.
    2. Next, use the company's full name to search for the latest financial news and perform a sentiment analysis.
    3. Then, perform a web search to identify the company's main competitors.
    4. Finally, synthesize all the gathered information into a single, cohesive report.

    Your final answer MUST be a well-structured and detailed financial report that includes these sections:
    - Business Summary
    - Recent News Summary & Sentiment
    - Main Competitors
    - Investment Thesis (a balanced bull vs. bear case)
    """

    # --- 7. Run the Agent ---
    ticker = input("Please enter the stock ticker (e.g., AAPL, TSLA, NVDA): ")
    print(f"\nStarting analysis for ticker: {ticker}...")
    
    try:
        result = agent_executor.invoke({
            "input": task_prompt.format(ticker=ticker)
        })

        # --- 8. Print the Final Report ---
        print("\n\n--- FINAL REPORT ---")
        print(result['output'])
    
    except Exception as e:
        print(f"\nAn error occurred during agent execution: {e}")


if __name__ == "__main__":
    main()