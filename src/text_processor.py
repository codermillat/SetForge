"""
Text processing module for SetForge.

Handles intelligent text chunking with structure preservation,
optimized for educational content and cost-effective processing.
"""

import re
import hashlib
import logging
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass

from config import Config


@dataclass
class TextChunk:
    """Represents a processed text chunk with metadata."""
    id: str
    file_path: str
    content: str
    start_pos: int
    end_pos: int
    section_title: Optional[str] = None
    chunk_type: str = "content"  # content, header, list, etc.
    word_count: int = 0
    char_count: int = 0
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        self.word_count = len(self.content.split())
        self.char_count = len(self.content)


class TextProcessor:
    """Advanced text processor with intelligent chunking strategies."""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Compile regex patterns for efficiency
        self._header_pattern = re.compile(
            r'^(#{1,6})\s+(.+)$', 
            re.MULTILINE
        )
        self._section_pattern = re.compile(
            r'\n(#{1,6})\s+(.+)\n', 
            re.MULTILINE
        )
        self._paragraph_pattern = re.compile(r'\n\s*\n')
        self._list_pattern = re.compile(r'^[\s]*[-*+]\s+(.+)$', re.MULTILINE)
        self._numbered_list_pattern = re.compile(r'^[\s]*\d+\.\s+(.+)$', re.MULTILINE)
        
    async def process_file(self, file_path: Path) -> List[TextChunk]:
        """
        Process a single text file into optimized chunks.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            List of TextChunk objects
        """
        self.logger.info(f"Processing file: {file_path}")
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                self.logger.warning(f"Empty file: {file_path}")
                return []
            
            # Normalize content
            content = self._normalize_text(content)
            
            # Extract structure information
            structure = self._analyze_structure(content)
            
            # Generate chunks based on strategy
            if self.config.chunking.chunk_by_sections and structure['has_sections']:
                chunks = self._chunk_by_sections(content, file_path, structure)
            else:
                chunks = self._chunk_by_paragraphs(content, file_path)
            
            # Add micro-chunks for finer-grained QA generation
            if getattr(self.config.chunking, 'enable_micro_chunks', False):
                micro_chunks = self._create_micro_chunks(content, file_path)
                chunks.extend(micro_chunks)
                self.logger.info(f"Added {len(micro_chunks)} micro-chunks for enhanced QA generation")
            
            # Post-process chunks
            chunks = self._post_process_chunks(chunks)
            
            # Optimize chunks for performance (but preserve more chunks for QA volume)
            if not getattr(self.config.chunking, 'enable_micro_chunks', False):
                chunks = self._optimize_chunks(chunks)
            
            self.logger.info(f"Created {len(chunks)} total chunks from {file_path}")
            return chunks
            
        except Exception as e:
            self.logger.error(f"Failed to process {file_path}: {e}")
            raise
    
    def _normalize_text(self, content: str) -> str:
        """Normalize text content for consistent processing."""
        # Remove excessive whitespace while preserving structure
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        
        # Normalize line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # Clean up common markdown issues
        content = re.sub(r'#+\s*$', '', content, flags=re.MULTILINE)
        
        return content.strip()
    
    def _optimize_chunks(self, chunks: List[TextChunk]) -> List[TextChunk]:
        """Optimize chunks for better API efficiency while maintaining quality."""
        if not chunks:
            return chunks
        
        optimized_chunks = []
        current_chunk = None
        
        for chunk in chunks:
            # Skip very small chunks that won't produce quality QA pairs
            if chunk.char_count < self.config.chunking.min_chunk_size // 2:
                continue
            
            # If we can merge small chunks without exceeding limits
            if (current_chunk and 
                current_chunk.char_count + chunk.char_count < self.config.chunking.max_chunk_size * 0.8 and
                current_chunk.section_title == chunk.section_title):
                
                # Merge chunks
                merged_content = current_chunk.content + "\n\n" + chunk.content
                current_chunk = TextChunk(
                    id=f"{current_chunk.id}_merged",
                    file_path=current_chunk.file_path,
                    content=merged_content,
                    start_pos=current_chunk.start_pos,
                    end_pos=chunk.end_pos,
                    section_title=current_chunk.section_title,
                    chunk_type="merged",
                    word_count=len(merged_content.split()),
                    char_count=len(merged_content),
                    metadata={
                        **current_chunk.metadata,
                        "merged_from": [current_chunk.id, chunk.id],
                        "optimization": "merged_for_efficiency"
                    }
                )
            else:
                # Add current chunk to optimized list
                if current_chunk:
                    optimized_chunks.append(current_chunk)
                current_chunk = chunk
        
        # Add the last chunk
        if current_chunk:
            optimized_chunks.append(current_chunk)
        
        self.logger.debug(f"Optimized {len(chunks)} chunks to {len(optimized_chunks)} chunks")
        return optimized_chunks

    def _analyze_structure(self, content: str) -> Dict:
        """Analyze text structure to determine optimal chunking strategy."""
        structure = {
            'has_sections': False,
            'sections': [],
            'has_lists': False,
            'list_count': 0,
            'paragraph_count': 0,
            'word_count': len(content.split()),
            'char_count': len(content)
        }
        
        # Find markdown headers
        header_matches = list(self._header_pattern.finditer(content))
        if header_matches:
            structure['has_sections'] = True
            for match in header_matches:
                level = len(match.group(1))
                title = match.group(2).strip()
                structure['sections'].append({
                    'level': level,
                    'title': title,
                    'pos': match.start()
                })
        
        # Find lists
        list_patterns = [
            r'^\s*[-*+]\s+',  # Bullet lists
            r'^\s*\d+\.\s+',  # Numbered lists
            r'^\s*[a-zA-Z]\.\s+',  # Letter lists
            r'^\s*[ivx]+\.\s+',  # Roman numeral lists
        ]
        
        for pattern in list_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            if matches:
                structure['has_lists'] = True
                structure['list_count'] += len(matches)
        
        # Count paragraphs
        paragraphs = re.split(r'\n\s*\n', content.strip())
        structure['paragraph_count'] = len([p for p in paragraphs if p.strip()])
        
        return structure
    
    def _chunk_by_sections(self, content: str, file_path: Path, structure: Dict) -> List[TextChunk]:
        """Chunk content by markdown sections."""
        chunks = []
        sections = structure['sections']
        
        if not sections:
            return self._chunk_by_paragraphs(content, file_path)
        
        # Sort sections by position
        sections.sort(key=lambda x: x['pos'])
        
        for i, section in enumerate(sections):
            # Find section boundaries
            start_pos = section['pos']
            
            # Find end position (start of next section or end of content)
            if i + 1 < len(sections):
                end_pos = sections[i + 1]['pos']
            else:
                end_pos = len(content)
            
            # Extract section content
            section_content = content[start_pos:end_pos].strip()
            
            if not section_content:
                continue
            
            # Split large sections into smaller chunks
            if len(section_content) > self.config.chunking.max_chunk_size:
                sub_chunks = self._split_large_section(
                    section_content, file_path, section['title'], start_pos
                )
                chunks.extend(sub_chunks)
            else:
                # Create single chunk for section
                chunk_id = self._generate_chunk_id(file_path, start_pos)
                chunk = TextChunk(
                    id=chunk_id,
                    file_path=str(file_path),
                    content=section_content,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    section_title=section['title'],
                    chunk_type="section",
                    metadata={
                        'section_level': section['level'],
                        'section_index': i
                    }
                )
                chunks.append(chunk)
        
        return chunks
    
    def _chunk_by_paragraphs(self, content: str, file_path: Path) -> List[TextChunk]:
        """Chunk content by paragraphs when no clear sections exist."""
        chunks = []
        paragraphs = self._paragraph_pattern.split(content)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        current_chunk = ""
        current_start = 0
        chunk_index = 0
        
        for paragraph in paragraphs:
            # Check if adding this paragraph would exceed chunk size
            potential_chunk = current_chunk + "\n\n" + paragraph if current_chunk else paragraph
            
            if len(potential_chunk) > self.config.chunking.max_chunk_size and current_chunk:
                # Create chunk from current content
                if len(current_chunk) >= self.config.chunking.min_chunk_size:
                    chunk_id = self._generate_chunk_id(file_path, chunk_index)
                    chunk = TextChunk(
                        id=chunk_id,
                        file_path=str(file_path),
                        content=current_chunk,
                        start_pos=current_start,
                        end_pos=current_start + len(current_chunk),
                        chunk_type="paragraph_group",
                        metadata={'chunk_index': chunk_index}
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                
                # Start new chunk with overlap
                overlap = self._get_overlap_text(current_chunk)
                current_chunk = overlap + paragraph if overlap else paragraph
                current_start = current_start + len(current_chunk) - len(overlap) if overlap else current_start + len(current_chunk)
            else:
                # Add paragraph to current chunk
                current_chunk = potential_chunk
        
        # Add final chunk
        if current_chunk and len(current_chunk) >= self.config.chunking.min_chunk_size:
            chunk_id = self._generate_chunk_id(file_path, chunk_index)
            chunk = TextChunk(
                id=chunk_id,
                file_path=str(file_path),
                content=current_chunk,
                start_pos=current_start,
                end_pos=current_start + len(current_chunk),
                chunk_type="paragraph_group",
                metadata={'chunk_index': chunk_index}
            )
            chunks.append(chunk)
        
        return chunks
    
    def _split_large_section(self, section_content: str, file_path: Path, 
                           section_title: str, base_start_pos: int) -> List[TextChunk]:
        """Split a large section into smaller chunks."""
        chunks = []
        paragraphs = self._paragraph_pattern.split(section_content)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        current_chunk = ""
        current_start = base_start_pos
        sub_chunk_index = 0
        
        for paragraph in paragraphs:
            potential_chunk = current_chunk + "\n\n" + paragraph if current_chunk else paragraph
            
            if len(potential_chunk) > self.config.chunking.max_chunk_size and current_chunk:
                # Create sub-chunk
                if len(current_chunk) >= self.config.chunking.min_chunk_size:
                    chunk_id = self._generate_chunk_id(file_path, f"{base_start_pos}_{sub_chunk_index}")
                    chunk = TextChunk(
                        id=chunk_id,
                        file_path=str(file_path),
                        content=current_chunk,
                        start_pos=current_start,
                        end_pos=current_start + len(current_chunk),
                        section_title=section_title,
                        chunk_type="section_part",
                        metadata={
                            'sub_chunk_index': sub_chunk_index,
                            'parent_section': section_title
                        }
                    )
                    chunks.append(chunk)
                    sub_chunk_index += 1
                
                # Start new chunk with overlap
                overlap = self._get_overlap_text(current_chunk)
                current_chunk = overlap + paragraph if overlap else paragraph
                current_start = current_start + len(current_chunk) - len(overlap) if overlap else current_start + len(current_chunk)
            else:
                current_chunk = potential_chunk
        
        # Add final sub-chunk
        if current_chunk and len(current_chunk) >= self.config.chunking.min_chunk_size:
            chunk_id = self._generate_chunk_id(file_path, f"{base_start_pos}_{sub_chunk_index}")
            chunk = TextChunk(
                id=chunk_id,
                file_path=str(file_path),
                content=current_chunk,
                start_pos=current_start,
                end_pos=current_start + len(current_chunk),
                section_title=section_title,
                chunk_type="section_part",
                metadata={
                    'sub_chunk_index': sub_chunk_index,
                    'parent_section': section_title
                }
            )
            chunks.append(chunk)
        
        return chunks
    
    def _get_overlap_text(self, text: str) -> str:
        """Extract overlap text from the end of a chunk."""
        if len(text) <= self.config.chunking.overlap_size:
            return ""
        
        # Try to break at sentence boundary
        sentences = re.split(r'[.!?]+\s+', text)
        if len(sentences) > 1:
            # Take last complete sentence(s) that fit in overlap size
            overlap = ""
            for sentence in reversed(sentences[:-1]):  # Exclude empty last element
                if len(overlap + sentence) <= self.config.chunking.overlap_size:
                    overlap = sentence + ". " + overlap
                else:
                    break
            return overlap.strip()
        
        # Fallback to character-based overlap
        return text[-self.config.chunking.overlap_size:].strip()
    
    def _post_process_chunks(self, chunks: List[TextChunk]) -> List[TextChunk]:
        """Post-process chunks for quality and consistency."""
        processed_chunks = []
        
        for chunk in chunks:
            # Skip chunks that are too small
            if chunk.char_count < self.config.chunking.min_chunk_size:
                self.logger.debug(f"Skipping small chunk: {chunk.id} ({chunk.char_count} chars)")
                continue
            
            # Clean up chunk content
            chunk.content = self._clean_chunk_content(chunk.content)
            
            # Update word and character counts
            chunk.word_count = len(chunk.content.split())
            chunk.char_count = len(chunk.content)
            
            # Add processing metadata
            chunk.metadata.update({
                'processed_at': str(Path().absolute()),
                'processor_version': '1.0',
                'chunking_strategy': 'sections' if self.config.chunking.chunk_by_sections else 'paragraphs'
            })
            
            processed_chunks.append(chunk)
        
        return processed_chunks
    
    def _clean_chunk_content(self, content: str) -> str:
        """Clean and normalize chunk content."""
        # Remove extra whitespace
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        
        # Ensure proper sentence endings
        content = re.sub(r'([.!?])([A-Z])', r'\1 \2', content)
        
        # Clean up list formatting
        content = re.sub(r'\n\s*[-*+]\s+', '\n• ', content)
        
        return content.strip()
    
    def _generate_chunk_id(self, file_path, position: any) -> str:
        """Generate unique chunk ID."""
        if isinstance(file_path, str):
            file_path = Path(file_path)
        base_name = file_path.stem
        position_str = str(position)
        hash_input = f"{base_name}_{position_str}".encode('utf-8')
        hash_digest = hashlib.md5(hash_input).hexdigest()[:8]
        return f"{base_name}_{position_str}_{hash_digest}"

    def _create_micro_chunks(self, content: str, file_path: Path, section_title: str = None) -> List[TextChunk]:
        """Create very fine-grained chunks for maximum QA generation."""
        chunks = []
        
        # First, split by sentences
        if getattr(self.config.chunking, 'sentence_split', False):
            sentence_chunks = self._chunk_by_sentences(content, file_path, section_title)
            chunks.extend(sentence_chunks)
        
        # Then, split by bullet points and lists
        if getattr(self.config.chunking, 'bullet_split', False):
            bullet_chunks = self._chunk_by_bullets(content, file_path, section_title)
            chunks.extend(bullet_chunks)
        
        # Create overlapping micro-chunks for dense content
        if getattr(self.config.chunking, 'enable_micro_chunks', False):
            micro_chunks = self._create_overlapping_micro_chunks(content, file_path, section_title)
            chunks.extend(micro_chunks)
        
        return chunks

    def _chunk_by_sentences(self, content: str, file_path: Path, section_title: str = None) -> List[TextChunk]:
        """Split content into sentence-based chunks."""
        chunks = []
        
        # Split into sentences using multiple delimiters
        sentences = re.split(r'[.!?]+(?=\s+[A-Z]|\s*$)', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        max_sentences = getattr(self.config.chunking, 'max_sentences_per_chunk', 4)
        
        for i in range(0, len(sentences), max_sentences):
            sentence_group = sentences[i:i + max_sentences]
            chunk_content = '. '.join(sentence_group)
            
            if len(chunk_content.strip()) < getattr(self.config.chunking, 'min_chunk_size', 200):
                continue
                
            chunk_id = self._generate_chunk_id(file_path, f"sent_{i}")
            chunk = TextChunk(
                id=chunk_id,
                file_path=str(file_path),
                content=chunk_content,
                start_pos=i,
                end_pos=i + len(sentence_group),
                section_title=section_title,
                chunk_type="sentence_group",
                metadata={
                    'sentence_count': len(sentence_group),
                    'chunk_method': 'sentence_split'
                }
            )
            chunks.append(chunk)
        
        return chunks

    def _chunk_by_bullets(self, content: str, file_path: Path, section_title: str = None) -> List[TextChunk]:
        """Split content by bullet points and list items."""
        chunks = []
        
        # Find bullet point patterns
        bullet_pattern = r'(^|\n)\s*[•\-\*\+]\s+(.+?)(?=\n\s*[•\-\*\+]|\n\n|\n[A-Z]|\Z)'
        bullet_matches = re.finditer(bullet_pattern, content, re.MULTILINE | re.DOTALL)
        
        for i, match in enumerate(bullet_matches):
            bullet_content = match.group(2).strip()
            
            if len(bullet_content) < 50:  # Skip very short bullets
                continue
                
            # Add context from surrounding text if available
            start_context = max(0, match.start() - 200)
            end_context = min(len(content), match.end() + 200)
            context = content[start_context:match.start()].strip()
            
            if context:
                full_content = f"{context}\n\n• {bullet_content}"
            else:
                full_content = f"• {bullet_content}"
            
            chunk_id = self._generate_chunk_id(file_path, f"bullet_{i}")
            chunk = TextChunk(
                id=chunk_id,
                file_path=str(file_path),
                content=full_content,
                start_pos=match.start(),
                end_pos=match.end(),
                section_title=section_title,
                chunk_type="bullet_point",
                metadata={
                    'bullet_index': i,
                    'chunk_method': 'bullet_split',
                    'has_context': bool(context)
                }
            )
            chunks.append(chunk)
        
        return chunks

    def _create_overlapping_micro_chunks(self, content: str, file_path: Path, section_title: str = None) -> List[TextChunk]:
        """Create small overlapping chunks for dense QA generation."""
        chunks = []
        
        # Parameters for micro-chunking
        chunk_size = getattr(self.config.chunking, 'max_chunk_size', 800) // 2  # Half the normal size
        overlap = chunk_size // 3  # 33% overlap
        
        words = content.split()
        if len(words) < 20:  # Skip very short content
            return chunks
        
        # Calculate words per chunk (approximate)
        words_per_chunk = chunk_size // 5  # Rough estimate: 5 chars per word
        
        for i in range(0, len(words), words_per_chunk - overlap // 5):
            chunk_words = words[i:i + words_per_chunk]
            chunk_content = ' '.join(chunk_words)
            
            if len(chunk_content) < getattr(self.config.chunking, 'min_chunk_size', 200):
                continue
            
            chunk_id = self._generate_chunk_id(file_path, f"micro_{i}")
            chunk = TextChunk(
                id=chunk_id,
                file_path=str(file_path),
                content=chunk_content,
                start_pos=i,
                end_pos=i + len(chunk_words),
                section_title=section_title,
                chunk_type="micro_chunk",
                metadata={
                    'word_start': i,
                    'word_count': len(chunk_words),
                    'chunk_method': 'micro_overlapping',
                    'overlap_ratio': overlap / chunk_size
                }
            )
            chunks.append(chunk)
        
        return chunks
