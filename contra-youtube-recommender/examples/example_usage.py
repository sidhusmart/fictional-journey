#!/usr/bin/env python3
"""
Example usage of the Contra YouTube Recommender

This script demonstrates how to use the contra feed algorithm
programmatically without the web interface.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from backend.youtube.api_client import YouTubeAPIClient
from backend.contra.algorithm import ContraFeedGenerator

# Load environment variables
load_dotenv()


def example_1_analyze_single_video():
    """Example 1: Analyze a single video and find contra videos"""
    print("=" * 80)
    print("Example 1: Analyze a single video")
    print("=" * 80)

    # Initialize clients
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("Error: YOUTUBE_API_KEY not found in environment variables")
        return

    youtube_client = YouTubeAPIClient(api_key)
    contra_generator = ContraFeedGenerator(youtube_client)

    # Analyze a video (replace with any YouTube video ID)
    video_id = "dQw4w9WgXcQ"
    print(f"\nAnalyzing video: {video_id}")

    result = contra_generator.analyze_single_video(
        video_id=video_id,
        num_contra_videos=10,
        random_sample_size=500,  # Use smaller sample for faster testing
        use_cache=True
    )

    # Print results
    print(f"\nInput Video: {result['input_video']['title']}")
    print(f"Channel: {result['input_video']['channel_title']}")
    print(f"\nFound {len(result['contra_videos'])} contra videos:")
    print(f"Average distance: {result['summary']['avg_distance']:.2f}")
    print(f"Average angle: {result['summary']['avg_angle']:.1f}°")

    print("\nTop 5 Contra Videos:")
    for i, video in enumerate(result['contra_videos'][:5], 1):
        score = video['contra_score']
        print(f"\n{i}. {video['title']}")
        print(f"   Channel: {video['channel_title']}")
        print(f"   Distance: {score['distance']:.2f}, Angle: {score['angle']:.1f}°")
        print(f"   URL: https://www.youtube.com/watch?v={video['video_id']}")


def example_2_compare_two_videos():
    """Example 2: Compare two videos"""
    print("\n" + "=" * 80)
    print("Example 2: Compare two videos")
    print("=" * 80)

    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("Error: YOUTUBE_API_KEY not found in environment variables")
        return

    youtube_client = YouTubeAPIClient(api_key)
    contra_generator = ContraFeedGenerator(youtube_client)

    # Compare two videos
    video_id_1 = "dQw4w9WgXcQ"
    video_id_2 = "jNQXAC9IVRw"

    print(f"\nComparing:")
    print(f"Video 1: {video_id_1}")
    print(f"Video 2: {video_id_2}")

    result = contra_generator.compare_videos(video_id_1, video_id_2)

    print(f"\nVideo 1: {result['video_1']['title']}")
    print(f"Video 2: {result['video_2']['title']}")

    comparison = result['comparison']
    print(f"\nComparison Results:")
    print(f"Cosine Similarity: {comparison['cosine_similarity']:.3f}")
    print(f"Cosine Distance: {comparison['cosine_distance']:.3f}")
    print(f"Angle: {comparison['angle_degrees']:.1f}°")
    print(f"Relationship: {comparison['relationship']}")


def example_3_analyze_multiple_videos():
    """Example 3: Analyze a feed of multiple videos"""
    print("\n" + "=" * 80)
    print("Example 3: Analyze multiple videos (simulating a feed)")
    print("=" * 80)

    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("Error: YOUTUBE_API_KEY not found in environment variables")
        return

    youtube_client = YouTubeAPIClient(api_key)
    contra_generator = ContraFeedGenerator(youtube_client)

    # Simulate a user's YouTube feed (multiple videos)
    # Replace these with actual video IDs from a user's feed
    feed_video_ids = [
        "dQw4w9WgXcQ",
        "jNQXAC9IVRw",
        "9bZkp7q19f0"
    ]

    print(f"\nAnalyzing feed with {len(feed_video_ids)} videos")

    contra_videos = contra_generator.generate_contra_feed(
        input_video_ids=feed_video_ids,
        num_contra_videos=15,
        random_sample_size=500,
        use_cache=True,
        method='diametric'
    )

    print(f"\nFound {len(contra_videos)} contra videos")

    print("\nTop 5 Contra Videos:")
    for i, video in enumerate(contra_videos[:5], 1):
        score = video['contra_score']
        print(f"\n{i}. {video['title']}")
        print(f"   Distance: {score['distance']:.2f}, Angle: {score['angle']:.1f}°")
        print(f"   URL: https://www.youtube.com/watch?v={video['video_id']}")


def example_4_collect_random_sample():
    """Example 4: Collect and cache a random sample"""
    print("\n" + "=" * 80)
    print("Example 4: Collect random sample of YouTube videos")
    print("=" * 80)

    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("Error: YOUTUBE_API_KEY not found in environment variables")
        return

    youtube_client = YouTubeAPIClient(api_key)
    contra_generator = ContraFeedGenerator(youtube_client)

    print("\nCollecting random sample (this may take a few minutes)...")

    random_sample = contra_generator.get_or_create_random_sample(
        sample_size=100,  # Small sample for testing
        use_cache=False  # Force new collection
    )

    print(f"\nCollected {len(random_sample)} random videos")
    print("\nSample videos:")
    for i, video in enumerate(random_sample[:5], 1):
        print(f"{i}. {video['title']}")
        print(f"   Views: {video['view_count']:,}")


def example_5_get_statistics():
    """Example 5: Get statistics about the system"""
    print("\n" + "=" * 80)
    print("Example 5: Get system statistics")
    print("=" * 80)

    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("Error: YOUTUBE_API_KEY not found in environment variables")
        return

    youtube_client = YouTubeAPIClient(api_key)
    contra_generator = ContraFeedGenerator(youtube_client)

    stats = contra_generator.get_statistics()

    print("\nSystem Statistics:")
    print(f"Cache directory: {stats['cache_dir']}")
    print(f"Cached samples: {stats['cache_size']}")
    print(f"Embedder cache size: {stats['embedder_cache_size']}")
    print(f"\nParameters:")
    print(f"Min distance threshold: {stats['parameters']['min_distance']}")
    print(f"Min angle threshold: {stats['parameters']['min_angle']}°")


def main():
    """Run all examples"""
    print("\n🎯 Contra YouTube Recommender - Examples\n")

    try:
        # Run examples
        example_1_analyze_single_video()
        example_2_compare_two_videos()
        example_3_analyze_multiple_videos()
        # example_4_collect_random_sample()  # Uncomment to test random sampling
        example_5_get_statistics()

        print("\n" + "=" * 80)
        print("All examples completed!")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
