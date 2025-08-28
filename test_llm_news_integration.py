#!/usr/bin/env python3
import sys
import os

# Add the app directory to the Python path
app_dir = os.path.join(os.path.dirname(__file__), 'app')
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from app.config import settings
from app.services.llm_gemini import llm

def test_llm_news_integration():
    print("Testing LLM news integration...")
    
    # Test various news-related queries
    test_queries = [
        "latest news",
        "technology news",
        "what's happening in the world",
        "recent developments",
        "news about AI"
    ]
    
    for query in test_queries:
        print(f"\n--- Testing query: '{query}' ---")
        try:
            response = llm.generate(query)
            print(f"Response: {response[:200]}...")  # Show first 200 chars
            print(f"Response length: {len(response)} characters")
        except Exception as e:
            print(f"Error with query '{query}': {e}")
    
    print("\n--- Testing edge cases ---")
    
    # Test empty query
    try:
        response = llm.generate("")
        print(f"Empty query response: {response[:100]}...")
    except Exception as e:
        print(f"Error with empty query: {e}")
    
    # Test very specific query
    try:
        response = llm.generate("latest news about artificial intelligence and machine learning")
        print(f"Specific query response: {response[:200]}...")
    except Exception as e:
        print(f"Error with specific query: {e}")

if __name__ == "__main__":
    test_llm_news_integration()
