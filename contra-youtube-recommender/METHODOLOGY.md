# Contra YouTube Recommender: Methodology

This document explains the technical methodology behind the Contra YouTube Recommender algorithm.

## Overview

The goal of this project is to find YouTube videos that present **diametrically opposite** viewpoints to a given set of videos (e.g., a user's recommendation feed). This helps users:

- Break out of echo chambers
- Understand opposing perspectives
- Make more informed decisions
- Develop critical thinking skills

## Algorithm Pipeline

The algorithm consists of five main stages:

### 1. Input Video Analysis

**Input:** YouTube video ID(s) from user's feed

**Process:**
- Fetch video metadata via YouTube Data API v3
- Extract relevant fields: title, description, tags, channel info
- Clean and preprocess text (remove URLs, special characters)
- Combine fields into a single text representation

**Output:** Structured metadata with embedding-ready text

### 2. Random Video Sampling

**Goal:** Create an unbiased sample of YouTube videos to search for contra content

**Methodology:** Based on [McGrady et al. (2023)](https://journalqd.org/article/view/4066) - "Dialing for Videos: A Random Sample of YouTube"

#### The Random Prefix Sampling Technique

YouTube video IDs are 11-character strings using the character set: `[A-Za-z0-9_-]` (64 possible characters)

The original method (Zhou et al., 2011):
1. Generate random k-character prefixes (typically k=5)
2. Query YouTube search API for videos starting with that prefix
3. Collect returned video IDs

This provides a statistically unbiased sample because:
- Each prefix has equal probability of being generated
- Videos are uniformly distributed across the ID space
- No algorithmic bias from YouTube's recommendation system

#### Our Implementation

Since YouTube's API no longer supports direct prefix searching of video IDs, we use a **hybrid sampling approach**:

1. **Random Prefix Search:** Search for random character sequences
2. **Category Sampling:** Sample from diverse content categories
3. **Caching:** Store samples for reuse to reduce API calls

While not perfectly random, this approach provides sufficient diversity for finding contra content.

### 3. Embedding Generation

**Goal:** Convert video text into dense vector representations in a semantic space

**Model:** Sentence Transformers (default: `all-MiniLM-L6-v2`)
- 384-dimensional embeddings
- Fast inference (~5ms per video)
- Captures semantic meaning of text
- Pre-trained on large text corpora

**Process:**
```
Text → Tokenization → BERT-based encoding → Mean pooling → Normalized vector
```

**Properties of embedding space:**
- Similar videos are close together
- Dissimilar videos are far apart
- Direction in space represents conceptual orientation

### 4. Contra Video Discovery

**Goal:** Find videos that are "diametrically opposite" to input videos

We implement two methods:

#### Method 1: Diametric Opposition (Recommended)

For each candidate video, calculate:

1. **Cosine Distance** to each input video:
   ```
   distance = 1 - cosine_similarity
   distance ∈ [0, 2]
   ```

2. **Angle** to each input video:
   ```
   angle = arccos(cosine_similarity)
   angle ∈ [0°, 180°]
   ```

A video is considered "contra" if:
- **High distance** from ALL input videos (min_distance > 0.7)
- **Large angle** on average (avg_angle > 150°)
- Ideally angle ≈ 180° (perfectly opposite)

**Ranking:** Sort by angle (descending), then distance

**Intuition:** These videos point in the opposite direction in semantic space

#### Method 2: Centroid Opposition

1. Calculate the centroid (average) of all input video embeddings
2. Find candidates with maximum distance and angle to this centroid

**Pros:** Simpler, faster
**Cons:** May miss nuanced opposition to individual videos

### 5. Result Filtering and Ranking

**Filtering:**
- Remove duplicates
- Remove videos too similar to any input video
- Remove unavailable/private videos

**Scoring:**
Each contra video receives:
- `distance`: Average cosine distance to input videos
- `angle`: Average angle to input videos
- `method`: Algorithm method used

**Ranking:**
Primary: angle (higher = more opposite)
Secondary: distance (higher = more dissimilar)

## Mathematical Foundations

### Cosine Similarity

```
similarity(A, B) = (A · B) / (||A|| × ||B||)
```

- Range: [-1, 1]
- 1 = identical direction
- 0 = orthogonal (unrelated)
- -1 = opposite direction

### Cosine Distance

```
distance(A, B) = 1 - similarity(A, B)
```

- Range: [0, 2]
- 0 = identical
- 1 = orthogonal
- 2 = opposite

### Angle Between Vectors

```
angle(A, B) = arccos(similarity(A, B))
```

- Range: [0°, 180°]
- 0° = same direction
- 90° = orthogonal
- 180° = opposite direction

## Why This Works

### Semantic Space Properties

Sentence transformers encode meaning into geometric relationships:

1. **Topical Clustering:** Videos about the same topic cluster together
2. **Perspective Orientation:** Different perspectives on the same topic point in different directions
3. **Opposition Detection:** Opposite viewpoints are maximally distant in angle

### Example

Consider three videos about climate change:

```
Video A: "Climate change is a serious threat"
  Embedding: [0.8, 0.6, ...]

Video B: "How to reduce your carbon footprint"
  Embedding: [0.7, 0.65, ...]  # Close to A

Video C: "Climate change is a hoax"
  Embedding: [-0.6, -0.5, ...]  # Opposite to A and B
```

The algorithm would identify Video C as "contra" to Videos A and B because:
- High cosine distance (≈1.8)
- Large angle (≈160-170°)
- Negative correlation in embedding dimensions

## Limitations and Considerations

### 1. Sampling Bias

- True random sampling of YouTube is computationally infractable
- Our hybrid approach may miss obscure or niche content
- Mitigation: Use large sample sizes (1000+ videos)

### 2. Language and Culture

- Sentence transformers work best for English content
- May not capture cultural context or sarcasm
- Mitigation: Use multilingual models for non-English content

### 3. Topic Coherence

- Algorithm may find opposite videos on different topics
- E.g., "cooking tutorial" vs "car repair" (both distant but unrelated)
- Mitigation: Filter by topic/category, require minimum topical overlap

### 4. Echo Chamber Reinforcement

- Users might dismiss contra content as "wrong"
- Need to present results thoughtfully
- Mitigation: UI design, framing, education

### 5. Content Quality

- Algorithm doesn't assess video quality or accuracy
- May surface misinformation if it's opposite to truth
- Mitigation: Consider view counts, channel authority, fact-checking

## Future Improvements

1. **Multi-modal Analysis:** Incorporate video thumbnails, audio transcripts
2. **Temporal Analysis:** Track how perspectives change over time
3. **Network Analysis:** Use channel/user networks to find opposing communities
4. **Topic Modeling:** Ensure contra videos are on the same topic
5. **Gradual Opposition:** Provide a spectrum from similar → neutral → opposite
6. **Personalization:** Learn user preferences for type of contra content
7. **Fact-Checking Integration:** Flag misinformation regardless of perspective

## References

1. McGrady, R., Zheng, K., Curran, R., Baumgartner, J., & Zuckerman, E. (2023). "Dialing for Videos: A Random Sample of YouTube". *Journal of Quantitative Description: Digital Media*, 3.

2. Zhou, Y., Chen, L., Yang, C., & Chiu, D. M. (2011). "Counting YouTube videos via random prefix sampling". *Proceedings of the 2011 ACM SIGCOMM Conference on Internet Measurement Conference*.

3. Reimers, N., & Gurevych, I. (2019). "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks". *Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing*.

## Conclusion

The Contra YouTube Recommender uses a combination of:
- Random sampling methodology from academic research
- State-of-the-art sentence embedding models
- Geometric analysis in semantic space

to find videos that present diametrically opposite perspectives. While not perfect, it provides a useful tool for breaking out of echo chambers and understanding diverse viewpoints.
