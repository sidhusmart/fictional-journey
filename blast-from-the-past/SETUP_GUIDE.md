# 🚀 Setup Guide - Blast from the Past

This guide will walk you through setting up the extension step by step.

## Part 1: Generate Icons (5 minutes)

You need icon files before loading the extension. Choose one method:

### Method A: Using Python Script (Recommended)

```bash
# Install Pillow if you don't have it
pip install Pillow

# Generate icons
python generate_icons.py
```

This will create:
- `icons/icon16.png`
- `icons/icon48.png`
- `icons/icon128.png`

### Method B: Using Browser (No Python needed)

1. Open `icons/generate-icons.html` in your browser
2. Click "Download All"
3. Save the three files in the `icons/` folder:
   - icon16.png
   - icon48.png
   - icon128.png

### Method C: Manual Creation

If you have graphic design skills, create three PNG icons (16x16, 48x48, 128x128) with a clock/time-travel theme.

---

## Part 2: Google Cloud Setup (15 minutes)

### Step 1: Create Google Cloud Project

1. Go to https://console.cloud.google.com/
2. Click "Select a project" → "New Project"
3. Name it "Blast from Past" or similar
4. Click "Create"

### Step 2: Enable Gmail API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Gmail API"
3. Click on it, then click "Enable"
4. Wait for it to enable (usually instant)

### Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Choose "External" (unless you have Google Workspace)
3. Click "Create"
4. Fill in required fields:
   - **App name**: Blast from the Past
   - **User support email**: Your email
   - **Developer contact**: Your email
5. Click "Save and Continue"
6. Scopes: Click "Add or Remove Scopes"
   - Search for "Gmail API"
   - Select: `.../auth/gmail.readonly`
   - Click "Update"
7. Click "Save and Continue"
8. Test users: Add your Gmail address
9. Click "Save and Continue"

### Step 4: Create OAuth Credentials (PART 1)

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Application type: **Choose "Chrome Extension"** (or Web application if Chrome Extension is not available)
4. Name: "Blast from the Past Extension"
5. **IMPORTANT**: Leave "Authorized JavaScript origins" empty for now
6. Click "Create"
7. **Copy the Client ID** - you'll need it next!

---

## Part 3: Update Extension Files (2 minutes)

### Update manifest.json

1. Open `manifest.json` in a text editor
2. Find this line:
   ```json
   "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
   ```
3. Replace `YOUR_CLIENT_ID` with the Client ID you copied
4. Save the file

Example:
```json
"client_id": "123456789-abc123def456.apps.googleusercontent.com",
```

---

## Part 4: Load Extension in Chrome (5 minutes)

### Step 1: Load Unpacked Extension

1. Open Chrome
2. Go to `chrome://extensions/`
3. Enable "Developer mode" (toggle in top-right corner)
4. Click "Load unpacked"
5. Navigate to and select the `blast-from-the-past` folder
6. Click "Select Folder"

### Step 2: Get Extension ID

1. The extension should now appear in your extensions list
2. Find "Blast from the Past"
3. Look for the **ID** field (looks like: `abcdefghijklmnopqrstuvwxyz123456`)
4. **Copy this ID** - you need it for the next step!

---

## Part 5: Update OAuth Credentials (PART 2) (3 minutes)

Now we need to tell Google about your extension:

1. Go back to Google Cloud Console
2. Go to "APIs & Services" → "Credentials"
3. Click on your OAuth client (the one you created)
4. Under "Authorized JavaScript origins", click "Add URI"
5. Add: `chrome-extension://YOUR_EXTENSION_ID`
   - Replace `YOUR_EXTENSION_ID` with the ID you copied
   - Example: `chrome-extension://abcdefghijklmnopqrstuvwxyz123456`
6. Click "Save"

---

## Part 6: Configure LLM Settings (5 minutes)

### Chrome AI (Easiest, Most Private)

