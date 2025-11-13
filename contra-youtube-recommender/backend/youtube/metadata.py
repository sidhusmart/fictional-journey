"""
Video Metadata Extraction and Processing
"""
import re
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetadataProcessor:
    """Process and clean YouTube video metadata for embedding"""

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean text by removing URLs, special characters, extra whitespace

        Args:
            text: Raw text

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove URLs
        text = re.sub(r'http\S+|www.\S+', '', text)

        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)

        return text.strip()

    @staticmethod
    def extract_text_for_embedding(metadata: Dict) -> str:
        """
        Extract and combine relevant text fields for embedding

        Args:
            metadata: Video metadata dictionary

        Returns:
            Combined text string ready for embedding
        """
        components = []

        # Title (most important)
        title = metadata.get('title', '')
        if title:
            # Give title more weight by including it twice
            components.append(MetadataProcessor.clean_text(title))
            components.append(MetadataProcessor.clean_text(title))

        # Tags (very relevant for topic)
        tags = metadata.get('tags', [])
        if tags:
            tags_text = ' '.join(tags)
            components.append(MetadataProcessor.clean_text(tags_text))

        # Channel title (provides context about content creator)
        channel_title = metadata.get('channel_title', '')
        if channel_title:
            components.append(MetadataProcessor.clean_text(channel_title))

        # Description (first 500 chars - often most relevant)
        description = metadata.get('description', '')
        if description:
            # Take first 500 characters to avoid very long descriptions
            description_snippet = description[:500]
            components.append(MetadataProcessor.clean_text(description_snippet))

        # Combine all components
        combined_text = ' '.join(components)

        return combined_text

    @staticmethod
    def parse_duration(duration_str: str) -> int:
        """
        Parse ISO 8601 duration string to seconds

        Args:
            duration_str: Duration in ISO 8601 format (e.g., 'PT4M13S')

        Returns:
            Duration in seconds
        """
        if not duration_str:
            return 0

        # Remove 'PT' prefix
        duration_str = duration_str.replace('PT', '')

        hours = 0
        minutes = 0
        seconds = 0

        # Parse hours
        if 'H' in duration_str:
            hours_match = re.search(r'(\d+)H', duration_str)
            if hours_match:
                hours = int(hours_match.group(1))

        # Parse minutes
        if 'M' in duration_str:
            minutes_match = re.search(r'(\d+)M', duration_str)
            if minutes_match:
                minutes = int(minutes_match.group(1))

        # Parse seconds
        if 'S' in duration_str:
            seconds_match = re.search(r'(\d+)S', duration_str)
            if seconds_match:
                seconds = int(seconds_match.group(1))

        return hours * 3600 + minutes * 60 + seconds

    @staticmethod
    def categorize_duration(seconds: int) -> str:
        """
        Categorize video duration

        Args:
            seconds: Duration in seconds

        Returns:
            Category string
        """
        if seconds < 60:
            return 'very_short'  # < 1 minute
        elif seconds < 300:
            return 'short'  # 1-5 minutes
        elif seconds < 1200:
            return 'medium'  # 5-20 minutes
        elif seconds < 3600:
            return 'long'  # 20-60 minutes
        else:
            return 'very_long'  # > 1 hour

    @staticmethod
    def enrich_metadata(metadata: Dict) -> Dict:
        """
        Enrich metadata with additional computed fields

        Args:
            metadata: Raw video metadata

        Returns:
            Enriched metadata
        """
        enriched = metadata.copy()

        # Parse duration
        duration_seconds = MetadataProcessor.parse_duration(metadata.get('duration', ''))
        enriched['duration_seconds'] = duration_seconds
        enriched['duration_category'] = MetadataProcessor.categorize_duration(duration_seconds)

        # Calculate engagement metrics
        view_count = metadata.get('view_count', 0)
        like_count = metadata.get('like_count', 0)
        comment_count = metadata.get('comment_count', 0)

        # Engagement rate (likes + comments per view)
        if view_count > 0:
            engagement_rate = (like_count + comment_count) / view_count
            enriched['engagement_rate'] = engagement_rate
        else:
            enriched['engagement_rate'] = 0.0

        # Extract text for embedding
        enriched['embedding_text'] = MetadataProcessor.extract_text_for_embedding(metadata)

        return enriched

    @staticmethod
    def batch_enrich_metadata(metadata_list: List[Dict]) -> List[Dict]:
        """
        Enrich a batch of metadata dictionaries

        Args:
            metadata_list: List of video metadata dictionaries

        Returns:
            List of enriched metadata dictionaries
        """
        return [MetadataProcessor.enrich_metadata(m) for m in metadata_list]
