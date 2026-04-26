# Open WebUI Setup Guide

## What is Open WebUI?

Open WebUI is a user-friendly, self-hosted web interface for running Large Language Models (LLMs). It provides:

- 🌐 **Web-based Interface**: Modern, intuitive chat interface
- 🔌 **Multiple Backend Support**: Works with Ollama, OpenAI API, and more
- 🔒 **Privacy**: Self-hosted, your data stays local
- 🎨 **Customizable**: Themes, prompts, and model configurations
- 👥 **Multi-user**: User authentication and management
- 📊 **Chat History**: Persistent conversation storage

## Installation

### Option 1: Docker (Recommended)

```bash
# Pull and run Open WebUI with Ollama support
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main
```

### Option 2: Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    ports:
      - "3000:8080"
    volumes:
      - open-webui:/app/backend/data
    extra_hosts:
      - "host.docker.internal:host-gateway"
    restart: always

volumes:
  open-webui:
```

Then run:

```bash
docker-compose up -d
```

### Option 3: Manual Installation

```bash
# Clone the repository
git clone https://github.com/open-webui/open-webui.git
cd open-webui

# Install dependencies
npm install

# Build frontend
npm run build

# Install Python dependencies
cd backend
pip install -r requirements.txt

# Run the server
python main.py
```

## Configuration

### 1. Access Open WebUI

Open your browser and navigate to:
```
http://localhost:3000
```

### 2. Create Admin Account

On first launch, create an admin account:
- Username: admin
- Email: admin@example.com
- Password: (choose a secure password)

### 3. Configure Ollama Connection

1. Go to **Settings** → **Connections**
2. Set Ollama API URL: `http://host.docker.internal:11434` (for Docker)
   - Or `http://localhost:11434` (for local installation)
3. Click **Test Connection**
4. If successful, you'll see available models

### 4. Get API Key

1. Go to **Settings** → **Account**
2. Click **Generate API Key**
3. Copy the API key
4. Add to your `.env` file:

```bash
OPENWEBUI_BASE_URL=http://localhost:3000
OPENWEBUI_API_KEY=your_api_key_here
OPENWEBUI_MODEL=llama3.2:latest
```

## Integration with This Platform

### Update Environment Variables

Edit `.env` file:

```bash
# Switch to Open WebUI backend
AI_BACKEND=openwebui

# Open WebUI Configuration
OPENWEBUI_BASE_URL=http://localhost:3000
OPENWEBUI_API_KEY=sk-xxxxxxxxxxxxx
OPENWEBUI_MODEL=llama3.2:latest
```

### Available Models

Common models you can use:
- `llama3.2:latest` - Latest Llama 3.2 model
- `llama2:latest` - Llama 2 model
- `mistral:latest` - Mistral model
- `codellama:latest` - Code-focused model
- `gemma:latest` - Google's Gemma model

Pull models using Ollama:
```bash
ollama pull llama3.2
ollama pull mistral
```

## Features

### Chat Interface

- **Streaming Responses**: Real-time AI responses
- **Chat History**: Persistent conversation storage
- **Model Switching**: Change models on the fly
- **System Prompts**: Customize AI behavior
- **Multi-turn Conversations**: Context-aware responses

### User Management

- **Authentication**: Secure user login
- **Role-based Access**: Admin, user roles
- **Chat Sharing**: Share conversations with others
- **Privacy Controls**: Control data visibility

### Advanced Features

- **RAG (Retrieval Augmented Generation)**: Upload documents for context
- **Function Calling**: Extend AI capabilities
- **Custom Prompts**: Create reusable prompt templates
- **API Access**: RESTful API for integrations

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to Open WebUI

**Solutions**:
1. Check if Docker container is running:
   ```bash
   docker ps | grep open-webui
   ```

2. Check logs:
   ```bash
   docker logs open-webui
   ```

3. Verify port is not in use:
   ```bash
   lsof -i :3000
   ```

### Ollama Connection Issues

**Problem**: Open WebUI cannot connect to Ollama

**Solutions**:
1. Ensure Ollama is running:
   ```bash
   ollama serve
   ```

2. For Docker, use `host.docker.internal:11434`
3. For local, use `localhost:11434`

### API Key Issues

**Problem**: API authentication fails

**Solutions**:
1. Regenerate API key in Open WebUI settings
2. Update `.env` file with new key
3. Restart the application

## Best Practices

### Security

- ✅ Use strong passwords
- ✅ Keep API keys secret
- ✅ Enable HTTPS in production
- ✅ Regular backups of data volume
- ✅ Update to latest version regularly

### Performance

- ✅ Use GPU-enabled models when available
- ✅ Adjust context length based on needs
- ✅ Monitor resource usage
- ✅ Use appropriate model sizes

### Data Management

- ✅ Regular backups of chat history
- ✅ Clean up old conversations
- ✅ Monitor storage usage
- ✅ Export important conversations

## Resources

- **Official Website**: https://openwebui.com
- **GitHub**: https://github.com/open-webui/open-webui
- **Documentation**: https://docs.openwebui.com
- **Discord Community**: https://discord.gg/5rJgQTnV4s

## Comparison with Other Backends

| Feature | Open WebUI | Ollama | Gemini |
|---------|-----------|--------|--------|
| Self-hosted | ✅ | ✅ | ❌ |
| Web Interface | ✅ | ❌ | ❌ |
| Multi-user | ✅ | ❌ | ❌ |
| Chat History | ✅ | ❌ | ❌ |
| API Access | ✅ | ✅ | ✅ |
| Cost | Free | Free | Paid |
| Privacy | High | High | Medium |

## Next Steps

1. ✅ Install Open WebUI
2. ✅ Configure Ollama connection
3. ✅ Generate API key
4. ✅ Update `.env` file
5. ✅ Restart application
6. ✅ Test chat interface

For more help, check the [official documentation](https://docs.openwebui.com) or ask in the community Discord.
