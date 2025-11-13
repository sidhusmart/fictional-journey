"""
FastAPI application for Contra YouTube Recommender
"""
import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import logging

from ..youtube.api_client import YouTubeAPIClient
from ..contra.algorithm import ContraFeedGenerator

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Contra YouTube Recommender API",
    description="API for finding diametrically opposite YouTube videos",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services (lazy loading)
youtube_client: Optional[YouTubeAPIClient] = None
contra_generator: Optional[ContraFeedGenerator] = None


def get_youtube_client() -> YouTubeAPIClient:
    """Get or create YouTube API client"""
    global youtube_client
    if youtube_client is None:
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="YouTube API key not configured. Set YOUTUBE_API_KEY environment variable."
            )
        youtube_client = YouTubeAPIClient(api_key)
    return youtube_client


def get_contra_generator() -> ContraFeedGenerator:
    """Get or create contra feed generator"""
    global contra_generator
    if contra_generator is None:
        contra_generator = ContraFeedGenerator(get_youtube_client())
    return contra_generator


# Pydantic models
class VideoInfo(BaseModel):
    """Basic video information"""
    video_id: str
    title: str
    channel_title: str


class ContraRequest(BaseModel):
    """Request for generating contra feed"""
    video_ids: List[str] = Field(..., description="List of video IDs from user's feed")
    num_contra_videos: int = Field(20, description="Number of contra videos to return", ge=1, le=50)
    random_sample_size: int = Field(1000, description="Size of random sample", ge=100, le=10000)
    use_cache: bool = Field(True, description="Whether to use cached random sample")
    method: str = Field('diametric', description="Algorithm method: 'diametric' or 'centroid'")


class ComparisonRequest(BaseModel):
    """Request for comparing two videos"""
    video_id_1: str
    video_id_2: str


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Contra YouTube Recommender API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        client = get_youtube_client()
        return {
            "status": "healthy",
            "youtube_api": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.get("/video/{video_id}")
async def get_video(video_id: str):
    """
    Get metadata for a single video

    Args:
        video_id: YouTube video ID
    """
    client = get_youtube_client()
    metadata = client.get_video_metadata(video_id)

    if not metadata:
        raise HTTPException(status_code=404, detail=f"Video {video_id} not found")

    return metadata


@app.post("/contra/generate")
async def generate_contra_feed(request: ContraRequest):
    """
    Generate contra feed for given video IDs

    This is the main endpoint that finds diametrically opposite videos.
    """
    try:
        generator = get_contra_generator()

        contra_videos = generator.generate_contra_feed(
            input_video_ids=request.video_ids,
            num_contra_videos=request.num_contra_videos,
            random_sample_size=request.random_sample_size,
            use_cache=request.use_cache,
            method=request.method
        )

        return {
            "success": True,
            "input_video_count": len(request.video_ids),
            "contra_video_count": len(contra_videos),
            "contra_videos": contra_videos
        }

    except Exception as e:
        logger.error(f"Error generating contra feed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/contra/single/{video_id}")
async def analyze_single_video(
    video_id: str,
    num_contra_videos: int = Query(20, ge=1, le=50),
    random_sample_size: int = Query(1000, ge=100, le=10000),
    use_cache: bool = Query(True)
):
    """
    Analyze a single video and find contra videos

    This is a convenience endpoint for analyzing just one video.
    """
    try:
        generator = get_contra_generator()

        result = generator.analyze_single_video(
            video_id=video_id,
            num_contra_videos=num_contra_videos,
            random_sample_size=random_sample_size,
            use_cache=use_cache
        )

        return {
            "success": True,
            **result
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing video: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compare")
async def compare_videos(request: ComparisonRequest):
    """
    Compare two videos and analyze their similarity/opposition

    Returns metrics like cosine similarity, angle, and relationship type.
    """
    try:
        generator = get_contra_generator()

        result = generator.compare_videos(
            video_id_1=request.video_id_1,
            video_id_2=request.video_id_2
        )

        return {
            "success": True,
            **result
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error comparing videos: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_statistics():
    """Get statistics about the contra feed generator"""
    try:
        generator = get_contra_generator()
        return generator.get_statistics()
    except Exception as e:
        logger.error(f"Error getting statistics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
