# Setup Guide

This guide will help you set up and run the Contra YouTube Recommender.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A YouTube Data API v3 key

## Step 1: Get YouTube API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **YouTube Data API v3**
4. Create credentials (API key)
5. Copy the API key

## Step 2: Install Dependencies

```bash
# Navigate to the project directory
cd contra-youtube-recommender

# (Optional but recommended) Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

## Step 3: Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit the `.env` file and add your YouTube API key:

```
YOUTUBE_API_KEY=your_youtube_api_key_here
```

## Step 4: Run the Backend Server

```bash
# Make sure you're in the project directory
python run_server.py
```

The API server will start at `http://localhost:8000`

You can view the API documentation at `http://localhost:8000/docs`

## Step 5: Open the Frontend

Simply open the frontend HTML file in your browser:

```bash
# On macOS
open frontend/index.html

# On Linux
xdg-open frontend/index.html

# On Windows
start frontend/index.html
```

Or use a simple HTTP server:

```bash
# Using Python
cd frontend
python3 -m http.server 3000

# Then open http://localhost:3000 in your browser
```

## Usage

### Using the Web Interface

1. Open the frontend in your browser
2. Enter a YouTube video ID or paste a full URL
3. Click "Find Contra Videos"
4. Wait for the analysis to complete (may take 30-60 seconds)
5. View the results showing opposite-perspective videos

### Using the API Directly

#### Analyze a single video:

```bash
curl "http://localhost:8000/contra/single/dQw4w9WgXcQ?num_contra_videos=10"
```

#### Get video metadata:

```bash
curl "http://localhost:8000/video/dQw4w9WgXcQ"
```

#### Compare two videos:

```bash
curl -X POST "http://localhost:8000/compare" \
  -H "Content-Type: application/json" \
  -d '{"video_id_1": "dQw4w9WgXcQ", "video_id_2": "jNQXAC9IVRw"}'
```

### Using Python

See `examples/example_usage.py` for Python examples.

## Troubleshooting

### API Key Issues

If you get errors about missing API key:
- Make sure your `.env` file exists and contains `YOUTUBE_API_KEY`
- Verify the API key is correct
- Ensure YouTube Data API v3 is enabled in Google Cloud Console

### Module Import Errors

If you get import errors when running the server:
- Make sure you've installed all dependencies: `pip install -r requirements.txt`
- Make sure you're running from the project root directory

### Slow Performance

The first run will be slower because:
- Sentence transformer models need to be downloaded (~90MB)
- Random video samples are being collected
- Subsequent runs use cached data and will be much faster

### CORS Errors in Frontend

If you see CORS errors in the browser console:
- Make sure the backend server is running
- Check that the API URL in the frontend settings matches your backend URL
- The backend is configured to allow all origins for development

## Advanced Configuration

You can modify algorithm parameters in the `.env` file:

```
# Minimum cosine distance threshold (0-2)
MIN_DISTANCE_THRESHOLD=0.7

# Minimum angle threshold in degrees (0-180)
ANGLE_THRESHOLD=150

# Embedding model to use
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Random sample size
RANDOM_SAMPLE_SIZE=10000
```

## Next Steps

- Try analyzing different types of videos (political, educational, entertainment)
- Experiment with different sample sizes and thresholds
- Export results and analyze the contra recommendations
- Build a browser extension or mobile app on top of the API

## Support

For issues and questions, please check the main README.md or create an issue in the repository.
