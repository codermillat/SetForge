#!/usr/bin/env python3
"""
SetForge Local RAG Generator
============================

This module provides a completely offline, persistent, and scalable RAG
(Retrieval-Augmented Generation) system using FAISS for vector search and
Sentence-Transformers for embeddings.
"""

import faiss
import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional, Any, cast
import logging

from src.utils.config_manager import ConfigManager

logger = logging.getLogger("SetForge")

class LocalRAGGenerator:
    """
    Manages a local, persistent FAISS-based RAG pipeline.
    """

    def __init__(self, config: ConfigManager, force_rebuild: bool = False):
        """
        Initializes the LocalRAGGenerator.

        Args:
            config: The main configuration object.
            force_rebuild: If True, forces the index to be rebuilt even if it exists.
        """
        self.config = config
        self.index_path = Path(self.config.output_config.checkpoint_dir) / "faiss_index.bin"
        self.doc_map_path = Path(self.config.output_config.checkpoint_dir) / "document_map.json"
        self.model: Any = SentenceTransformer('all-MiniLM-L6-v2')
        self.index: Optional[Any] = None
        self.document_map: List[Dict[str, Any]] = []

        if not force_rebuild and self.index_path.exists() and self.doc_map_path.exists():
            logger.info("🚀 Loading existing FAISS index and document map...")
            self._load_index()
        else:
            logger.info("🛠️ Building new FAISS index from scratch...")
            self._build_index()

    def _load_index(self) -> None:
        """Loads the FAISS index and document map from disk."""
        try:
            self.index = faiss.read_index(str(self.index_path))
            with open(self.doc_map_path, 'r', encoding='utf-8') as f:
                self.document_map = json.load(f)
            if self.index:
                logger.info(f"✅ Successfully loaded index with {self.index.ntotal} vectors.")
        except Exception as e:
            logger.error(f"❌ Failed to load index: {e}. Rebuilding...", exc_info=True)
            self._build_index()

    def _build_index(self) -> None:
        """Builds the FAISS index from documents in the cleaned_data directory."""
        cleaned_data_dir = Path(self.config.data_config.cleaned_dir)
        if not cleaned_data_dir.exists():
            logger.error(f"❌ Cleaned data directory not found at: {cleaned_data_dir}")
            return

        logger.info("📂 Reading documents from cleaned data directory...")
        filepaths = list(cleaned_data_dir.rglob("*.txt"))
        if not filepaths:
            logger.warning("⚠️ No text files found in cleaned data directory. Index will be empty.")
            return
            
        logger.info(f"Found {len(filepaths)} documents to index.")
        
        all_chunks = []
        self.document_map = []

        for path in filepaths:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                chunks = self._chunk_text(content)
                for i, chunk in enumerate(chunks):
                    all_chunks.append(chunk)
                    self.document_map.append({"source": str(path), "chunk_id": i, "text": chunk})
            except Exception as e:
                logger.warning(f"Could not process file {path}: {e}")

        if not all_chunks:
            logger.warning("⚠️ No content chunks to index.")
            return

        logger.info(f"🧠 Generating embeddings for {len(all_chunks)} chunks...")
        embeddings: np.ndarray[Any, Any] = self.model.encode(all_chunks, show_progress_bar=True, convert_to_numpy=True)
        
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32'))

        if self.index:
            logger.info(f"✅ Index built with {self.index.ntotal} vectors.")
        self._save_index()

    def _save_index(self) -> None:
        """Saves the FAISS index and document map to disk."""
        if self.index is None:
            logger.error("Cannot save a null index.")
            return
        logger.info("💾 Saving FAISS index and document map...")
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.index_path))
        with open(self.doc_map_path, 'w', encoding='utf-8') as f:
            json.dump(self.document_map, f)
        logger.info("✅ Index saved successfully.")

    def _chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """Splits text into overlapping chunks."""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunks.append(" ".join(words[i:i + chunk_size]))
        return chunks

    def retrieve_context(self, query: str, k: int = 5) -> Optional[str]:
        """
        Retrieves the most relevant context for a given query.

        Args:
            query: The input question or text.
            k: The number of top chunks to retrieve.

        Returns:
            A combined string of the most relevant context chunks, or None.
        """
        if not self.index:
            logger.warning("⚠️ Index is not built or loaded. Cannot retrieve context.")
            return None
            
        logger.info(f"🔍 Searching for context for query: '{query[:50]}...'")
        query_embedding: np.ndarray[Any, Any] = self.model.encode([query]).astype('float32')
        distances, indices = self.index.search(query_embedding, k)

        retrieved_chunks: List[str] = [self.document_map[i]['text'] for i in indices[0]]
        
        combined_context = "\n\n---\n\n".join(retrieved_chunks)
        logger.info(f"✅ Retrieved {len(retrieved_chunks)} context chunks.")
        
        return combined_context

def create_local_rag_generator(config: ConfigManager, force_rebuild: bool = False) -> "LocalRAGGenerator":
    """Factory function to create a LocalRAGGenerator instance."""
    return LocalRAGGenerator(config, force_rebuild)
