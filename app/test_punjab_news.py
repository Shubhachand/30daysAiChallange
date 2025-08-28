#!/usr/bin/env python3
import sys
import os

# ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.web_search import web_search

def test_punjab_news():
    print("Testing news/price/location queries (using web_search)...")
    test_queries = [
        "what is happening in punjab",
        "news of punjab",
        "latest news from punjab",
        "tell me the latest news here today",
        "price of eth",
        "where am i"
    ]

    for q in test_queries:
        print(f"\n--- Query: {q} ---")
        try:
            # prefer short-circuit special handler first
            resp = web_search.handle_special_queries(q)
            if resp is not None:
                print(resp)
                continue
            # otherwise use the LLM-first pipeline with fallbacks
            results = web_search.search_with_fallback(q, max_results=5, freshness_days=7)
            print(web_search.humanize_results(results))
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    test_punjab_news()