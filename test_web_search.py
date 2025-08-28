#!/usr/bin/env python3
import sys
import os

# Set the NEWS_API_KEY environment variable
os.environ['NEWS_API_KEY'] = '3ee17717ab0a41db极狐5a2edd51d330941'

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.web_search import web_search

def test_web_search_fallback():
    print("Testing web search fallback...")
    
    # Test with a simple query
    results = web_search.get_news_fallback('technology', 2)
    print(f"Found {len(results)} news articles")
    
    for i, article in enumerate(results, 1):
        print(f"{i}. {article['title']}")
        if article.get('content'):
            print(f"   Content: {article['content'][:100]}...")
        if article.get('url'):
            print(f"   URL: {article['url']}")
        print()

if __name__ == "__main__":
    test_web_search_fallback()
