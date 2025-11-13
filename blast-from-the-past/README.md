# ⏰ Blast from the Past

A beautiful Gmail extension that helps you rediscover old emails as nostalgic memories, presented in an Instagram Stories-style interface. Just like Google Photos shows photo memories, this extension shows email memories from your past.

![Blast from the Past Preview](https://img.shields.io/badge/status-ready-brightgreen)
![Chrome Extension](https://img.shields.io/badge/chrome-extension-blue)
![Privacy First](https://img.shields.io/badge/privacy-first-green)

## ✨ Features

- 📧 **Random Old Email Selection** - Automatically picks emails from 1+ year ago
- 🎨 **Beautiful Story UI** - Instagram-style presentation with gradients and animations
- 🔒 **Privacy-Focused** - Multiple LLM options including local processing
- 🤖 **Smart Content** - Uses AI to extract interesting snippets from emails
- 👥 **Participant Display** - Shows who was involved in the conversation
- 📱 **Two-Stage Reveal** - Teaser first, then full context
- ⚡ **Seamless Gmail Integration** - Works directly within Gmail interface

## 🚀 Quick Start

### Prerequisites

- Google Chrome 128+ (for Chrome AI features)
- A Gmail account
- Optional: Ollama installed locally for private AI processing

### Installation Steps

#### 1. Generate Icons

First, you need to generate the icon files:

1. Open `icons/generate-icons.html` in your browser
2. Click "Download All" button
3. Save the three files as:
   - `icons/icon16.png`
   - `icons/icon48.png`
   - `icons/icon128.png`

#### 2. Set Up Google OAuth

To access Gmail API, you need to create OAuth credentials:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing one)
3. Enable **Gmail API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Chrome Extension" as application type
   - Add your extension ID (you'll get this after loading the extension)
   - Download the credentials
5. Update `manifest.json`:
   - Replace `YOUR_CLIENT_ID.apps.googleusercontent.com` with your actual OAuth client ID

#### 3. Load the Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `blast-from-the-past` folder
5. Note the Extension ID that appears
6. Go back to Google Cloud Console and add this Extension ID to your OAuth credentials

#### 4. Configure Settings

1. Click the extension icon in Chrome toolbar
2. Click "Settings"
3. Choose your preferred LLM provider:
   - **Chrome AI** (recommended): No setup needed, completely private
   - **Ollama**: Install [Ollama](https://ollama.ai) and run `ollama run llama2`
   - **OpenRouter**: Get API key from [openrouter.ai](https://openrouter.ai)
   - **Custom API**: Use your own OpenAI or compatible API key
4. Save settings

#### 5. Use the Extension

1. Go to [Gmail](https://mail.google.com)
2. Look for the floating "Blast from the Past" button (bottom right)
3. Click it to view a random old email as a beautiful memory!

## 🔧 Configuration Options

### LLM Providers

The extension supports multiple LLM providers, giving you flexibility based on your privacy and performance needs:

#### 1. Chrome Built-in AI (Recommended)
- **Privacy**: ⭐⭐⭐⭐⭐ (Completely local)
- **Cost**: Free
- **Setup**: None required (Chrome 128+)
- **Best for**: Maximum privacy, no API keys needed

#### 2. Ollama (Local)
- **Privacy**: ⭐⭐⭐⭐⭐ (Completely local)
- **Cost**: Free
- **Setup**: Install Ollama, download model
- **Best for**: Advanced users who want local AI control

#### 3. OpenRouter
- **Privacy**: ⭐⭐⭐ (Processes on cloud)
- **Cost**: Pay per use (very affordable)
- **Setup**: API key required
- **Best for**: Best AI quality, multiple models

#### 4. Custom API (OpenAI, etc.)
- **Privacy**: ⭐⭐⭐ (Processes on cloud)
- **Cost**: Depends on provider
- **Setup**: API key required
- **Best for**: If you already have an OpenAI account

## 🎨 How It Works

1. **Email Fetching**: Extension uses Gmail API to fetch emails older than 1 year
2. **Random Selection**: Randomly picks one email from the results
3. **AI Processing**: Sends email to your chosen LLM to extract:
   - An intriguing teaser sentence
   - Participant names
   - Context and explanation
   - Emotional sentiment
4. **Story Display**: Shows the content in two stages:
   - **Stage 1**: Teaser with "Can you remember what this was about?"
   - **Stage 2**: Full context and link to original email

## 📦 Publishing to Chrome Web Store

### Costs
- **One-time fee**: $5 developer registration
- **No recurring costs**: Free to publish after registration

### Approval Process

The Chrome Web Store review process typically takes **1-3 business days**. Your extension will be reviewed for:

- Security and privacy compliance
- Proper OAuth implementation
- Clear privacy policy
- Appropriate permissions usage

### Publishing Steps

1. **Prepare for Submission**
   ```bash
   # Remove any development files
   rm -rf .git node_modules

   # Create a zip file
   zip -r blast-from-past-v1.0.0.zip blast-from-the-past/
   ```

2. **Register as Developer**
   - Go to [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole/)
   - Pay the $5 one-time registration fee
   - Complete your developer account setup

3. **Create Privacy Policy**

   You **must** create a privacy policy. Here's a template:

   ```markdown
   # Privacy Policy for Blast from the Past

   ## Data Collection
   - We access your Gmail emails to show you memories
   - Email content is processed based on your chosen LLM provider
   - No data is stored on our servers

   ## LLM Processing
   - Chrome AI: All processing is local, no data leaves your device
   - Ollama: All processing is local, no data leaves your device
   - OpenRouter/Custom API: Email content is sent to third-party APIs for processing

   ## Data Usage
   - Email data is only used to generate memory snippets
   - No emails are stored or transmitted except for AI processing
   - No analytics or tracking

   ## Third-Party Services
   - Gmail API (Google): Used to read emails
   - OpenRouter/OpenAI (optional): Used for AI processing if selected

   ## User Control
   - You can revoke access at any time via Google account settings
   - You can choose which LLM provider to use
   - You can uninstall the extension anytime
   ```

   Host this on GitHub Pages, your website, or use a service like [PrivacyPolicies.com](https://www.privacypolicies.com/).

4. **Upload Extension**
   - Click "New Item" in Developer Dashboard
   - Upload your zip file
   - Fill in required information:
     - Name: Blast from the Past
     - Description: Rediscover your old emails as beautiful memories
     - Category: Productivity
     - Language: English
     - Screenshots: Take 3-5 screenshots of the extension in action
     - Icon: Use the 128x128 icon
     - Promotional tile: Create a 440x280 image
     - Privacy policy URL: Your hosted privacy policy
     - Permissions justification: Explain why you need Gmail access

5. **OAuth Verification**

   Since you're using Gmail API, you'll need to complete OAuth verification:

   - Submit your OAuth consent screen for verification
   - Provide a YouTube video demonstrating the extension
   - Explain data access and usage
   - This can take 4-6 weeks for approval

6. **Submit for Review**
   - Click "Submit for Review"
   - Wait for approval (usually 1-3 business days)
   - Respond promptly to any reviewer questions

### After Approval

Once approved:
- Your extension will be live on Chrome Web Store
- Users can install it directly from the store
- You can publish updates anytime
- Updates are typically reviewed within 24-48 hours

## 🔐 Security & Privacy

### Permissions Explained

- **`gmail.readonly`**: Required to read your emails (read-only access)
- **`storage`**: Saves your LLM preferences locally
- **`identity`**: Handles Gmail OAuth authentication

### Data Privacy

- **Chrome AI & Ollama**: Your emails never leave your computer
- **Cloud APIs**: Only the specific email being processed is sent to the API
- **No Storage**: We don't store any of your emails or data
- **No Analytics**: No tracking or usage analytics

### Security Best Practices

- All API communication uses HTTPS
- OAuth tokens are securely managed by Chrome
- Minimal permissions requested
- Open source - you can review all code

## 🛠️ Development

### Project Structure

```
blast-from-the-past/
├── manifest.json          # Extension manifest
├── background.js          # Gmail API integration
├── content.js            # Gmail UI integration & LLM processing
├── styles.css            # Story UI styles
├── popup.html            # Extension popup
├── popup.js              # Popup logic
├── options.html          # Settings page
├── options.js            # Settings logic
├── icons/                # Extension icons
│   ├── icon16.png
│   ├── icon48.png
│   ├── icon128.png
│   ├── icon.svg
│   └── generate-icons.html
└── README.md             # This file
```

### Key Files

- **`background.js`**: Handles Gmail API calls, OAuth, email fetching
- **`content.js`**: Injects UI into Gmail, handles LLM processing
- **`styles.css`**: Beautiful Instagram-style UI with animations
- **`options.html/js`**: Settings page for LLM configuration

### Customization

#### Change Email Age Filter

In `background.js`, modify the age filter:

```javascript
const ONE_YEAR_MS = 365 * 24 * 60 * 60 * 1000; // Change this value
```

#### Customize UI Colors

In `styles.css`, change the gradient colors:

```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

#### Modify LLM Prompt

In `content.js`, find the `processEmailWithLLM` function and customize the prompt.

## 🐛 Troubleshooting

### "No old emails found"

- Make sure you have emails older than 1 year
- Check that Gmail API is enabled
- Verify OAuth credentials are correct

### Chrome AI not available

- Update Chrome to version 128+
- Enable AI features in `chrome://flags`
- Try using Ollama or cloud options instead

### OAuth errors

- Verify your OAuth client ID in manifest.json
- Make sure Gmail API is enabled in Google Cloud Console
- Check that extension ID matches in OAuth settings

### LLM processing fails

- Check your API key is correct
- Verify internet connection (for cloud APIs)
- Try switching to Chrome AI or Ollama
- Check browser console for error messages

## 🤝 Contributing

This is an open-source project. Contributions are welcome!

### Ideas for Improvements

- [ ] Multiple memory view in one session
- [ ] Favorite/save memories
- [ ] Share memories (with privacy controls)
- [ ] Filter by sender or date range
- [ ] Dark mode support
- [ ] More story templates and themes
- [ ] Email thread context
- [ ] Notification reminders

## 📄 License

MIT License - feel free to use and modify as needed.

## 🙏 Acknowledgments

- Inspired by Google Photos Memories
- Built with Chrome Extension Manifest V3
- UI inspired by Instagram Stories

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review [Chrome Extension documentation](https://developer.chrome.com/docs/extensions/)
3. Check [Gmail API documentation](https://developers.google.com/gmail/api)

---

**Made with ❤️ for nostalgia**

Enjoy rediscovering your email memories! 📧✨
