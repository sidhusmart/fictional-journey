# Contra YouTube Recommender

An algorithm that creates a "contra feed" - a collection of YouTube videos with diametrically opposite views and perspectives to your current YouTube recommendation feed.

## Overview

This tool helps you break out of echo chambers by finding and recommending videos that present opposing viewpoints to your current YouTube feed. It uses embedding-based analysis to identify content that is maximally distant from your current recommendations in the semantic space.

## How It Works

1. **Feed Collection**: Extract metadata from videos in your current YouTube feed (or analyze a specific video)
2. **Random Sampling**: Collect a random sample of YouTube videos using random prefix sampling methodology
3. **Embedding**: Convert video metadata (titles, descriptions, tags) into vector embeddings using open-source models
4. **Contra Discovery**: Find videos that are diametrically opposite in the embedding space
5. **Seed Generation**: Use these contra videos as seeds for the recommendation algorithm
6. **Feed Generation**: Simulate watching these seeds to generate a full contra feed

## Methodology

### Random Prefix Sampling

Based on the research paper ["Dialing for Videos: A Random Sample of YouTube"](https://journalqd.org/article/view/4066) by McGrady et al. (2023), we use random prefix sampling to create an unbiased sample of YouTube videos.

**How it works:**
- YouTube video IDs are 11-character strings (e.g., `dQw4w9WgXcQ`)
- We generate random 5-character prefixes
- Query YouTube's search API with these prefixes
- This provides a statistically random sample of videos

### Embedding & Distance Calculation

- Use open-source sentence transformers (e.g., `all-MiniLM-L6-v2`) to embed video metadata
- Calculate cosine distances between current feed videos and random sample
- Identify videos with maximum distance AND opposite direction (180° angle)

### Contra Feed Definition

A video is considered "contra" if:
1. It has high cosine distance from all current feed videos
2. Its embedding vector points in the opposite direction (diametrically opposite)
3. It represents a coherent alternative viewpoint (not just random/unrelated content)

## Project Structure

```
contra-youtube-recommender/
├── backend/
│   ├── api/                    # API endpoints
│   ├── youtube/
│   │   ├── sampler.py         # Random prefix sampling
│   │   ├── metadata.py        # Metadata extraction
│   │   └── api_client.py      # YouTube API wrapper
│   ├── embeddings/
│   │   ├── encoder.py         # Embedding generation
│   │   └── distance.py        # Distance calculations
│   ├── contra/
│   │   └── algorithm.py       # Contra feed algorithm
│   └── database/
│       └── models.py          # Data models
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── package.json
├── data/
│   └── random_samples/        # Cached random video samples
├── requirements.txt
└── README.md
```

## Installation

```bash
# Backend
cd contra-youtube-recommender
pip install -r requirements.txt

# Frontend (to be implemented)
cd frontend
npm install
```

## Usage

### Option 1: Connect YouTube Account
```python
# Analyze your recommendation feed
python -m backend.api.main --mode feed
```

### Option 2: Single Video Analysis
```python
# Analyze a specific video
python -m backend.api.main --mode video --video-id dQw4w9WgXcQ
```

## API Requirements

- **YouTube Data API v3**: For video metadata and search
- **Google OAuth 2.0**: For user feed access (if available)

## References

- McGrady, R., Zheng, K., Curran, R., Baumgartner, J., & Zuckerman, E. (2023). "Dialing for Videos: A Random Sample of YouTube". *Journal of Quantitative Description: Digital Media*, 3.
- Zhou, Y. et al. (2011). "Counting YouTube videos via random prefix sampling". *ACM SIGCOMM IMC*.

## Future Enhancements

- [ ] Web frontend for easy interaction
- [ ] Persistent database of random samples
- [ ] User accounts and feed history
- [ ] Visualization of embedding space
- [ ] Export contra feed as YouTube playlist
- [ ] Browser extension for real-time contra suggestions

## License

MIT License
