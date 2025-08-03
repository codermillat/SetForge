#!/usr/bin/env python3
"""
Simple test to debug the SetForge generator
"""

import asyncio
import os
from pathlib import Path
from main_generator import SetForgeGenerator, GenerationConfig

async def test_simple_generation():
    """Test the generator with a simple example."""
    print("🧪 Testing SetForge Generator...")
    
    # Create configuration
    api_key = os.getenv('DIGITALOCEAN_API_KEY')
    if not api_key:
        print("❌ No API key found!")
        return
    
    config = GenerationConfig(
        target_pairs=1,
        max_cost_usd=1.0,
        api_key=api_key,
        api_url='https://inference.do-ai.run/v1/chat/completions',
        model='llama3-8b-instruct',
        max_tokens=200,
        temperature=0.7,
        batch_size=1
    )
    
    print(f"✅ Config created - API key: {config.api_key[:20]}...")
    
    # Test with async context
    async with SetForgeGenerator(config) as generator:
        print("✅ Generator initialized with session")
        
        # Read a file directly and check its content
        data_dir = Path("data/educational")
        files = list(data_dir.glob("*.txt"))
        
        if files:
            test_file = files[0]
            print(f"📄 Testing with file: {test_file.name}")
            
            # Read file content directly
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"📊 File size: {len(content)} characters")
            
            # Check chunks
            chunks = [chunk.strip() for chunk in content.split('\n\n') if chunk.strip()]
            print(f"📄 Found {len(chunks)} chunks")
            
            # Show chunk lengths
            chunk_lengths = [len(chunk) for chunk in chunks]
            long_chunks = [i for i, length in enumerate(chunk_lengths) if length >= 100]
            print(f"🔍 Chunks >= 100 chars: {len(long_chunks)} out of {len(chunks)}")
            
            if long_chunks:
                idx = long_chunks[0]
                print(f"🔍 First long chunk ({idx}): {chunks[idx][:200]}...")
                print(f"🔍 Length: {len(chunks[idx])} characters")
            else:
                print(f"🔍 Max chunk length: {max(chunk_lengths) if chunk_lengths else 0}")
            
            try:
                pairs = await generator.process_file(test_file)
                print(f"✅ Generated {len(pairs)} pairs")
                
                for i, pair in enumerate(pairs[:1]):  # Show first pair
                    print(f"\n📝 Pair {i+1}:")
                    print(f"Q: {pair.question}")
                    print(f"A: {pair.answer[:100]}...")
                    print(f"Confidence: {pair.confidence:.3f}")
                    
            except Exception as e:
                print(f"❌ Error processing file: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("❌ No educational files found")

if __name__ == "__main__":
    asyncio.run(test_simple_generation())
