#!/usr/bin/env python3
"""
Debug version with detailed logging
"""

import asyncio
import random
from pathlib import Path
from main_generator import SetForgeGenerator, GenerationConfig, QuestionType, StudentPersona

class DebugSetForgeGenerator(SetForgeGenerator):
    """Debug generator with detailed logging."""
    
    async def process_file(self, file_path: Path):
        """Debug version of process_file with detailed logging."""
        print(f"🔍 DEBUG: Starting process_file for {file_path.name}")
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"🔍 DEBUG: File read successfully, {len(content)} characters")
        except Exception as e:
            print(f"🔍 DEBUG: Failed to read file: {e}")
            return []
        
        # Split into chunks
        chunks = [chunk.strip() for chunk in content.split('\n\n') if chunk.strip()]
        print(f"🔍 DEBUG: Found {len(chunks)} chunks")
        
        # Filter chunks
        long_chunks = [chunk for chunk in chunks if len(chunk) >= 100]
        print(f"🔍 DEBUG: {len(long_chunks)} chunks >= 100 chars")
        
        pairs = []
        
        # Process first 5 chunks
        for chunk_idx, chunk in enumerate(chunks[:5]):
            print(f"🔍 DEBUG: Processing chunk {chunk_idx + 1}/5, length: {len(chunk)}")
            
            if len(chunk) < 100:
                print(f"🔍 DEBUG: Skipping chunk {chunk_idx + 1} (too short)")
                continue
            
            print(f"🔍 DEBUG: Chunk {chunk_idx + 1} passed length check")
            
            # Test question types
            q_types = list(QuestionType)
            print(f"🔍 DEBUG: Available question types: {[qt.value for qt in q_types]}")
            
            # Sample 2 question types
            try:
                sampled_q_types = random.sample(q_types, 2)
                print(f"🔍 DEBUG: Sampled question types: {[qt.value for qt in sampled_q_types]}")
            except Exception as e:
                print(f"🔍 DEBUG: Error sampling question types: {e}")
                continue
                
            for q_type in sampled_q_types:
                print(f"🔍 DEBUG: Processing question type: {q_type.value}")
                
                # Test personas
                personas = list(StudentPersona)
                print(f"🔍 DEBUG: Available personas: {[p.value for p in personas]}")
                
                try:
                    sampled_personas = random.sample(personas, 1)
                    print(f"🔍 DEBUG: Sampled persona: {[p.value for p in sampled_personas]}")
                except Exception as e:
                    print(f"🔍 DEBUG: Error sampling personas: {e}")
                    continue
                    
                for persona in sampled_personas:
                    print(f"🔍 DEBUG: Processing persona: {persona.value}")
                    
                    # Check templates
                    if q_type not in self.templates:
                        print(f"🔍 DEBUG: No templates for {q_type.value}")
                        continue
                        
                    templates = self.templates[q_type]
                    print(f"🔍 DEBUG: Found {len(templates)} templates for {q_type.value}")
                    
                    template = random.choice(templates)
                    print(f"🔍 DEBUG: Selected template: {template}")
                    
                    # Generate question
                    try:
                        question = self.generate_question_from_template(template, persona)
                        print(f"🔍 DEBUG: Generated question: {question}")
                    except Exception as e:
                        print(f"🔍 DEBUG: Error generating question: {e}")
                        continue
                    
                    # Check duplicates
                    is_dup = self.is_duplicate_question(question)
                    print(f"🔍 DEBUG: Is duplicate: {is_dup}")
                    
                    if is_dup:
                        print(f"🔍 DEBUG: Skipping duplicate question")
                        continue
                    
                    # Create prompt
                    try:
                        prompt = self.create_qa_prompt(chunk, question, persona)
                        print(f"🔍 DEBUG: Created prompt, length: {len(prompt)}")
                    except Exception as e:
                        print(f"🔍 DEBUG: Error creating prompt: {e}")
                        continue
                    
                    # Mock API call for testing
                    try:
                        answer = f"This is a mock answer for the question about {q_type.value} for Bangladeshi students."
                        cost = 0.001
                        self.total_cost += cost
                        print(f"🔍 DEBUG: Mock API call successful")
                    except Exception as e:
                        print(f"🔍 DEBUG: Error in API call: {e}")
                        continue
                    
                    # Calculate confidence
                    try:
                        confidence = self.calculate_confidence(answer, chunk)
                        print(f"🔍 DEBUG: Calculated confidence: {confidence}")
                    except Exception as e:
                        print(f"🔍 DEBUG: Error calculating confidence: {e}")
                        confidence = 0.5
                    
                    # Create QA pair
                    from main_generator import QAPair
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
                    print(f"🔍 DEBUG: Added QA pair, total pairs: {len(pairs)}")
                    
                    # Stop after first successful pair for testing
                    if len(pairs) >= 1:
                        print(f"🔍 DEBUG: Reached test limit, stopping")
                        return pairs
        
        print(f"🔍 DEBUG: Finished processing, total pairs: {len(pairs)}")
        return pairs

async def test_debug_generation():
    """Test with debug generator."""
    print("🧪 Testing with Debug Generator...")
    
    config = GenerationConfig(
        target_pairs=1,
        max_cost_usd=1.0,
        api_key="debug-key",
        api_url='debug-url',
        model='debug-model'
    )
    
    async with DebugSetForgeGenerator(config) as generator:
        print("✅ Debug Generator initialized")
        
        # Test with one file
        data_dir = Path("data/educational")
        files = list(data_dir.glob("*.txt"))
        test_file = files[0]
        
        pairs = await generator.process_file(test_file)
        print(f"\n✅ Final result: Generated {len(pairs)} pairs")
        
        for pair in pairs:
            print(f"\n📝 Generated Pair:")
            print(f"Q: {pair.question}")
            print(f"A: {pair.answer}")

if __name__ == "__main__":
    asyncio.run(test_debug_generation())
