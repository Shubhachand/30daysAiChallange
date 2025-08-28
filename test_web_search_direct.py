#!/usr/bin/env python3
"""
Direct test of web search functionality
"""
import os
import sys
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Load environment variables
load_dotenv()

from app.services.web_search import web_search

def test_web_search():
    """Test web search functionality directly"""
    print("Testing web search functionality directly...")
    
    # Test search
    query = "latest news from Punjab"
    print(f"Searching for: '{query}'")
    
    try:
        results = web_search.search_web(query, max_results=2)
        print(f"Found {len(results)} results")
        
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"Title: {result['title']}")
            print(f"URL: {result['url']}")
            print(f"Content: {result['content'][:100]}...")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_web_search()
