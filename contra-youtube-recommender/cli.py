#!/usr/bin/env python3
"""
Command-line interface for Contra YouTube Recommender
"""
import argparse
import os
import sys
import json
from dotenv import load_dotenv

from backend.youtube.api_client import YouTubeAPIClient
from backend.contra.algorithm import ContraFeedGenerator

# Load environment variables
load_dotenv()


def analyze_video(args):
    """Analyze a single video and find contra videos"""
    print(f"Analyzing video: {args.video_id}")

    # Initialize
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("Error: YOUTUBE_API_KEY not found. Please set it in .env file")
        sys.exit(1)

    youtube_client = YouTubeAPIClient(api_key)
    contra_generator = ContraFeedGenerator(youtube_client)

    # Analyze
    result = contra_generator.analyze_single_video(
        video_id=args.video_id,
        num_contra_videos=args.num_videos,
        random_sample_size=args.sample_size,
        use_cache=not args.no_cache
    )

    # Output
    if args.output_json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n{'=' * 80}")
        print(f"Input Video: {result['input_video']['title']}")
        print(f"Channel: {result['input_video']['channel_title']}")
        print(f"{'=' * 80}")
        print(f"\nFound {len(result['contra_videos'])} contra videos")
        print(f"Average distance: {result['summary']['avg_distance']:.2f}")
        print(f"Average angle: {result['summary']['avg_angle']:.1f}°")
        print(f"\nContra Videos:")
        for i, video in enumerate(result['contra_videos'], 1):
            score = video['contra_score']
            print(f"\n{i}. {video['title']}")
            print(f"   Channel: {video['channel_title']}")
            print(f"   Distance: {score['distance']:.2f}, Angle: {score['angle']:.1f}°")
            print(f"   URL: https://www.youtube.com/watch?v={video['video_id']}")


def compare_videos(args):
    """Compare two videos"""
    print(f"Comparing videos: {args.video_id_1} vs {args.video_id_2}")

    # Initialize
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("Error: YOUTUBE_API_KEY not found. Please set it in .env file")
        sys.exit(1)

    youtube_client = YouTubeAPIClient(api_key)
    contra_generator = ContraFeedGenerator(youtube_client)

    # Compare
    result = contra_generator.compare_videos(args.video_id_1, args.video_id_2)

    # Output
    if args.output_json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n{'=' * 80}")
        print(f"Video 1: {result['video_1']['title']}")
        print(f"Video 2: {result['video_2']['title']}")
        print(f"{'=' * 80}")
        comparison = result['comparison']
        print(f"\nSimilarity: {comparison['cosine_similarity']:.3f}")
        print(f"Distance: {comparison['cosine_distance']:.3f}")
        print(f"Angle: {comparison['angle_degrees']:.1f}°")
        print(f"Relationship: {comparison['relationship']}")


def analyze_feed(args):
    """Analyze multiple videos (a feed)"""
    video_ids = args.video_ids.split(',')
    print(f"Analyzing feed with {len(video_ids)} videos")

    # Initialize
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("Error: YOUTUBE_API_KEY not found. Please set it in .env file")
        sys.exit(1)

    youtube_client = YouTubeAPIClient(api_key)
    contra_generator = ContraFeedGenerator(youtube_client)

    # Analyze
    contra_videos = contra_generator.generate_contra_feed(
        input_video_ids=video_ids,
        num_contra_videos=args.num_videos,
        random_sample_size=args.sample_size,
        use_cache=not args.no_cache,
        method=args.method
    )

    # Output
    if args.output_json:
        print(json.dumps(contra_videos, indent=2))
    else:
        print(f"\nFound {len(contra_videos)} contra videos")
        print(f"\nTop Contra Videos:")
        for i, video in enumerate(contra_videos, 1):
            score = video['contra_score']
            print(f"\n{i}. {video['title']}")
            print(f"   Distance: {score['distance']:.2f}, Angle: {score['angle']:.1f}°")
            print(f"   URL: https://www.youtube.com/watch?v={video['video_id']}")


def collect_sample(args):
    """Collect random sample of videos"""
    print(f"Collecting random sample of {args.sample_size} videos...")

    # Initialize
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("Error: YOUTUBE_API_KEY not found. Please set it in .env file")
        sys.exit(1)

    youtube_client = YouTubeAPIClient(api_key)
    contra_generator = ContraFeedGenerator(youtube_client)

    # Collect
    random_sample = contra_generator.get_or_create_random_sample(
        sample_size=args.sample_size,
        use_cache=False  # Force new collection
    )

    print(f"\nCollected {len(random_sample)} random videos")
    print("Sample saved to cache")


def main():
    parser = argparse.ArgumentParser(
        description='Contra YouTube Recommender - CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a single video
  python cli.py analyze dQw4w9WgXcQ

  # Compare two videos
  python cli.py compare dQw4w9WgXcQ jNQXAC9IVRw

  # Analyze a feed of videos
  python cli.py feed "dQw4w9WgXcQ,jNQXAC9IVRw,9bZkp7q19f0"

  # Collect random sample
  python cli.py sample --sample-size 1000
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a single video')
    analyze_parser.add_argument('video_id', help='YouTube video ID')
    analyze_parser.add_argument('-n', '--num-videos', type=int, default=20,
                               help='Number of contra videos to find (default: 20)')
    analyze_parser.add_argument('-s', '--sample-size', type=int, default=1000,
                               help='Random sample size (default: 1000)')
    analyze_parser.add_argument('--no-cache', action='store_true',
                               help='Don\'t use cached random sample')
    analyze_parser.add_argument('--json', dest='output_json', action='store_true',
                               help='Output as JSON')
    analyze_parser.set_defaults(func=analyze_video)

    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare two videos')
    compare_parser.add_argument('video_id_1', help='First video ID')
    compare_parser.add_argument('video_id_2', help='Second video ID')
    compare_parser.add_argument('--json', dest='output_json', action='store_true',
                               help='Output as JSON')
    compare_parser.set_defaults(func=compare_videos)

    # Feed command
    feed_parser = subparsers.add_parser('feed', help='Analyze multiple videos')
    feed_parser.add_argument('video_ids', help='Comma-separated video IDs')
    feed_parser.add_argument('-n', '--num-videos', type=int, default=20,
                            help='Number of contra videos to find (default: 20)')
    feed_parser.add_argument('-s', '--sample-size', type=int, default=1000,
                            help='Random sample size (default: 1000)')
    feed_parser.add_argument('-m', '--method', choices=['diametric', 'centroid'],
                            default='diametric', help='Algorithm method (default: diametric)')
    feed_parser.add_argument('--no-cache', action='store_true',
                            help='Don\'t use cached random sample')
    feed_parser.add_argument('--json', dest='output_json', action='store_true',
                            help='Output as JSON')
    feed_parser.set_defaults(func=analyze_feed)

    # Sample command
    sample_parser = subparsers.add_parser('sample', help='Collect random sample')
    sample_parser.add_argument('-s', '--sample-size', type=int, default=1000,
                              help='Sample size (default: 1000)')
    sample_parser.set_defaults(func=collect_sample)

    # Parse and execute
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        if '--debug' in sys.argv:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
