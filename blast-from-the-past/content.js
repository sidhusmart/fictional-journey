// Content script to inject Blast from the Past button into Gmail

let storyOverlay = null;

// Create the floating button
function createBlastButton() {
  const button = document.createElement('button');
  button.id = 'blast-from-past-btn';
  button.innerHTML = `
    <svg viewBox="0 0 24 24" width="24" height="24" fill="white">
      <path d="M13,3A9,9 0 0,0 4,12H1L4.89,15.89L4.96,16.03L9,12H6A7,7 0 0,1 13,5A7,7 0 0,1 20,12A7,7 0 0,1 13,19C11.07,19 9.32,18.21 8.06,16.94L6.64,18.36C8.27,20 10.5,21 13,21A9,9 0 0,0 22,12A9,9 0 0,0 13,3M12,8V13L16.28,15.54L17,14.33L13.5,12.25V8H12Z"/>
    </svg>
    <span>Blast from the Past</span>
  `;
  button.title = 'View a memory from your old emails';

  button.addEventListener('click', openStory);

  document.body.appendChild(button);
}

// Open the story overlay
async function openStory() {
  if (storyOverlay) {
    storyOverlay.remove();
  }

  // Create overlay
  storyOverlay = document.createElement('div');
  storyOverlay.id = 'blast-story-overlay';
  storyOverlay.innerHTML = `
    <div class="blast-story-container">
      <div class="blast-story-header">
        <div class="blast-story-title">Blast from the Past</div>
        <button class="blast-story-close" title="Close">&times;</button>
      </div>
      <div class="blast-story-content">
        <div class="blast-loading">
          <div class="blast-spinner"></div>
          <p>Finding a memory...</p>
        </div>
      </div>
    </div>
  `;

  document.body.appendChild(storyOverlay);

  // Close button
  const closeBtn = storyOverlay.querySelector('.blast-story-close');
  closeBtn.addEventListener('click', () => {
    storyOverlay.remove();
    storyOverlay = null;
  });

  // Close on background click
  storyOverlay.addEventListener('click', (e) => {
    if (e.target === storyOverlay) {
      storyOverlay.remove();
      storyOverlay = null;
    }
  });

  // Fetch and display story
  try {
    await displayStory();
  } catch (error) {
    showError(error.message);
  }
}

// Display the story
async function displayStory() {
  // Get random old email
  const response = await chrome.runtime.sendMessage({ action: 'getRandomOldEmail' });

  if (response.error) {
    throw new Error(response.error);
  }

  const email = response.email;

  // Process with LLM to create story content
  const storyData = await processEmailWithLLM(email);

  // Display stage 1: teaser
  displayStage1(storyData);
}

// Process email with LLM to extract interesting content
async function processEmailWithLLM(email) {
  const settings = await chrome.storage.sync.get(['llmProvider', 'apiKey', 'ollamaUrl']);
  const provider = settings.llmProvider || 'chrome';

  const prompt = `You are analyzing an old email to create a nostalgic memory snippet.

Email Subject: ${email.subject}
From: ${email.from}
Date: ${email.date}
Body: ${email.body.substring(0, 2000)}

Create a JSON response with:
1. "teaser": A 1-2 sentence intriguing snippet from the email that makes someone think "what was this about?"
2. "participants": Array of participant names (not email addresses)
3. "context": A 2-3 sentence explanation providing context about what this email was about
4. "sentiment": The emotional tone (nostalgic/funny/important/casual)

Make it engaging and nostalgic. Use the exact words from the email in the teaser.

Respond with valid JSON only.`;

  let result;

  try {
    if (provider === 'chrome') {
      result = await useChromeAI(prompt);
    } else if (provider === 'openrouter') {
      result = await useOpenRouter(prompt, settings.apiKey);
    } else if (provider === 'ollama') {
      result = await useOllama(prompt, settings.ollamaUrl);
    } else if (provider === 'custom') {
      result = await useCustomAPI(prompt, settings.apiKey);
    } else {
      throw new Error('No LLM provider configured');
    }

    const parsed = JSON.parse(result);
    return {
      ...parsed,
      originalEmail: email
    };
  } catch (error) {
    console.error('LLM processing failed, using fallback:', error);
    // Fallback: use basic extraction
    return createFallbackStory(email);
  }
}

// Fallback story creation without LLM
function createFallbackStory(email) {
  const sentences = email.body.split(/[.!?]+/).filter(s => s.trim().length > 20);
  const teaser = sentences[0] || email.subject;

  return {
    teaser: teaser.trim(),
    participants: email.participants.slice(0, 3),
    context: `This email was about: ${email.subject}. It was sent on ${new Date(email.date).toLocaleDateString()}.`,
    sentiment: 'nostalgic',
    originalEmail: email
  };
}

