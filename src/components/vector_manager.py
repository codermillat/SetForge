import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List

class VectorManager:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.index = None

    def create_index(self, texts: List[str]):
        embeddings = self.model.encode(texts, convert_to_tensor=True)
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings.cpu().detach().numpy())

    def search(self, query: str, k: int = 5) -> List[int]:
        if self.index is None:
            raise ValueError("Index has not been created yet.")
        query_embedding = self.model.encode([query], convert_to_tensor=True)
        _, indices = self.index.search(query_embedding.cpu().detach().numpy(), k)
        return indices[0]
