"""
Contra Feed Algorithm

This module implements the core algorithm for finding "contra" videos -
videos that are diametrically opposite in viewpoint/perspective to
a given set of videos.
"""
import os
import json
from typing import List, Dict, Tuple, Optional
import logging
from pathlib import Path
import numpy as np

from ..youtube.api_client import YouTubeAPIClient
from ..youtube.sampler import RandomPrefixSampler
from ..youtube.metadata import MetadataProcessor
from ..embeddings.encoder import CachedVideoEmbedder
from ..embeddings.distance import DistanceCalculator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContraFeedGenerator:
    """
    Main class for generating contra feeds

    This implements the full pipeline:
    1. Get metadata for input videos (user's feed)
    2. Get random sample of YouTube videos
    3. Embed all videos
    4. Find diametrically opposite videos
    5. Return contra feed recommendations
    """

    def __init__(
        self,
        api_client: YouTubeAPIClient,
        embedder: Optional[CachedVideoEmbedder] = None,
        cache_dir: str = "data/random_samples"
    ):
        """
        Initialize the contra feed generator

        Args:
            api_client: YouTube API client
            embedder: Video embedder (creates one if not provided)
            cache_dir: Directory for caching random samples
        """
        self.api_client = api_client
        self.embedder = embedder or CachedVideoEmbedder()
        self.sampler = RandomPrefixSampler(api_client)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Algorithm parameters (can be configured)
        self.min_distance = float(os.getenv('MIN_DISTANCE_THRESHOLD', '0.7'))
        self.min_angle = float(os.getenv('ANGLE_THRESHOLD', '150.0'))

    def get_or_create_random_sample(
        self,
        sample_size: int = 1000,
        use_cache: bool = True
    ) -> List[Dict]:
        """
        Get or create a random sample of YouTube videos

        Args:
            sample_size: Number of videos to sample
            use_cache: Whether to use cached sample if available

        Returns:
            List of video metadata dictionaries
        """
        cache_file = self.cache_dir / f"random_sample_{sample_size}.json"

        # Try to load from cache
        if use_cache and cache_file.exists():
            logger.info(f"Loading random sample from cache: {cache_file}")
            with open(cache_file, 'r') as f:
                return json.load(f)

        # Generate new sample
        logger.info(f"Generating new random sample of {sample_size} videos")
        video_ids = self.sampler.get_diverse_sample(target_size=sample_size)

        logger.info(f"Fetching metadata for {len(video_ids)} videos")
        videos_metadata = self.api_client.get_videos_metadata(video_ids)

        # Enrich metadata
        videos_metadata = MetadataProcessor.batch_enrich_metadata(videos_metadata)

        # Save to cache
        logger.info(f"Saving random sample to cache: {cache_file}")
        with open(cache_file, 'w') as f:
            json.dump(videos_metadata, f, indent=2)

        return videos_metadata

    def generate_contra_feed(
        self,
        input_video_ids: List[str],
        num_contra_videos: int = 20,
        random_sample_size: int = 1000,
        use_cache: bool = True,
        method: str = 'diametric'
    ) -> List[Dict]:
        """
        Generate a contra feed for given input videos

        Args:
            input_video_ids: List of video IDs representing user's current feed
            num_contra_videos: Number of contra videos to return
            random_sample_size: Size of random sample to search from
            use_cache: Whether to use cached random sample
            method: Algorithm method ('diametric' or 'centroid')

        Returns:
            List of contra video metadata with scores
        """
        logger.info(f"Generating contra feed for {len(input_video_ids)} input videos")

        # Step 1: Get metadata for input videos
        logger.info("Step 1: Fetching metadata for input videos")
        input_metadata = self.api_client.get_videos_metadata(input_video_ids)
        input_metadata = MetadataProcessor.batch_enrich_metadata(input_metadata)
        logger.info(f"Got metadata for {len(input_metadata)} input videos")

        # Step 2: Get random sample of YouTube videos
        logger.info("Step 2: Getting random sample of YouTube videos")
        random_sample = self.get_or_create_random_sample(
            sample_size=random_sample_size,
            use_cache=use_cache
        )
        logger.info(f"Got {len(random_sample)} videos in random sample")

        # Step 3: Generate embeddings
        logger.info("Step 3: Generating embeddings")
        input_embeddings = self.embedder.embed_videos(input_metadata)
        sample_embeddings = self.embedder.embed_videos(random_sample)
        logger.info(f"Generated embeddings: {input_embeddings.shape}, {sample_embeddings.shape}")

        # Step 4: Find contra videos
        logger.info(f"Step 4: Finding contra videos using method '{method}'")
        if method == 'diametric':
            contra_results = DistanceCalculator.find_diametrically_opposite(
                query_embeddings=input_embeddings,
                candidate_embeddings=sample_embeddings,
                k=num_contra_videos,
                min_distance=self.min_distance,
                min_angle=self.min_angle
            )
        elif method == 'centroid':
            contra_results = DistanceCalculator.find_opposite_to_centroid(
                query_embeddings=input_embeddings,
                candidate_embeddings=sample_embeddings,
                k=num_contra_videos
            )
        else:
            raise ValueError(f"Unknown method: {method}")

        # Step 5: Prepare results
        logger.info(f"Step 5: Preparing {len(contra_results)} contra video results")
        contra_videos = []
        for idx, avg_distance, avg_angle in contra_results:
            video = random_sample[idx].copy()
            video['contra_score'] = {
                'distance': float(avg_distance),
                'angle': float(avg_angle),
                'method': method
            }
            contra_videos.append(video)

        logger.info(f"Contra feed generation complete: {len(contra_videos)} videos")
        return contra_videos

    def analyze_single_video(
        self,
        video_id: str,
        num_contra_videos: int = 20,
        random_sample_size: int = 1000,
        use_cache: bool = True
    ) -> Dict:
        """
        Analyze a single video and find contra videos

        Args:
            video_id: YouTube video ID
            num_contra_videos: Number of contra videos to find
            random_sample_size: Size of random sample
            use_cache: Whether to use cached sample

        Returns:
            Dictionary with input video info and contra videos
        """
        logger.info(f"Analyzing single video: {video_id}")

        # Get metadata for input video
        input_metadata = self.api_client.get_video_metadata(video_id)
        if not input_metadata:
            raise ValueError(f"Could not fetch metadata for video: {video_id}")

        input_metadata = MetadataProcessor.enrich_metadata(input_metadata)

        # Generate contra feed
        contra_videos = self.generate_contra_feed(
            input_video_ids=[video_id],
            num_contra_videos=num_contra_videos,
            random_sample_size=random_sample_size,
            use_cache=use_cache
        )

        return {
            'input_video': input_metadata,
            'contra_videos': contra_videos,
            'summary': {
                'input_video_id': video_id,
                'input_video_title': input_metadata['title'],
                'num_contra_videos': len(contra_videos),
                'avg_distance': np.mean([v['contra_score']['distance'] for v in contra_videos]),
                'avg_angle': np.mean([v['contra_score']['angle'] for v in contra_videos]),
            }
        }

    def compare_videos(
        self,
        video_id_1: str,
        video_id_2: str
    ) -> Dict:
        """
        Compare two videos and analyze their similarity/opposition

        Args:
            video_id_1: First video ID
            video_id_2: Second video ID

        Returns:
            Dictionary with comparison metrics
        """
        logger.info(f"Comparing videos: {video_id_1} vs {video_id_2}")

        # Get metadata
        metadata1 = self.api_client.get_video_metadata(video_id_1)
        metadata2 = self.api_client.get_video_metadata(video_id_2)

        if not metadata1 or not metadata2:
            raise ValueError("Could not fetch metadata for one or both videos")

        metadata1 = MetadataProcessor.enrich_metadata(metadata1)
        metadata2 = MetadataProcessor.enrich_metadata(metadata2)

        # Generate embeddings
        emb1 = self.embedder.embed_text(metadata1['embedding_text'])
        emb2 = self.embedder.embed_text(metadata2['embedding_text'])

        # Calculate metrics
        similarity = DistanceCalculator.cosine_similarity(emb1, emb2)
        distance = DistanceCalculator.cosine_distance(emb1, emb2)
        angle = DistanceCalculator.angle_between_vectors(emb1, emb2)
        euclidean = DistanceCalculator.euclidean_distance(emb1, emb2)

        # Determine relationship
        if angle < 30:
            relationship = "very_similar"
        elif angle < 60:
            relationship = "similar"
        elif angle < 120:
            relationship = "different"
        elif angle < 150:
            relationship = "opposite"
        else:
            relationship = "diametrically_opposite"

        return {
            'video_1': metadata1,
            'video_2': metadata2,
            'comparison': {
                'cosine_similarity': float(similarity),
                'cosine_distance': float(distance),
                'angle_degrees': float(angle),
                'euclidean_distance': float(euclidean),
                'relationship': relationship
            }
        }

    def get_statistics(self) -> Dict:
        """
        Get statistics about the contra feed generator

        Returns:
            Dictionary with statistics
        """
        return {
            'cache_dir': str(self.cache_dir),
            'cache_size': len(list(self.cache_dir.glob('*.json'))),
            'embedder_cache_size': self.embedder.cache_size(),
            'parameters': {
                'min_distance': self.min_distance,
                'min_angle': self.min_angle,
            }
        }
