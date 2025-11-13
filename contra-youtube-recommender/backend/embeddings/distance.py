"""
Distance and Similarity Calculations for Embeddings
"""
import numpy as np
from typing import List, Tuple
from sklearn.metrics.pairwise import cosine_similarity, cosine_distances
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DistanceCalculator:
    """Calculate distances and similarities between video embeddings"""

    @staticmethod
    def cosine_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity (1 = identical, 0 = orthogonal, -1 = opposite)
        """
        # Normalize vectors
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        return float(similarity)

    @staticmethod
    def cosine_distance(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine distance between two embeddings

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine distance (0 = identical, 1 = orthogonal, 2 = opposite)
        """
        similarity = DistanceCalculator.cosine_similarity(embedding1, embedding2)
        return 1.0 - similarity

    @staticmethod
    def euclidean_distance(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate Euclidean distance between two embeddings

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Euclidean distance
        """
        return float(np.linalg.norm(embedding1 - embedding2))

    @staticmethod
    def angle_between_vectors(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate angle in degrees between two embeddings

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Angle in degrees (0 = same direction, 180 = opposite direction)
        """
        similarity = DistanceCalculator.cosine_similarity(embedding1, embedding2)

        # Clamp to [-1, 1] to handle numerical errors
        similarity = np.clip(similarity, -1.0, 1.0)

        # Calculate angle in radians, then convert to degrees
        angle_rad = np.arccos(similarity)
        angle_deg = np.degrees(angle_rad)

        return float(angle_deg)

    @staticmethod
    def batch_cosine_similarity(embeddings1: np.ndarray, embeddings2: np.ndarray) -> np.ndarray:
        """
        Calculate pairwise cosine similarities between two sets of embeddings

        Args:
            embeddings1: Array of shape (n, d)
            embeddings2: Array of shape (m, d)

        Returns:
            Similarity matrix of shape (n, m)
        """
        return cosine_similarity(embeddings1, embeddings2)

    @staticmethod
    def batch_cosine_distance(embeddings1: np.ndarray, embeddings2: np.ndarray) -> np.ndarray:
        """
        Calculate pairwise cosine distances between two sets of embeddings

        Args:
            embeddings1: Array of shape (n, d)
            embeddings2: Array of shape (m, d)

        Returns:
            Distance matrix of shape (n, m)
        """
        return cosine_distances(embeddings1, embeddings2)

    @staticmethod
    def find_nearest_neighbors(
        query_embedding: np.ndarray,
        candidate_embeddings: np.ndarray,
        k: int = 10
    ) -> List[Tuple[int, float]]:
        """
        Find k nearest neighbors to query embedding

        Args:
            query_embedding: Query embedding of shape (d,)
            candidate_embeddings: Candidate embeddings of shape (n, d)
            k: Number of nearest neighbors to find

        Returns:
            List of (index, distance) tuples sorted by distance
        """
        # Calculate distances to all candidates
        distances = []
        for i, candidate in enumerate(candidate_embeddings):
            dist = DistanceCalculator.cosine_distance(query_embedding, candidate)
            distances.append((i, dist))

        # Sort by distance and return top k
        distances.sort(key=lambda x: x[1])
        return distances[:k]

    @staticmethod
    def find_farthest_neighbors(
        query_embedding: np.ndarray,
        candidate_embeddings: np.ndarray,
        k: int = 10
    ) -> List[Tuple[int, float]]:
        """
        Find k farthest neighbors to query embedding (most dissimilar)

        Args:
            query_embedding: Query embedding of shape (d,)
            candidate_embeddings: Candidate embeddings of shape (n, d)
            k: Number of farthest neighbors to find

        Returns:
            List of (index, distance) tuples sorted by distance (descending)
        """
        # Calculate distances to all candidates
        distances = []
        for i, candidate in enumerate(candidate_embeddings):
            dist = DistanceCalculator.cosine_distance(query_embedding, candidate)
            distances.append((i, dist))

        # Sort by distance (descending) and return top k
        distances.sort(key=lambda x: x[1], reverse=True)
        return distances[:k]

    @staticmethod
    def find_diametrically_opposite(
        query_embeddings: np.ndarray,
        candidate_embeddings: np.ndarray,
        k: int = 10,
        min_distance: float = 0.7,
        min_angle: float = 150.0
    ) -> List[Tuple[int, float, float]]:
        """
        Find videos that are diametrically opposite to query videos

        A video is considered "diametrically opposite" if:
        1. It has high cosine distance from all query videos
        2. The angle is close to 180 degrees (opposite direction)

        Args:
            query_embeddings: Query embeddings of shape (n, d)
            candidate_embeddings: Candidate embeddings of shape (m, d)
            k: Number of contra videos to find
            min_distance: Minimum cosine distance threshold (default: 0.7)
            min_angle: Minimum angle in degrees (default: 150°)

        Returns:
            List of (index, avg_distance, avg_angle) tuples for contra videos
        """
        contra_videos = []

        for i, candidate in enumerate(candidate_embeddings):
            distances = []
            angles = []

            # Calculate distance and angle to each query video
            for query in query_embeddings:
                dist = DistanceCalculator.cosine_distance(query, candidate)
                angle = DistanceCalculator.angle_between_vectors(query, candidate)

                distances.append(dist)
                angles.append(angle)

            # Calculate average distance and angle
            avg_distance = np.mean(distances)
            avg_angle = np.mean(angles)
            min_dist_to_any = np.min(distances)

            # Check if this candidate is "contra"
            # It should be far from ALL query videos (not just on average)
            if min_dist_to_any >= min_distance and avg_angle >= min_angle:
                contra_videos.append((i, avg_distance, avg_angle))

        # Sort by angle (descending) - we want the most opposite videos
        contra_videos.sort(key=lambda x: (x[2], x[1]), reverse=True)

        return contra_videos[:k]

    @staticmethod
    def calculate_centroid(embeddings: np.ndarray) -> np.ndarray:
        """
        Calculate the centroid (average) of a set of embeddings

        Args:
            embeddings: Array of shape (n, d)

        Returns:
            Centroid embedding of shape (d,)
        """
        return np.mean(embeddings, axis=0)

    @staticmethod
    def find_opposite_to_centroid(
        query_embeddings: np.ndarray,
        candidate_embeddings: np.ndarray,
        k: int = 10
    ) -> List[Tuple[int, float, float]]:
        """
        Find videos opposite to the centroid of query videos

        This is an alternative approach: find the center point of all query videos,
        then find candidates that are opposite to that center point.

        Args:
            query_embeddings: Query embeddings of shape (n, d)
            candidate_embeddings: Candidate embeddings of shape (m, d)
            k: Number of contra videos to find

        Returns:
            List of (index, distance, angle) tuples
        """
        # Calculate centroid of query videos
        centroid = DistanceCalculator.calculate_centroid(query_embeddings)

        # Find candidates opposite to centroid
        results = []
        for i, candidate in enumerate(candidate_embeddings):
            dist = DistanceCalculator.cosine_distance(centroid, candidate)
            angle = DistanceCalculator.angle_between_vectors(centroid, candidate)
            results.append((i, dist, angle))

        # Sort by angle (descending)
        results.sort(key=lambda x: x[2], reverse=True)

        return results[:k]
