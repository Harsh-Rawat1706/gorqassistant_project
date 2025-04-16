import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2/top-headlines"

def fetch_news(country="us", category="general"):
    """Fetch breaking news from NewsAPI"""
    url = f"{BASE_URL}?country={country}&category={category}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["articles"]
    else:
        return []

def get_headlines():
    """Extract and return just the headlines from the fetched articles."""
    articles = fetch_news()
    return [article["title"] for article in articles]
