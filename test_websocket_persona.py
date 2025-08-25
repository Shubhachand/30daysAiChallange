#!/usr/bin/env python3
"""
Test script to verify WebSocket persona functionality
"""

import asyncio
import websockets
import json

async def test_persona_websocket():
    """Test WebSocket connection with different personas"""
    
    personas = ["Teacher", "Pirate", "Cowboy", "Robot"]
    
    for persona in personas:
        try:
            print(f"\nTesting persona: {persona}")
            async with websockets.connect(f"ws://localhost:8000/ws/transcribe?persona={persona}") as websocket:
                print(f"✅ Successfully connected with persona: {persona}")
                
                # Send a simple test message
                test_message = json.dumps({"type": "test", "text": "Hello"})
                await websocket.send(test_message)
                print("✅ Test message sent successfully")
                
        except Exception as e:
            print(f"❌ Error with persona {persona}: {e}")

if __name__ == "__main__":
    print("Testing WebSocket persona connections...")
    asyncio.run(test_persona_websocket())
