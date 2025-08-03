#!/usr/bin/env python3
"""
Fixed version of the SetForge generator
"""

import asyncio
from pathlib import Path
from main_generator import SetForgeGenerator, GenerationConfig

class FixedSetForgeGenerator(SetForgeGenerator):
    """Fixed generator that processes long chunks first."""
    
    async def process_file(self, file_path: Path):
        """Fixed version that processes long chunks first."""
        print(f"🔧 FIXED: Processing {file_path.name}")
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Failed to read {file_path}: {e}")
            return []
        
        # Split into chunks and filter for long ones first
        all_chunks = [chunk.strip() for chunk in content.split('\n\n') if chunk.strip()]
        long_chunks = [chunk for chunk in all_chunks if len(chunk) >= 100]
        
        print(f"📊 Found {len(all_chunks)} total chunks, {len(long_chunks)} long chunks")
        
        if not long_chunks:
            print("❌ No chunks >= 100 characters found")
            return []
        
        # Use the parent's process_file logic but with filtered chunks
        # For now, let's manually implement the core logic
        pairs = []
        
        # Process up to 3 long chunks to stay within budget
        for chunk in long_chunks[:3]:
            print(f"🔧 Processing chunk ({len(chunk)} chars): {chunk[:50]}...")
            
            # Import the enums we need
            from main_generator import QuestionType, StudentPersona, QAPair
            import random
            
            # Generate 1 Q&A pair per chunk for testing
            q_type = random.choice(list(QuestionType))
            persona = random.choice(list(StudentPersona))
            
            # Get template
            if q_type in self.templates:
                template = random.choice(self.templates[q_type])
                question = self.generate_question_from_template(template, persona)
                
                # Check duplicates
                if self.is_duplicate_question(question):
                    continue
                
                # Create prompt
                prompt = self.create_qa_prompt(chunk, question, persona)
                
                # Mock API call for now
                answer = f"Based on the provided information for Bangladeshi students, this {q_type.value} question can be answered as follows: [Mock response for testing the generator logic]"
                cost = 0.001
                self.total_cost += cost
                
                # Calculate confidence
                confidence = self.calculate_confidence(answer, chunk)
                
                # Create QA pair
                qa_pair = QAPair(
                    question=question,
                    answer=answer,
                    context=chunk[:200] + "..." if len(chunk) > 200 else chunk,
                    persona=persona.value,
                    question_type=q_type.value,
                    university=self.extract_university(chunk),
                    confidence=confidence,
                    source_file=file_path.name,
                    cost=cost
                )
                
                pairs.append(qa_pair)
                print(f"✅ Generated pair {len(pairs)}: {question[:50]}...")
        
        print(f"🔧 FIXED: Generated {len(pairs)} pairs from {file_path.name}")
        return pairs

async def test_fixed_generation():
    """Test the fixed generator."""
    print("🔧 Testing Fixed SetForge Generator...")
    
    config = GenerationConfig(
        target_pairs=5,
        max_cost_usd=1.0,
        api_key="test-key",
        api_url='test-url',
        model='test-model'
    )
    
    async with FixedSetForgeGenerator(config) as generator:
        print("✅ Fixed Generator initialized")
        
        # Test with one file
        data_dir = Path("data/educational")
        files = list(data_dir.glob("*.txt"))
        test_file = files[0]
        
        pairs = await generator.process_file(test_file)
        print(f"\n🎉 SUCCESS: Generated {len(pairs)} pairs!")
        
        for i, pair in enumerate(pairs):
            print(f"\n📝 Pair {i+1}:")
            print(f"Q: {pair.question}")
            print(f"A: {pair.answer[:100]}...")
            print(f"Type: {pair.question_type} | Persona: {pair.persona}")
            print(f"Confidence: {pair.confidence:.3f} | Cost: ${pair.cost:.6f}")

if __name__ == "__main__":
    asyncio.run(test_fixed_generation())
