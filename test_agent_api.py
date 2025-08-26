#!/usr/bin/env python3
"""
Test script to verify the agent API with web search functionality
"""
import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API endpoint
API_URL = "http://localhost:8000/agent/chat"

def test_agent_api():
    """Test the agent API for web search integration"""
    print("Testing agent API for web search integration...")
    
    # Sample session ID and file (mocking file upload)
    session_id = "test_session"
    mock_file_path = "path/to/mock_audio_file.wav"  # Replace with a valid audio file path if needed
    
    # Test prompts that should trigger web search
    test_prompts = [
        "What are the latest developments in AI research?",
        "Find me recent news about space exploration",
        "Search for information about climate change solutions"
    ]
    
    for prompt in test_prompts:
        print(f"\nTesting prompt: '{prompt}'")
        
        # Simulate file upload
        with open(mock_file_path, 'rb') as file:
            response = requests.post(API_URL, files={'file': file}, data={'session_id': session_id, 'persona': 'Teacher'})
        
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_agent_api()
