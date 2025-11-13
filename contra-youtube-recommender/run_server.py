#!/usr/bin/env python3
"""
Run the Contra YouTube Recommender API server
"""
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    print("Starting Contra YouTube Recommender API server...")
    print("API will be available at: http://localhost:8000")
    print("API docs will be available at: http://localhost:8000/docs")

    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
