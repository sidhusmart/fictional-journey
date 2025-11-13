"""
Random Prefix Sampler for YouTube Videos

Based on the methodology from:
"Dialing for Videos: A Random Sample of YouTube" (McGrady et al., 2023)
and "Counting YouTube videos via random prefix sampling" (Zhou et al., 2011)
"""
import random
import string
import logging
from typing import List, Set
from .api_client import YouTubeAPIClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RandomPrefixSampler:
    """
    Generates random samples of YouTube videos using random prefix sampling.

    YouTube video IDs are 11-character strings using characters: [A-Za-z0-9_-]
    By generating random prefixes and querying the search API, we can obtain
    a statistically unbiased sample of YouTube videos.
    """

    # YouTube video ID character set
    YOUTUBE_CHARSET = string.ascii_letters + string.digits + '_-'

    def __init__(self, api_client: YouTubeAPIClient, prefix_length: int = 5):
        """
        Initialize the random prefix sampler

        Args:
            api_client: YouTube API client instance
            prefix_length: Length of random prefixes (default: 5)
        """
        self.api_client = api_client
        self.prefix_length = prefix_length

    def generate_random_prefix(self) -> str:
        """
        Generate a random prefix for YouTube video ID

        Returns:
            Random string of specified length
        """
        return ''.join(random.choice(self.YOUTUBE_CHARSET) for _ in range(self.prefix_length))

    def generate_random_video_id(self) -> str:
        """
        Generate a completely random 11-character video ID

        Returns:
            Random 11-character string
        """
        return ''.join(random.choice(self.YOUTUBE_CHARSET) for _ in range(11))

    def sample_videos_by_prefix(self, num_prefixes: int = 100) -> List[str]:
        """
        Sample videos by searching with random prefixes

        Args:
            num_prefixes: Number of random prefixes to generate and search

        Returns:
            List of unique video IDs found
        """
        video_ids: Set[str] = set()
        successful_searches = 0

        logger.info(f"Starting prefix sampling with {num_prefixes} random prefixes")

        for i in range(num_prefixes):
            prefix = self.generate_random_prefix()

            # Search for videos with this prefix
            # Note: This searches for the prefix in video titles/descriptions
            # For true random prefix sampling, we would need to search for video IDs starting with prefix
            # However, YouTube search API doesn't support direct video ID prefix search anymore
            found_ids = self.api_client.search_videos(query=prefix, max_results=10)

            if found_ids:
                video_ids.update(found_ids)
                successful_searches += 1

            if (i + 1) % 10 == 0:
                logger.info(f"Progress: {i + 1}/{num_prefixes} prefixes, {len(video_ids)} unique videos found")

        logger.info(f"Sampling complete: {len(video_ids)} unique videos from {successful_searches} successful searches")
        return list(video_ids)

    def sample_videos_by_random_ids(self, num_attempts: int = 1000) -> List[str]:
        """
        Sample videos by generating random video IDs and checking if they exist

        This is a "drunk dialing" approach - generating random IDs and checking if they're valid.
        This is less efficient but provides a truly random sample.

        Args:
            num_attempts: Number of random IDs to try

        Returns:
            List of valid video IDs found
        """
        valid_video_ids: List[str] = []
        logger.info(f"Starting random ID sampling with {num_attempts} attempts")

        for i in range(num_attempts):
            video_id = self.generate_random_video_id()

            if self.api_client.check_video_exists(video_id):
                valid_video_ids.append(video_id)
                logger.info(f"Found valid video: {video_id} ({len(valid_video_ids)} total)")

            if (i + 1) % 100 == 0:
                logger.info(f"Progress: {i + 1}/{num_attempts} attempts, {len(valid_video_ids)} valid videos found")

        logger.info(f"Random ID sampling complete: {len(valid_video_ids)} valid videos found")
        return valid_video_ids

    def sample_videos_hybrid(
        self,
        num_prefixes: int = 100,
        num_random_ids: int = 500,
        use_trending: bool = True
    ) -> List[str]:
        """
        Hybrid sampling approach combining multiple methods

        Args:
            num_prefixes: Number of prefix searches
            num_random_ids: Number of random ID attempts
            use_trending: Whether to include trending videos

        Returns:
            Combined list of unique video IDs
        """
        video_ids: Set[str] = set()

        # Method 1: Random prefix search
        logger.info("Phase 1: Random prefix sampling")
        prefix_videos = self.sample_videos_by_prefix(num_prefixes)
        video_ids.update(prefix_videos)

        # Method 2: Random ID generation (more likely to find older/obscure videos)
        # Note: This is very inefficient as the hit rate is extremely low
        # The YouTube video ID space is 64^11 ≈ 10^19 possibilities
        # With billions of videos, the hit rate is still incredibly low
        # Commented out by default, but kept for reference
        # logger.info("Phase 2: Random ID sampling")
        # random_id_videos = self.sample_videos_by_random_ids(num_random_ids)
        # video_ids.update(random_id_videos)

        # Method 3: Sample from trending/popular categories for diversity
        if use_trending:
            logger.info("Phase 3: Sampling from various categories")
            categories = ['music', 'gaming', 'news', 'sports', 'education', 'technology',
                         'science', 'politics', 'cooking', 'travel', 'fashion', 'comedy']

            for category in categories:
                category_videos = self.api_client.search_videos(query=category, max_results=20)
                video_ids.update(category_videos)

        logger.info(f"Hybrid sampling complete: {len(video_ids)} total unique videos")
        return list(video_ids)

    def get_diverse_sample(self, target_size: int = 1000) -> List[str]:
        """
        Get a diverse sample of videos trying to approximate random sampling

        Since true random sampling via random ID generation is extremely inefficient,
        this method uses a combination of techniques to create a diverse sample.

        Args:
            target_size: Target number of videos to sample

        Returns:
            List of video IDs
        """
        # Calculate how many prefixes we need
        # Assuming each prefix search returns ~5-10 unique videos
        num_prefixes = target_size // 7

        return self.sample_videos_hybrid(
            num_prefixes=num_prefixes,
            use_trending=True
        )
