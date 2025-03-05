from flask import Flask, render_template, jsonify, request
import yfinance as yf
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()

# Load API key
groq_api = os.getenv("GROQ_API_KEY")

# ✅ Function to Fetch Stock Data
def fetch_stock_data(company_ticker):
    stock = yf.Ticker(company_ticker)
    historical_data = stock.history(period="1mo")
    historical_data.index = historical_data.index.astype(str)  # Convert timestamps to string
    return {"historical_data": historical_data.to_dict()}

# ✅ Agent Setup
stock_data_agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile", api_key=groq_api),
    tools=[DuckDuckGoTools()],
    markdown=True,
    instructions=["Fetch real-time stock data for the given company.",
        "Retrieve key metrics such as price, volume, and historical trends."]
)

analysis_agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile", api_key=groq_api),
    markdown=True,
    instructions=["Analyze the given stock data.",
        "Identify trends, volatility, and key indicators such as moving averages."]
)

recommendation_agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile", api_key=groq_api),
    markdown=True,
    instructions=["Provide a stock recommendation (Buy, Hold, or Sell) based on recent data and market trends."]
)

# ✅ Flask Routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_stock_data", methods=["POST"])
def get_stock_data():
    data = request.json
    ticker = data.get("ticker", "TSLA")  # Default to TSLA if no ticker is provided

    # Fetch stock data
    stock_data = fetch_stock_data(ticker)

    # ✅ Structured Prompt
    structured_prompt = f"""
    Collect real-time stock data and market insights for {ticker}.

    1. Retrieve historical stock prices, volume changes, and performance over the last month.
    2. Search for recent news articles related to {ticker} that might impact its stock performance.
    3. Analyze key financial indicators such as moving averages, volatility, and momentum.
    4. Based on historical trends and recent news, provide a stock recommendation (Buy, Hold, or Sell).
    5. At last, display the disclaimer: "Please do your own research before making any financial decisions."
    """

    try:
        # Fetch real-time news using AI agent
        stock_data_with_news = stock_data_agent.run(structured_prompt)
        stock_news_content = stock_data_with_news.content if hasattr(stock_data_with_news, 'content') else str(stock_data_with_news)

        # Analyze stock data
        analysis_result = analysis_agent.run(stock_news_content)
        analysis_text = analysis_result.content if hasattr(analysis_result, 'content') else str(analysis_result)

        # Get AI-powered recommendation
        recommendation = recommendation_agent.run(analysis_text)
        recommendation_text = recommendation.content if hasattr(recommendation, 'content') else str(recommendation)

        # ✅ Return formatted JSON response
        return jsonify({
            "stock_data": stock_data,
            "news": stock_news_content.strip(),
            "analysis": analysis_text.strip(),
            "recommendation": recommendation_text.strip()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return error message

if __name__ == "__main__":
    app.run(debug=True)