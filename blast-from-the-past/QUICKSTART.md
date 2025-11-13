# ⚡ Quick Start - Blast from the Past

Get up and running in 10 minutes!

## Step 1: OAuth Setup (5 min)

1. Go to https://console.cloud.google.com/
2. Create new project → Enable **Gmail API**
3. Create OAuth credentials:
   - Go to Credentials → Create OAuth Client ID
   - Type: Chrome Extension (or Web Application)
   - **Copy the Client ID**
4. Update `manifest.json`:
   ```json
   "client_id": "YOUR_CLIENT_ID_HERE.apps.googleusercontent.com"
   ```

## Step 2: Load Extension (2 min)

1. Open Chrome → `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select `blast-from-the-past` folder
5. **Copy the Extension ID** (like: `abcd123...xyz789`)

## Step 3: Update OAuth (2 min)

1. Back to Google Cloud Console → Credentials
2. Edit your OAuth client
3. Add authorized origin:
   ```
   chrome-extension://YOUR_EXTENSION_ID_HERE
   ```
4. Save

## Step 4: Test It! (1 min)

1. Go to https://mail.google.com
2. Click the floating "Blast from the Past" button
3. Grant permissions
4. Enjoy your first memory! 🎉

---

## LLM Setup (Optional)

### Chrome AI (Easiest - Built-in)
No setup needed! Already configured.

### Ollama (Most Private)
```bash
# Install from https://ollama.ai
ollama pull llama2
ollama serve
```

### OpenRouter (Best Quality)
1. Get API key from https://openrouter.ai
2. Extension settings → Select OpenRouter → Paste key

---

## Troubleshooting

**No button in Gmail?**
- Refresh the page
- Check extension is enabled

**OAuth error?**
- Verify client ID in manifest.json
- Check extension ID in OAuth settings

**No old emails?**
- Need emails 1+ year old

---

For detailed instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)

For publishing info, see [README.md](README.md)
