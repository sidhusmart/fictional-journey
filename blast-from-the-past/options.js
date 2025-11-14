// Options page script

document.addEventListener('DOMContentLoaded', async () => {
  // Load saved settings
  const settings = await chrome.storage.sync.get(['llmProvider', 'apiKey', 'ollamaUrl']);

  // Set provider
  const provider = settings.llmProvider || 'chrome';
  document.querySelector(`input[value="${provider}"]`).checked = true;
  updateSelectedOption(provider);

  // Set API keys
  if (settings.apiKey) {
    if (provider === 'openrouter') {
      document.getElementById('openrouterKey').value = settings.apiKey;
    } else if (provider === 'custom') {
      document.getElementById('customKey').value = settings.apiKey;
    }
  }

  if (settings.ollamaUrl) {
    document.getElementById('ollamaUrl').value = settings.ollamaUrl;
  }

  // Radio option change
  document.querySelectorAll('input[name="llmProvider"]').forEach(radio => {
    radio.addEventListener('change', (e) => {
      updateSelectedOption(e.target.value);
    });
  });

  // Click on label to select
  document.querySelectorAll('.radio-option').forEach(option => {
    option.addEventListener('click', (e) => {
      if (e.target.tagName !== 'INPUT' && e.target.tagName !== 'A') {
        const radio = option.querySelector('input[type="radio"]');
        radio.checked = true;
        updateSelectedOption(radio.value);
      }
    });
  });

  // Save button
  document.getElementById('saveBtn').addEventListener('click', saveSettings);

  // Reset button
  document.getElementById('resetBtn').addEventListener('click', resetSettings);
});

function updateSelectedOption(provider) {
  // Update visual selection
  document.querySelectorAll('.radio-option').forEach(option => {
    option.classList.remove('selected');
  });
  document.querySelector(`[data-provider="${provider}"]`).classList.add('selected');

  // Show/hide input fields
  document.getElementById('ollamaInput').style.display = provider === 'ollama' ? 'block' : 'none';
  document.getElementById('openrouterInput').style.display = provider === 'openrouter' ? 'block' : 'none';
  document.getElementById('customInput').style.display = provider === 'custom' ? 'block' : 'none';
}

async function saveSettings() {
  const provider = document.querySelector('input[name="llmProvider"]:checked').value;
  let apiKey = '';
  let ollamaUrl = '';

  if (provider === 'openrouter') {
    apiKey = document.getElementById('openrouterKey').value.trim();
    if (!apiKey) {
      showStatus('Please enter your OpenRouter API key', 'error');
      return;
    }
  } else if (provider === 'custom') {
    apiKey = document.getElementById('customKey').value.trim();
    if (!apiKey) {
      showStatus('Please enter your API key', 'error');
      return;
    }
  } else if (provider === 'ollama') {
    ollamaUrl = document.getElementById('ollamaUrl').value.trim() || 'http://localhost:11434';
  }

  try {
    await chrome.storage.sync.set({
      llmProvider: provider,
      apiKey: apiKey,
      ollamaUrl: ollamaUrl
    });

    showStatus('Settings saved successfully!', 'success');

    // Hide success message after 3 seconds
    setTimeout(() => {
      hideStatus();
    }, 3000);
  } catch (error) {
    showStatus('Error saving settings: ' + error.message, 'error');
  }
}

async function resetSettings() {
  if (confirm('Reset all settings to default?')) {
    await chrome.storage.sync.clear();

    // Reset UI
    document.querySelector('input[value="chrome"]').checked = true;
    updateSelectedOption('chrome');
    document.getElementById('openrouterKey').value = '';
    document.getElementById('customKey').value = '';
    document.getElementById('ollamaUrl').value = '';

    showStatus('Settings reset to default', 'success');

    setTimeout(() => {
      hideStatus();
    }, 3000);
  }
}

function showStatus(message, type) {
  const statusEl = document.getElementById('statusMessage');
  statusEl.textContent = message;
  statusEl.className = `status-message ${type}`;
}

function hideStatus() {
  const statusEl = document.getElementById('statusMessage');
  statusEl.className = 'status-message';
}
