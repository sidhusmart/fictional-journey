"""
YouTube API Client
Wrapper around YouTube Data API v3
"""
import os
from typing import List, Dict, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YouTubeAPIClient:
    """Client for interacting with YouTube Data API v3"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize YouTube API client

        Args:
            api_key: YouTube Data API key. If None, reads from YOUTUBE_API_KEY env var
        """
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        if not self.api_key:
            raise ValueError("YouTube API key is required. Set YOUTUBE_API_KEY environment variable.")

        self.youtube = build('youtube', 'v3', developerKey=self.api_key)

    def get_video_metadata(self, video_id: str) -> Optional[Dict]:
        """
        Get metadata for a single video

        Args:
            video_id: YouTube video ID (11 characters)

        Returns:
            Dictionary with video metadata or None if not found
        """
        try:
            request = self.youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            )
            response = request.execute()

            if not response.get('items'):
                logger.warning(f"Video {video_id} not found")
                return None

            item = response['items'][0]
            snippet = item['snippet']
            statistics = item.get('statistics', {})

            return {
                'video_id': video_id,
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'channel_title': snippet.get('channelTitle', ''),
                'channel_id': snippet.get('channelId', ''),
                'published_at': snippet.get('publishedAt', ''),
                'tags': snippet.get('tags', []),
                'category_id': snippet.get('categoryId', ''),
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'comment_count': int(statistics.get('commentCount', 0)),
                'duration': item['contentDetails'].get('duration', ''),
            }

        except HttpError as e:
            logger.error(f"HTTP error getting video {video_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting video {video_id}: {e}")
            return None

    def get_videos_metadata(self, video_ids: List[str]) -> List[Dict]:
        """
        Get metadata for multiple videos (batch operation)

        Args:
            video_ids: List of YouTube video IDs

        Returns:
            List of video metadata dictionaries
        """
        results = []
        # YouTube API allows up to 50 videos per request
        batch_size = 50

        for i in range(0, len(video_ids), batch_size):
            batch = video_ids[i:i + batch_size]
            try:
                request = self.youtube.videos().list(
                    part='snippet,statistics,contentDetails',
                    id=','.join(batch)
                )
                response = request.execute()

                for item in response.get('items', []):
                    snippet = item['snippet']
                    statistics = item.get('statistics', {})

                    results.append({
                        'video_id': item['id'],
                        'title': snippet.get('title', ''),
                        'description': snippet.get('description', ''),
                        'channel_title': snippet.get('channelTitle', ''),
                        'channel_id': snippet.get('channelId', ''),
                        'published_at': snippet.get('publishedAt', ''),
                        'tags': snippet.get('tags', []),
                        'category_id': snippet.get('categoryId', ''),
                        'view_count': int(statistics.get('viewCount', 0)),
                        'like_count': int(statistics.get('likeCount', 0)),
                        'comment_count': int(statistics.get('commentCount', 0)),
                        'duration': item['contentDetails'].get('duration', ''),
                    })

            except HttpError as e:
                logger.error(f"HTTP error getting batch: {e}")
            except Exception as e:
                logger.error(f"Error getting batch: {e}")

        return results

    def search_videos(self, query: str, max_results: int = 50) -> List[str]:
        """
        Search for videos using a query

        Args:
            query: Search query
            max_results: Maximum number of results to return

        Returns:
            List of video IDs
        """
        try:
            request = self.youtube.search().list(
                part='id',
                q=query,
                type='video',
                maxResults=min(max_results, 50)
            )
            response = request.execute()

            video_ids = [
                item['id']['videoId']
                for item in response.get('items', [])
                if item['id']['kind'] == 'youtube#video'
            ]

            return video_ids

        except HttpError as e:
            logger.error(f"HTTP error searching for '{query}': {e}")
            return []
        except Exception as e:
            logger.error(f"Error searching for '{query}': {e}")
            return []

    def check_video_exists(self, video_id: str) -> bool:
        """
        Check if a video exists and is accessible

        Args:
            video_id: YouTube video ID

        Returns:
            True if video exists and is accessible
        """
        try:
            request = self.youtube.videos().list(
                part='id',
                id=video_id
            )
            response = request.execute()
            return len(response.get('items', [])) > 0

        except Exception as e:
            logger.error(f"Error checking video {video_id}: {e}")
            return False
