# Open WebUI Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Install Open WebUI (1 minute)

```bash
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main
```

### Step 2: Access Open WebUI (1 minute)

1. Open browser: http://localhost:3000
2. Create admin account (first time only)
3. Go to Settings → Account
4. Click "Generate API Key"
5. Copy the API key

### Step 3: Configure Platform (1 minute)

Edit `.env` file:

```bash
# Change this line
AI_BACKEND=openwebui

# Update this line with your actual API key
OPENWEBUI_API_KEY=sk-your-actual-key-here
```

### Step 4: Start Platform (1 minute)

```bash
streamlit run streamlit_app.py
```

### Step 5: Test Chat (1 minute)

1. Login to platform
2. Click "与大师对话 / Chat with Masters"
3. Check sidebar shows ✅ green checkmark
4. Type a question and press Enter
5. Watch the AI respond!

## ✅ Success Indicators

- ✅ Sidebar shows "✅ Open WebUI 连接正常"
- ✅ Model dropdown shows available models
- ✅ Chat input is active
- ✅ Messages appear in chat history
- ✅ AI responds to your questions

## ❌ Common Issues

### Issue: Connection Failed

**Fix**: Check if Open WebUI is running
```bash
docker ps | grep open-webui
```

If not running, start it:
```bash
docker start open-webui
```

### Issue: No Models Available

**Fix**: Pull a model using Ollama
```bash
ollama pull llama3.2
```

### Issue: API Key Error

**Fix**: Regenerate API key in Open WebUI and update `.env`

## 🎯 Quick Commands

```bash
# Check Open WebUI status
docker ps | grep open-webui

# View Open WebUI logs
docker logs open-webui

# Restart Open WebUI
docker restart open-webui

# Stop Open WebUI
docker stop open-webui

# Start Open WebUI
docker start open-webui

# Pull new model
ollama pull llama3.2

# List available models
ollama list
```

## 📝 Default Configuration

```bash
OPENWEBUI_BASE_URL=http://localhost:3000
OPENWEBUI_API_KEY=your_api_key_here
OPENWEBUI_MODEL=llama3.2:latest
```

## 🔗 Useful Links

- Open WebUI: http://localhost:3000
- Platform: http://localhost:8501
- Setup Guide: `docs/openwebui_setup_guide.md`
- Full Documentation: `docs/openwebui_integration_summary.md`

## 💡 Tips

1. **First Time**: Create admin account in Open WebUI before generating API key
2. **Models**: Pull models using `ollama pull <model-name>` before using
3. **Performance**: Use smaller models (llama3.2) for faster responses
4. **Privacy**: All data stays on your machine - nothing sent to cloud
5. **Backup**: Chat history is stored in Docker volume `open-webui`

## 🆘 Need Help?

1. Check logs: `docker logs open-webui`
2. Read full guide: `docs/openwebui_setup_guide.md`
3. Verify configuration in `.env` file
4. Ensure Ollama is running: `ollama serve`

---

**Ready to chat?** Follow the 5 steps above and start exploring! 🚀
