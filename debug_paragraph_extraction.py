#!/usr/bin/env python3
"""
Debug script to check paragraph extraction
"""

import re
from pathlib import Path

def _extract_paragraphs(content: str):
    """Extract meaningful paragraphs from text content."""
    
    # Split by sections and headers
    sections = re.split(r'\n\s*#{1,3}\s+', content)
    
    paragraphs = []
    
    for section in sections:
        # Split section into paragraphs
        section_paragraphs = re.split(r'\n\s*\n', section.strip())
        
        for para in section_paragraphs:
            # Clean up paragraph
            cleaned_para = re.sub(r'\n+', ' ', para.strip())
            cleaned_para = re.sub(r'\s+', ' ', cleaned_para)
            
            # Skip if too short or just headers
            if len(cleaned_para) < 50 or re.match(r'^#+\s', cleaned_para):
                continue
            
            paragraphs.append(cleaned_para)
    
    return paragraphs

def _is_administrative_text(text: str) -> bool:
    """Check if text is administrative/boilerplate."""
    administrative_patterns = [
        r'source:', r'updated:', r'contact information',
        r'table of contents', r'index', r'references',
        r'appendix', r'copyright', r'disclaimer'
    ]
    
    text_lower = text.lower()
    return any(re.search(pattern, text_lower) for pattern in administrative_patterns)

# Test with one file
test_file = Path("data/educational/fees_scholarship_btech.txt")

if test_file.exists():
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"File: {test_file.name}")
    print(f"Content length: {len(content)} characters")
    
    paragraphs = _extract_paragraphs(content)
    print(f"Found {len(paragraphs)} paragraphs:")
    
    for i, paragraph in enumerate(paragraphs):
        print(f"\nParagraph {i+1} (length: {len(paragraph)}):")
        print(f"Administrative: {_is_administrative_text(paragraph)}")
        print(f"Preview: {paragraph[:200]}...")
        
        # Check final filter
        if len(paragraph) >= 100 and not _is_administrative_text(paragraph):
            print("✅ WOULD BE PROCESSED")
        else:
            print("❌ WOULD BE FILTERED OUT")
            print(f"   Length check: {len(paragraph) >= 100}")
            print(f"   Admin check: {not _is_administrative_text(paragraph)}")
else:
    print(f"File not found: {test_file}")
