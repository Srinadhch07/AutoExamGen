# embeddings.py

from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(text: str):
    return model.encode(text, normalize_embeddings=True)

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2)