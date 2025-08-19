#!/usr/bin/env python3
"""
SetForge Semantic Segmenter
===========================

This module breaks down documents into semantically coherent chunks.
"""

import logging
import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer

logger = logging.getLogger("SetForge")

class SemanticSegmenter:
    """
    Segments text based on semantic similarity of sentences.
    """

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', threshold: float = 0.45):
        """
        Initializes the SemanticSegmenter.

        Args:
            model_name: The name of the sentence-transformer model to use.
            threshold: The similarity threshold for splitting segments.
        """
        self.model = SentenceTransformer(model_name)
        self.threshold = threshold

    def segment(self, text: str) -> List[str]:
        """
        Segments a block of text into semantically coherent chunks.

        Args:
            text: The text to be segmented.

        Returns:
            A list of text segments.
        """
        try:
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            if not sentences:
                return []

            embeddings = self.model.encode(sentences, convert_to_tensor=True).cpu()
            
            # Calculate cosine similarity between adjacent sentences
            similarities = []
            for i in range(len(embeddings) - 1):
                # Ensure tensors are converted to numpy for the operation
                emb1 = embeddings[i].numpy()
                emb2 = embeddings[i+1].numpy()
                sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
                similarities.append(sim)

            segments = []
            current_segment = [sentences[0]]
            for i, similarity in enumerate(similarities):
                if similarity < self.threshold:
                    segments.append(" ".join(current_segment))
                    current_segment = [sentences[i+1]]
                else:
                    current_segment.append(sentences[i+1])
            
            segments.append(" ".join(current_segment)) # Add the last segment
            
            return segments

        except Exception as e:
            logger.error(f"Error during semantic segmentation: {e}", exc_info=True)
            return [text] # Fallback to returning the whole text as one segment
