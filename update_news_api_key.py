#!/usr/bin/env python3
import os

# Read the current .env file
env_file = ".env"
new_api_key = "NEWS_API_KEY=your_new_api_key_here"  # Replace with the actual new key

if os.path.exists(env_file):
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Find and replace the NEWS_API_KEY line
    updated_lines = []
    for line in lines:
        if line.startswith("NEWS_API_KEY="):
            updated_lines.append(f"{new_api_key}\n")
        else:
            updated_lines.append(line)
    
    # Write the updated content back
    with open(env_file, 'w') as f:
        f.writelines(updated_lines)
    
    print("Updated NEWS_API_KEY in .env file")
else:
    print(".env file not found")

print("Please provide the actual new API key to replace 'your_new_api_key_here'")
