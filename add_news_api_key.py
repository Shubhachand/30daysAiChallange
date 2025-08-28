#!/usr/bin/env python3
import os

# Add NEWS_API_KEY to .env file
env_file = ".env"
news_api_key = "NEWS_API_KEY=3ee17717ab0a41dbd5a2edd51d330941"

# Check if .env file exists and add the key
if os.path.exists(env_file):
    # Read existing content
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Check if NEWS_API_KEY already exists
    if "NEWS_API_KEY" not in content:
        # Add the key to the end of the file
        with open(env_file, 'a') as f:
            f.write(f"\n{news_api_key}\n")
        print("Added NEWS_API_KEY to .env file")
    else:
        print("NEWS_API_KEY already exists in .env file")
else:
    # Create new .env file with the key
    with open(env_file, 'w') as f:
        f.write(f"{news_api_key}\n")
    print("Created .env file with NEWS_API_KEY")

print("Please restart your application for the changes to take effect")