1. Make sure you have Chrome 128 or later
2. Check `chrome://version` to see your version
3. Go to `chrome://flags`
4. Search for "ai" or "gemini nano"
5. Enable relevant AI flags if available
6. Restart Chrome
7. **No additional setup needed** - just select "Chrome AI" in settings

### Ollama (Private, Local)

1. Install Ollama from https://ollama.ai
2. Open terminal and run:
   ```bash
   ollama pull llama2
   ollama serve
   ```
3. In extension settings, select "Ollama"
4. Use default URL: `http://localhost:11434`

### OpenRouter (Best Quality)

1. Go to https://openrouter.ai
2. Sign up for an account
3. Add credits (starts at $5)
4. Copy your API key
5. In extension settings, select "OpenRouter"
6. Paste your API key
7. Save settings

### Custom API (OpenAI, etc.)

1. Get an API key from OpenAI or compatible service
2. In extension settings, select "Custom API"
3. Paste your API key
4. Save settings

---

## Part 7: Test the Extension (2 minutes)

### First Test

1. Go to https://mail.google.com
2. You should see a floating button "Blast from the Past" (bottom-right)
3. Click it
4. Grant permissions when prompted
5. Wait for it to fetch an old email
6. Enjoy your first memory! 🎉

### Troubleshooting

If the button doesn't appear:
- Refresh Gmail
- Check if extension is enabled in `chrome://extensions/`
- Open console (F12) and check for errors

If authentication fails:
- Double-check OAuth client ID in manifest.json
- Verify Gmail API is enabled
- Make sure extension ID matches in OAuth credentials

If no emails found:
- Make sure you have emails older than 1 year
- Check Gmail permissions were granted

---

## Part 8: OAuth Verification for Publishing (Optional, 4-6 weeks)

If you want to publish to Chrome Web Store:

### Prepare for Verification

1. Create a privacy policy (see README.md for template)
2. Host it publicly (GitHub Pages works great)
3. Create a YouTube video showing:
   - How the extension works
   - What data it accesses
   - Privacy controls available
   - Settings and configuration

### Submit for Verification

1. Go to Google Cloud Console
2. Navigate to OAuth consent screen
3. Click "Publish App"
4. Fill out verification form:
   - Add privacy policy URL
   - Add YouTube demo video
   - Explain data usage
   - Justify scopes needed
5. Submit for review

### Timeline

- **Initial review**: 1-2 weeks
- **Additional questions**: 1-2 weeks
- **Final approval**: 1-2 weeks
- **Total time**: 4-6 weeks typically

---

## Quick Reference

### File Checklist

Before loading extension, ensure you have:

- ✅ `icons/icon16.png`
- ✅ `icons/icon48.png`
- ✅ `icons/icon128.png`
- ✅ `manifest.json` with your OAuth client ID
- ✅ All other files from repository

### URLs You'll Need

- **Google Cloud Console**: https://console.cloud.google.com/
- **Chrome Extensions**: chrome://extensions/
- **Gmail**: https://mail.google.com
- **Ollama**: https://ollama.ai
- **OpenRouter**: https://openrouter.ai

### Common Issues

| Issue | Solution |
|-------|----------|
| Icons missing | Run `python generate_icons.py` or use HTML generator |
| OAuth errors | Check client ID in manifest.json |
| No button in Gmail | Refresh page, check extension is enabled |
| LLM not working | Check settings, verify API key or local service |
| No old emails | Need emails 1+ year old in your Gmail |

---

## Next Steps

Once everything is working:

1. ⭐ Use it daily to rediscover memories
2. 🎨 Customize colors and gradients (see README)
3. 🚀 Consider publishing to Chrome Web Store
4. 🤝 Share with friends and family
5. 💡 Suggest improvements or contribute

---

**Need Help?**

- Check the main README.md
- Review troubleshooting section
- Check browser console for errors
- Verify all setup steps completed

Enjoy your blast from the past! 📧✨
