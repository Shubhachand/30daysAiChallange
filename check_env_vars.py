#!/usr/bin/env python3
import os

print("Current environment variables:")
for key, value in os.environ.items():
    if 'NEWS' in key or 'API' in key:
        print(f"{key}: {value}")

# Check specifically for NEWS_API_KEY
news_api_key = os.environ.get('NEWS_API_KEY')
print(f"\nNEWS_API_KEY: {news_api_key}")
