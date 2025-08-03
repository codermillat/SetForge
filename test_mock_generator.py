#!/usr/bin/env python3
"""
Mock generator for testing SetForge functionality
"""

import asyncio
import random
from pathlib import Path
from main_generator import SetForgeGenerator, GenerationConfig, QuestionType, StudentPersona, QAPair

class MockSetForgeGenerator(SetForgeGenerator):
    """Mock generator that simulates API calls for testing."""
    
    async def call_llm_api(self, prompt: str):
        """Mock API call that returns a simulated answer."""
        await asyncio.sleep(0.1)  # Simulate API delay
        
        # Generate a mock answer based on the prompt content
        if "scholarship" in prompt.lower():
            answer = "Based on the provided information, Bangladeshi students can apply for scholarships with GPA requirements ranging from 3.0 to 5.0. Level 1 scholarships (20% tuition reduction) are available for students with GPA 3.0-3.4, while Level 2 scholarships (50% tuition reduction) are for students with GPA 3.5-5.0."
        elif "admission" in prompt.lower():
            answer = "For Bangladeshi students seeking admission to Indian universities, the typical requirements include HSC/SSC certificates, CGPA conversion to Indian standards, and meeting specific program requirements. The admission process usually involves document verification and may require entrance exams."
        elif "fee" in prompt.lower():
            answer = "The fees for Bangladeshi students at Indian universities vary by program. Typical costs include tuition fees, accommodation, and living expenses. Many universities offer payment plans and scholarship opportunities to make education more affordable."
        else:
            answer = "Based on the provided information, this guidance is specifically designed for Bangladeshi students considering Indian universities. The information covers various aspects of the admission and study process."
        
        # Simulate cost (very small)
        cost = 0.0001
        self.total_cost += cost
        
        return answer, cost

async def test_mock_generation():
    """Test the generator with mock API calls."""
    print("🧪 Testing SetForge with Mock API...")
    
    config = GenerationConfig(
        target_pairs=5,
        max_cost_usd=1.0,
        api_key="mock-key",
        api_url='mock-url',
        model='mock-model',
        max_tokens=200,
        temperature=0.7,
        batch_size=1
    )
    
    async with MockSetForgeGenerator(config) as generator:
        print("✅ Mock Generator initialized")
        
        # Test with one file
        data_dir = Path("data/educational")
        files = list(data_dir.glob("*.txt"))
        test_file = files[0]
        
        print(f"📄 Testing with file: {test_file.name}")
        
        pairs = await generator.process_file(test_file)
        print(f"✅ Generated {len(pairs)} pairs")
        
        for i, pair in enumerate(pairs[:3]):  # Show first 3 pairs
            print(f"\n📝 Pair {i+1}:")
            print(f"Q: {pair.question}")
            print(f"A: {pair.answer[:100]}...")
            print(f"Type: {pair.question_type}")
            print(f"Persona: {pair.persona}")
            print(f"Confidence: {pair.confidence:.3f}")
            print(f"Cost: ${pair.cost:.6f}")

if __name__ == "__main__":
    asyncio.run(test_mock_generation())