// Chrome AI implementation
async function useChromeAI(prompt) {
  if (!window.ai || !window.ai.languageModel) {
    throw new Error('Chrome AI not available');
  }

  const session = await window.ai.languageModel.create();
  const result = await session.prompt(prompt);
  session.destroy();

  return result;
}

// OpenRouter implementation
async function useOpenRouter(prompt, apiKey) {
  if (!apiKey) {
    throw new Error('OpenRouter API key not configured');
  }

  const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`,
      'HTTP-Referer': window.location.href
    },
    body: JSON.stringify({
      model: 'google/gemini-flash-1.5',
      messages: [{ role: 'user', content: prompt }]
    })
  });

  const data = await response.json();
  return data.choices[0].message.content;
}

// Ollama implementation
async function useOllama(prompt, ollamaUrl) {
  const url = ollamaUrl || 'http://localhost:11434';

  const response = await fetch(`${url}/api/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: 'llama2',
      prompt: prompt,
      stream: false
    })
  });

  const data = await response.json();
  return data.response;
}

// Custom API implementation (OpenAI-compatible)
async function useCustomAPI(prompt, apiKey) {
  if (!apiKey) {
    throw new Error('API key not configured');
  }

  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`
    },
    body: JSON.stringify({
      model: 'gpt-3.5-turbo',
      messages: [{ role: 'user', content: prompt }]
    })
  });

  const data = await response.json();
  return data.choices[0].message.content;
}

// Display Stage 1: Teaser
function displayStage1(storyData) {
  const container = storyOverlay.querySelector('.blast-story-content');

  const gradients = [
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    'linear-gradient(135deg, #30cfd0 0%, #330867 100%)'
  ];

  const gradient = gradients[Math.floor(Math.random() * gradients.length)];

  container.innerHTML = `
    <div class="blast-stage blast-stage-1" style="background: ${gradient}">
      <div class="blast-stage-content">
        <div class="blast-participants">
          ${storyData.participants.map(p => `<span class="participant-tag">${p}</span>`).join('')}
        </div>
        <div class="blast-teaser">
          "${storyData.teaser}"
        </div>
        <div class="blast-prompt">
          Can you remember what this was about?
        </div>
        <button class="blast-reveal-btn">Reveal Memory</button>
      </div>
      <div class="blast-date">${new Date(storyData.originalEmail.date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</div>
    </div>
  `;

  // Reveal button
  const revealBtn = container.querySelector('.blast-reveal-btn');
  revealBtn.addEventListener('click', () => {
    displayStage2(storyData, gradient);
  });
}

// Display Stage 2: Full context
function displayStage2(storyData, gradient) {
  const container = storyOverlay.querySelector('.blast-story-content');

  container.innerHTML = `
    <div class="blast-stage blast-stage-2" style="background: ${gradient}">
      <div class="blast-stage-content">
        <div class="blast-context-title">The Full Story</div>
        <div class="blast-context">
          ${storyData.context}
        </div>
        <div class="blast-email-details">
          <div class="blast-email-subject">
            <strong>Subject:</strong> ${storyData.originalEmail.subject}
          </div>
          <div class="blast-email-from">
            <strong>From:</strong> ${storyData.originalEmail.from}
          </div>
        </div>
        <button class="blast-view-email-btn">View Full Email in Gmail</button>
        <button class="blast-another-btn">Show Another Memory</button>
      </div>
    </div>
  `;

  // View email button
  const viewBtn = container.querySelector('.blast-view-email-btn');
  viewBtn.addEventListener('click', () => {
    window.location.href = `https://mail.google.com/mail/u/0/#all/${storyData.originalEmail.id}`;
  });

  // Another memory button
  const anotherBtn = container.querySelector('.blast-another-btn');
  anotherBtn.addEventListener('click', () => {
    displayStory();
  });
}

// Show error
function showError(message) {
  const container = storyOverlay.querySelector('.blast-story-content');
  container.innerHTML = `
    <div class="blast-error">
      <div class="blast-error-icon">⚠️</div>
      <div class="blast-error-message">${message}</div>
      <button class="blast-error-btn" onclick="window.location.reload()">Close</button>
    </div>
  `;
}

// Initialize when Gmail loads
function init() {
  // Wait for Gmail to load
  const checkGmail = setInterval(() => {
    if (document.querySelector('[role="navigation"]') || document.querySelector('.aeN')) {
      clearInterval(checkGmail);
      createBlastButton();
    }
  }, 1000);

  // Cleanup after 30 seconds
  setTimeout(() => clearInterval(checkGmail), 30000);
}

// Start
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
