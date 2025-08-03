#!/usr/bin/env python3
"""
Detailed step-by-step test of the SetForge generator
"""

import asyncio
import os
import random
from pathlib import Path
from main_generator import SetForgeGenerator, GenerationConfig, QuestionType, StudentPersona

async def test_step_by_step():
    """Test each step of the generation process."""
    print("🧪 Step-by-step SetForge Generator Test...")
    
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
    
    print(f"✅ Config created")
    
    # Test enums
    print(f"📊 QuestionType values: {[qt.value for qt in QuestionType]}")
    print(f"📊 StudentPersona values: {[sp.value for sp in StudentPersona]}")
    
    # Test with async context
    async with SetForgeGenerator(config) as generator:
        print("✅ Generator initialized with session")
        
        # Read a file directly
        data_dir = Path("data/educational")
        files = list(data_dir.glob("*.txt"))
        test_file = files[0]
        
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get chunks
        chunks = [chunk.strip() for chunk in content.split('\n\n') if chunk.strip()]
        long_chunks = [chunk for chunk in chunks if len(chunk) >= 100]
        
        if not long_chunks:
            print("❌ No long chunks found")
            return
        
        test_chunk = long_chunks[0]
        print(f"🔍 Testing with chunk: {test_chunk[:100]}...")
        
        # Test question generation
        print("\n🎯 Testing question generation...")
        q_types = list(QuestionType)
        personas = list(StudentPersona)
        
        for i in range(2):  # Test 2 iterations
            try:
                q_type = random.choice(q_types)
                persona = random.choice(personas)
                
                print(f"   Iteration {i+1}: {q_type.value} + {persona.value}")
                
                # Get template
                if hasattr(generator, 'templates') and q_type in generator.templates:
                    template = random.choice(generator.templates[q_type])
                    print(f"   Template: {template[:50]}...")
                    
                    # Generate question
                    question = generator.generate_question_from_template(template, persona)
                    print(f"   Question: {question}")
                    
                    # Check for duplicates
                    is_dup = generator.is_duplicate_question(question)
                    print(f"   Is duplicate: {is_dup}")
                    
                    if not is_dup:
                        # Create prompt
                        prompt = generator.create_qa_prompt(test_chunk, question, persona)
                        print(f"   Prompt length: {len(prompt)} chars")
                        
                        # Try API call
                        try:
                            answer, cost = await generator.call_llm_api(prompt)
                            print(f"   ✅ API call successful!")
                            print(f"   Answer: {answer[:100]}...")
                            print(f"   Cost: ${cost:.6f}")
                            
                            # Calculate confidence
                            confidence = generator.calculate_confidence(answer, test_chunk)
                            print(f"   Confidence: {confidence:.3f}")
                            
                            break  # Success, we can stop here
                            
                        except Exception as e:
                            print(f"   ❌ API call failed: {e}")
                            
                else:
                    print(f"   ❌ No templates found for {q_type}")
                    
            except Exception as e:
                print(f"   ❌ Error in iteration {i+1}: {e}")

if __name__ == "__main__":
    asyncio.run(test_step_by_step())
