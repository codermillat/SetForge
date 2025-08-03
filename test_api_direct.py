#!/usr/bin/env python3
"""
Direct API test for DigitalOcean
"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv

async def test_api_direct():
    """Test DigitalOcean API directly."""
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('DIGITALOCEAN_API_KEY')
    
    if not api_key:
        print("❌ No API key found!")
        return
    
    print(f"🔑 API Key: {api_key[:20]}...")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': 'llama3-8b-instruct',
        'messages': [
            {'role': 'user', 'content': 'Hello, what is 2+2?'}
        ],
        'max_tokens': 50,
        'temperature': 0.7
    }
    
    print("📡 Making API request...")
    
    timeout = aiohttp.ClientTimeout(total=30)
    
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                'https://inference.do-ai.run/v1/chat/completions',
                headers=headers,
                json=data
            ) as response:
                print(f"📊 Response status: {response.status}")
                print(f"📊 Response headers: {dict(response.headers)}")
                
                if response.status == 200:
                    result = await response.json()
                    print("✅ API call successful!")
                    print(f"Response: {result}")
                else:
                    error_text = await response.text()
                    print(f"❌ API error: {response.status}")
                    print(f"Error body: {error_text}")
                    
    except asyncio.TimeoutError:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_api_direct())
