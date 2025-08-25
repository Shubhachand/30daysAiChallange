#!/usr/bin/env python3
"""
Test script to verify persona functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.llm_gemini import GeminiLLM
from app.config import settings

def test_personas():
    """Test different personas with sample input"""
    
    # Initialize LLM
    llm = GeminiLLM(settings.GEMINI_API_KEY)
    
    # Test input
    test_input = "Hello, how are you today?"
    
    print("Testing personas with input:", test_input)
    print("-" * 50)
    
    # Test each persona
    personas = ["Teacher", "Pirate", "Cowboy", "Robot"]
    
    for persona in personas:
        try:
            prompt = llm.generate_persona_prompt(persona, test_input)
            print(f"\n{persona}:")
            print(f"Prompt: {prompt}")
            
            # Generate response
            response = llm.generate(prompt, persona)
            if response:
                print(f"Response: {response}")
            else:
                print("Failed to generate response")
                
        except Exception as e:
            print(f"Error with {persona}: {e}")

if __name__ == "__main__":
    test_personas()
