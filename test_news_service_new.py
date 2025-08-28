#!/usr/bin/env python3
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
from app.config import settings
from app.services.news_service import news_service

def test_news_service():
    print("Testing news service with new API key...")
    print(f"Using NEWS_API_KEY: {settings.NEWS_API_KEY[:10]}...")
    
    # Test with a simple query
    results = news_service.get_latest_news('technology', 2)
    print(f"Found {len(results)} news articles")
    
    for i, article in enumerate(results, 1):
        print(f"{i}. {article['title']}")
        if article.get('content'):
            print(f"   Content: {article['content'][:100]}...")
        if article.get('url'):
            print(f"   URL: {article['url']}")
        print()

if __name__ == "__main__":
    test_news_service()
