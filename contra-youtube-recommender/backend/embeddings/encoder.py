"""
Text Embedding using Sentence Transformers
"""
import os
from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoEmbedder:
    """Generate embeddings for video metadata using sentence transformers"""

    def __init__(self, model_name: str = None):
        """
        Initialize the video embedder

        Args:
            model_name: Name of the sentence transformer model
                       Default: sentence-transformers/all-MiniLM-L6-v2
        """
        if model_name is None:
            model_name = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')

        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Model loaded. Embedding dimension: {self.embedding_dimension}")

    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text

        Args:
            text: Input text

        Returns:
            Numpy array of shape (embedding_dimension,)
        """
        if not text or not text.strip():
            # Return zero vector for empty text
            return np.zeros(self.embedding_dimension)

        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding

    def embed_texts(self, texts: List[str], batch_size: int = 32, show_progress: bool = True) -> np.ndarray:
        """
        Generate embeddings for multiple texts (batched for efficiency)

        Args:
            texts: List of input texts
            batch_size: Batch size for encoding
            show_progress: Whether to show progress bar

        Returns:
            Numpy array of shape (num_texts, embedding_dimension)
        """
        if not texts:
            return np.array([])

        # Replace empty texts with a space to avoid errors
        texts = [text if text and text.strip() else " " for text in texts]

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )

        return embeddings

    def embed_videos(self, videos_metadata: List[dict]) -> np.ndarray:
        """
        Generate embeddings for multiple videos using their metadata

        Args:
            videos_metadata: List of video metadata dictionaries
                            Each should have 'embedding_text' field

        Returns:
            Numpy array of shape (num_videos, embedding_dimension)
        """
        texts = [video.get('embedding_text', '') for video in videos_metadata]
        return self.embed_texts(texts)

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this model"""
        return self.embedding_dimension


class EmbeddingCache:
    """Simple in-memory cache for embeddings to avoid recomputation"""

    def __init__(self):
        self.cache = {}

    def get(self, key: str) -> Union[np.ndarray, None]:
        """Get embedding from cache"""
        return self.cache.get(key)

    def set(self, key: str, embedding: np.ndarray):
        """Store embedding in cache"""
        self.cache[key] = embedding

    def has(self, key: str) -> bool:
        """Check if key exists in cache"""
        return key in self.cache

    def clear(self):
        """Clear all cached embeddings"""
        self.cache.clear()

    def size(self) -> int:
        """Get number of cached embeddings"""
        return len(self.cache)


class CachedVideoEmbedder(VideoEmbedder):
    """Video embedder with caching support"""

    def __init__(self, model_name: str = None):
        super().__init__(model_name)
        self.cache = EmbeddingCache()

    def embed_text(self, text: str) -> np.ndarray:
        """Embed text with caching"""
        if self.cache.has(text):
            return self.cache.get(text)

        embedding = super().embed_text(text)
        self.cache.set(text, embedding)
        return embedding

    def embed_videos(self, videos_metadata: List[dict]) -> np.ndarray:
        """
        Embed videos with caching based on video_id

        Args:
            videos_metadata: List of video metadata dictionaries

        Returns:
            Numpy array of embeddings
        """
        embeddings = []

        for video in videos_metadata:
            video_id = video.get('video_id', '')
            text = video.get('embedding_text', '')

            # Use video_id as cache key
            cache_key = f"video:{video_id}"

            if self.cache.has(cache_key):
                embedding = self.cache.get(cache_key)
            else:
                embedding = self.embed_text(text)
                self.cache.set(cache_key, embedding)

            embeddings.append(embedding)

        return np.array(embeddings)

    def clear_cache(self):
        """Clear the embedding cache"""
        self.cache.clear()

    def cache_size(self) -> int:
        """Get the number of cached embeddings"""
        return self.cache.size()
