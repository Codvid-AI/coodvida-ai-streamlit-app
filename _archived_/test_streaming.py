#!/usr/bin/env python3
"""
Test script for streaming functionality
"""

import json
import time
from main import APIClient
from config import Config

def test_streaming():
    """Test the streaming functionality"""
    print("🧪 Testing Streaming Functionality")
    print("=" * 50)
    
    # Initialize API client
    api_url = Config.get_api_url("local")
    print(f"🔗 API URL: {api_url}")
    
    api_client = APIClient(api_url)
    
    # Test the process_streaming_response method
    print("\n📡 Testing process_streaming_response method...")
    
    # Create a mock streaming response (simulating what the real API would return)
    class MockStreamingResponse:
        def __init__(self):
            self.chunks = [
                '{"result": true, "response": {"text": "Hello"}}',
                '{"result": true, "response": {"text": " there"}}',
                '{"result": true, "response": {"text": "! How"}}',
                '{"result": true, "response": {"text": " can I"}}',
                '{"result": true, "response": {"text": " help you"}}',
                '{"result": true, "response": {"text": " today?"}}'
            ]
            self.index = 0
        
        def iter_content(self, chunk_size=None, decode_unicode=True):
            for chunk in self.chunks:
                yield chunk
                time.sleep(0.1)  # Simulate network delay
    
    mock_response = MockStreamingResponse()
    
    print("📝 Processing mock streaming response...")
    aggregated_text = ""
    
    try:
        for text_chunk, is_final, data_mods in api_client.process_streaming_response(mock_response, "test_project"):
            if text_chunk:
                aggregated_text += text_chunk
                print(f"📨 Chunk received: '{text_chunk}' (Final: {is_final})")
                print(f"📊 Current text: '{aggregated_text}'")
            
            if is_final:
                print("✅ Streaming complete!")
                break
                
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"\n🎯 Final aggregated text: '{aggregated_text}'")
    print("✅ Streaming test completed successfully!")

if __name__ == "__main__":
    test_streaming()
