// Contra YouTube Recommender - Frontend JavaScript

// State
let currentAnalysis = null;

// DOM Elements
const videoInput = document.getElementById('videoInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const retryBtn = document.getElementById('retryBtn');
const loadingSection = document.getElementById('loadingSection');
const errorSection = document.getElementById('errorSection');
const errorMessage = document.getElementById('errorMessage');
const resultsSection = document.getElementById('resultsSection');
const inputVideoCard = document.getElementById('inputVideoCard');
const summaryStats = document.getElementById('summaryStats');
const contraVideosList = document.getElementById('contraVideosList');

// Config
const numVideosInput = document.getElementById('numVideos');
const sampleSizeInput = document.getElementById('sampleSize');
const methodSelect = document.getElementById('method');
const apiUrlInput = document.getElementById('apiUrl');

// Event Listeners
analyzeBtn.addEventListener('click', handleAnalyze);
retryBtn.addEventListener('click', resetUI);
videoInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleAnalyze();
    }
});

// Extract video ID from input (handles both IDs and URLs)
function extractVideoId(input) {
    input = input.trim();

    // If it's already a video ID (11 characters)
    if (input.length === 11 && /^[a-zA-Z0-9_-]+$/.test(input)) {
        return input;
    }

    // Try to extract from URL
    const patterns = [
        /(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/,
        /youtube\.com\/embed\/([a-zA-Z0-9_-]{11})/,
        /youtube\.com\/v\/([a-zA-Z0-9_-]{11})/
    ];

    for (const pattern of patterns) {
        const match = input.match(pattern);
        if (match) {
            return match[1];
        }
    }

    return null;
}

// Handle analyze button click
async function handleAnalyze() {
    const input = videoInput.value;
    const videoId = extractVideoId(input);

    if (!videoId) {
        showError('Please enter a valid YouTube video ID or URL');
        return;
    }

    try {
        await analyzeVideo(videoId);
    } catch (error) {
        showError(error.message);
    }
}

// Main analysis function
async function analyzeVideo(videoId) {
    // Show loading state
    showLoading();

    // Get configuration
    const apiUrl = apiUrlInput.value || 'http://localhost:8000';
    const numVideos = parseInt(numVideosInput.value) || 20;
    const sampleSize = parseInt(sampleSizeInput.value) || 1000;
    const method = methodSelect.value || 'diametric';

    try {
        // Call API
        const response = await fetch(
            `${apiUrl}/contra/single/${videoId}?num_contra_videos=${numVideos}&random_sample_size=${sampleSize}&use_cache=true`,
            {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            }
        );

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to analyze video');
        }

        const data = await response.json();
        currentAnalysis = data;

        // Display results
        displayResults(data);
    } catch (error) {
        console.error('Error analyzing video:', error);
        showError(error.message || 'Failed to connect to API. Make sure the backend server is running.');
    }
}

// Display results
function displayResults(data) {
    // Hide loading, show results
    loadingSection.classList.add('hidden');
    errorSection.classList.add('hidden');
    resultsSection.classList.remove('hidden');

    // Display input video
    displayInputVideo(data.input_video);

    // Display summary statistics
    displaySummary(data.summary);

    // Display contra videos
    displayContraVideos(data.contra_videos);
}

// Display input video
function displayInputVideo(video) {
    inputVideoCard.innerHTML = createVideoCardHTML(video, false);
}

// Display summary statistics
function displaySummary(summary) {
    summaryStats.innerHTML = `
        <div class="stat-item">
            <span class="stat-value">${summary.num_contra_videos}</span>
            <span class="stat-label">Contra Videos Found</span>
        </div>
        <div class="stat-item">
            <span class="stat-value">${summary.avg_distance.toFixed(2)}</span>
            <span class="stat-label">Avg Distance</span>
        </div>
        <div class="stat-item">
            <span class="stat-value">${summary.avg_angle.toFixed(1)}°</span>
            <span class="stat-label">Avg Angle</span>
        </div>
    `;
}

// Display contra videos
function displayContraVideos(videos) {
    contraVideosList.innerHTML = videos
        .map(video => createVideoCardHTML(video, true))
        .join('');
}

// Create video card HTML
function createVideoCardHTML(video, showContraScore) {
    const thumbnailUrl = `https://i.ytimg.com/vi/${video.video_id}/mqdefault.jpg`;
    const videoUrl = `https://www.youtube.com/watch?v=${video.video_id}`;
    const viewCount = formatNumber(video.view_count);
    const likeCount = formatNumber(video.like_count);

    let contraScoreHTML = '';
    if (showContraScore && video.contra_score) {
        contraScoreHTML = `
            <div class="contra-score">
                <div class="score-item">
                    <span class="score-label">Distance:</span>
                    <span class="score-value">${video.contra_score.distance.toFixed(2)}</span>
                </div>
                <div class="score-item">
                    <span class="score-label">Angle:</span>
                    <span class="score-value">${video.contra_score.angle.toFixed(1)}°</span>
                </div>
            </div>
        `;
    }

    return `
        <div class="video-card">
            <div class="video-thumbnail">
                <img src="${thumbnailUrl}" alt="${escapeHtml(video.title)}" />
            </div>
            <div class="video-title">${escapeHtml(video.title)}</div>
            <div class="video-channel">${escapeHtml(video.channel_title)}</div>
            <div class="video-stats">
                <span>${viewCount} views</span>
                <span>${likeCount} likes</span>
            </div>
            ${contraScoreHTML}
            <a href="${videoUrl}" target="_blank" class="video-link">
                Watch on YouTube
            </a>
        </div>
    `;
}

// UI State Management
function showLoading() {
    analyzeBtn.disabled = true;
    loadingSection.classList.remove('hidden');
    errorSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
}

function showError(message) {
    analyzeBtn.disabled = false;
    loadingSection.classList.add('hidden');
    errorSection.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    errorMessage.textContent = message;
}

function resetUI() {
    analyzeBtn.disabled = false;
    loadingSection.classList.add('hidden');
    errorSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
}

// Utility Functions
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize
console.log('Contra YouTube Recommender loaded');
console.log('Make sure the API server is running at:', apiUrlInput.value);
