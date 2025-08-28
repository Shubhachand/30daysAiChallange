import logging
import requests
from app.config import settings
from typing import List, Dict, Any

log = logging.getLogger(__name__)

class NewsService:
    def __init__(self):
        self.api_key = settings.NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2"

    def get_latest_news(self, query: str, max_results: int = 5, location: str = None) -> List[Dict[str, Any]]:
        """Fetch the latest news articles based on a query, optionally filtered by location."""
        url = f"{self.base_url}/everything"
        params = {
            "q": query,
            "pageSize": max_results,
            "apiKey": self.api_key,
            "sortBy": "publishedAt"  # Get the most recent news first
        }
        
        # Add location to query if specified
        if location:
            params["q"] = f"{query} {location}"
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            articles = response.json().get("articles", [])
            
            # Filter out articles with no content
            filtered_articles = []
            for article in articles:
                if article.get("title") and article.get("description"):
                    filtered_articles.append({
                        "title": article.get("title"),
                        "url": article.get("url"),
                        "content": article.get("description"),
                        "publishedAt": article.get("publishedAt")
                    })
            
            return filtered_articles
        except Exception as e:
            log.error("Failed to fetch news: %s", e)
            return []

    def get_news_by_location(self, location: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Get news specifically about a location."""
        return self.get_latest_news("news", max_results, location)

# Global instance
news_service = NewsService()
