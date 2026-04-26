# Open WebUI Integration Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     广告思想简史 Platform                          │
│                    (Streamlit Application)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────┐         ┌──────────────────┐               │
│  │  streamlit_app │────────▶│ chat_openwebui   │               │
│  │     .py        │         │      .py         │               │
│  └────────────────┘         └──────────────────┘               │
│         │                            │                          │
│         │                            │                          │
│         ▼                            ▼                          │
│  ┌────────────────────────────────────────────┐                │
│  │         Navigation Menu                     │                │
│  │  - 首页 / Home                              │                │
│  │  - 搜索 / Search                            │                │
│  │  - 广告大事年表 / Timeline                   │                │
│  │  - 20世纪广告百位巨星榜 / Top 100 Stars      │                │
│  │  - 与大师对话 / Chat with Masters ◄─────────┼────────┐       │
│  │  - 行业数据 / Industry Data                 │        │       │
│  └────────────────────────────────────────────┘        │       │
│                                                         │       │
└─────────────────────────────────────────────────────────┼───────┘
                                                          │
                                                          │
                    ┌─────────────────────────────────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │   OpenWebUIChat      │
         │      Class           │
         ├──────────────────────┤
         │ - check_connection() │
         │ - get_models()       │
         │ - generate_response()│
         │ - stream_response()  │
         └──────────────────────┘
                    │
                    │ HTTP/REST API
                    │ (OpenAI-compatible)
                    ▼
         ┌──────────────────────┐
         │    Open WebUI        │
         │   (Docker Container) │
         │   Port: 3000         │
         ├──────────────────────┤
         │ - Web Interface      │
         │ - API Server         │
         │ - User Management    │
         │ - Chat History       │
         └──────────────────────┘
                    │
                    │ Ollama API
                    │
                    ▼
         ┌──────────────────────┐
         │      Ollama          │
         │   (Local Service)    │
         │   Port: 11434        │
         ├──────────────────────┤
         │ - Model Management   │
         │ - Inference Engine   │
         │ - GPU Acceleration   │
         └──────────────────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │   LLM Models         │
         │ - llama3.2:latest    │
         │ - mistral:latest     │
         │ - codellama:latest   │
         │ - gemma:latest       │
         └──────────────────────┘
```

## Data Flow

### 1. User Sends Message

```
User Input
    │
    ▼
Streamlit Chat Input
    │
    ▼
chat_interface() function
    │
    ▼
append_message("user", prompt)
    │
    ▼
Session State (st.session_state.openwebui_messages)
```

### 2. AI Response Generation

```
OpenWebUIChat.stream_response()
    │
    ▼
Build message context
    │
    ├─ System Prompt
    ├─ Chat History (last 10 messages)
    └─ Current User Message
    │
    ▼
HTTP POST to Open WebUI
    │
    └─ URL: http://localhost:3000/api/chat/completions
    └─ Headers: Authorization: Bearer {API_KEY}
    └─ Body: {model, messages, stream: true}
    │
    ▼
Open WebUI processes request
    │
    ▼
Forward to Ollama
    │
    └─ URL: http://host.docker.internal:11434/api/generate
    │
    ▼
Ollama runs inference
    │
    ▼
Stream response chunks back
    │
    ▼
Parse SSE (Server-Sent Events)
    │
    └─ data: {"choices": [{"delta": {"content": "..."}}]}
    │
    ▼
Yield content chunks
    │
    ▼
Streamlit displays in real-time
    │
    ▼
append_message("assistant", full_response)
```

## Component Responsibilities

### Streamlit Application (`streamlit_app.py`)

**Responsibilities**:
- User authentication and session management
- Navigation and routing
- Page rendering
- Integration of all modules

**Key Functions**:
- `main()` - Application entry point
- `show_login_page()` - Authentication UI
- `get_navigation_menu()` - Role-based menu

### Chat Module (`chat_openwebui.py`)

**Responsibilities**:
- Open WebUI API client
- Chat interface rendering
- Message history management
- Model selection UI

**Key Classes/Functions**:
- `OpenWebUIChat` - API client class
- `chat_interface()` - Main chat UI
- `initialize_session_state()` - Session setup
- `show_model_selector()` - Model selection UI

### Open WebUI (Docker Container)

**Responsibilities**:
- Web-based chat interface
- User authentication and management
- Chat history persistence
- API gateway to Ollama
- Model management UI

**Key Features**:
- OpenAI-compatible API
- Multi-user support
- Persistent storage
- Web UI for configuration

### Ollama (Local Service)

**Responsibilities**:
- LLM model hosting
- Inference execution
- GPU acceleration
- Model downloading and management

**Key Features**:
- Multiple model support
- Efficient inference
- REST API
- Model quantization

## Configuration Flow

```
.env file
    │
    ├─ AI_BACKEND=openwebui
    ├─ OPENWEBUI_BASE_URL=http://localhost:3000
    ├─ OPENWEBUI_API_KEY=sk-xxxxx
    └─ OPENWEBUI_MODEL=llama3.2:latest
    │
    ▼
os.getenv() in chat_openwebui.py
    │
    ▼
OpenWebUIChat.__init__()
    │
    ├─ self.base_url
    ├─ self.api_key
    ├─ self.model
    └─ self.headers
    │
    ▼
Used in API calls
```

## Session State Management

```python
st.session_state = {
    # Authentication
    'authentication_status': True,
    'username': 'student',
    'name': 'Student User',
    'user_role': 'student',
    
    # Chat
    'openwebui_client': OpenWebUIChat(),
    'openwebui_messages': [
        {
            'role': 'user',
            'content': 'Hello',
            'timestamp': '2026-01-19T10:30:00'
        },
        {
            'role': 'assistant',
            'content': 'Hi! How can I help?',
            'timestamp': '2026-01-19T10:30:05'
        }
    ],
    'openwebui_chat_history': [...]  # Same as messages
}
```

## API Endpoints

### Open WebUI API

| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/api/models` | GET | List available models | Bearer Token |
| `/api/chat/completions` | POST | Generate chat response | Bearer Token |
| `/api/chat` | GET | Get chat history | Bearer Token |
| `/api/chat/{id}` | DELETE | Delete chat | Bearer Token |

### Request Example

```json
POST /api/chat/completions
Authorization: Bearer sk-xxxxx
Content-Type: application/json

{
  "model": "llama3.2:latest",
  "messages": [
    {
      "role": "system",
      "content": "你是一位广告学领域的专家..."
    },
    {
      "role": "user",
      "content": "什么是广告的黄金时代？"
    }
  ],
  "stream": true,
  "temperature": 0.7,
  "top_p": 0.9,
  "max_tokens": 2000
}
```

### Response Example (Streaming)

```
data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","created":1705660800,"model":"llama3.2:latest","choices":[{"index":0,"delta":{"content":"广告"},"finish_reason":null}]}

data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","created":1705660800,"model":"llama3.2:latest","choices":[{"index":0,"delta":{"content":"的"},"finish_reason":null}]}

data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","created":1705660800,"model":"llama3.2:latest","choices":[{"index":0,"delta":{"content":"黄金"},"finish_reason":null}]}

data: [DONE]
```

## Error Handling Flow

```
API Call
    │
    ├─ Connection Error
    │   └─ Display: "无法连接到Open WebUI服务"
    │
    ├─ Timeout Error
    │   └─ Display: "请求超时，请稍后重试"
    │
    ├─ Authentication Error (401/403)
    │   └─ Display: "API密钥无效"
    │
    ├─ Server Error (500)
    │   └─ Display: "服务器错误"
    │
    └─ Success (200)
        └─ Parse and display response
```

## Security Considerations

### API Key Storage

```
.env file (not in git)
    │
    ▼
Environment Variables
    │
    ▼
os.getenv() at runtime
    │
    ▼
HTTP Headers (Authorization: Bearer)
    │
    ▼
Open WebUI validates
```

### Best Practices

1. ✅ API key in `.env` (not hardcoded)
2. ✅ `.env` in `.gitignore`
3. ✅ HTTPS in production
4. ✅ Token expiration handling
5. ✅ Rate limiting awareness
6. ✅ Input sanitization
7. ✅ Error message sanitization

## Performance Optimization

### Streaming Responses

- **Benefit**: Better UX, perceived faster response
- **Implementation**: SSE (Server-Sent Events)
- **Trade-off**: Slightly more complex parsing

### History Management

- **Limit**: 10 messages (MAX_HISTORY)
- **Benefit**: Prevents memory bloat
- **Trade-off**: Loses older context

### Connection Pooling

- **Current**: New connection per request
- **Future**: Consider connection pooling for high traffic

## Monitoring and Debugging

### Health Check

```python
def check_connection() -> bool:
    try:
        response = requests.get(
            f"{self.base_url}/api/models",
            headers=self.headers,
            timeout=5
        )
        return response.status_code == 200
    except Exception as e:
        st.error(f"Connection failed: {e}")
        return False
```

### Logging Points

1. Connection attempts
2. API calls (request/response)
3. Model switches
4. Error occurrences
5. User actions

### Debug Commands

```bash
# Check Open WebUI logs
docker logs open-webui

# Check Ollama logs
journalctl -u ollama

# Test API manually
curl -H "Authorization: Bearer sk-xxx" \
     http://localhost:3000/api/models

# Monitor network traffic
docker logs -f open-webui
```

## Scalability Considerations

### Current Setup (Single User)

```
User ──▶ Streamlit ──▶ Open WebUI ──▶ Ollama ──▶ GPU
```

### Multi-User Setup (Future)

```
User 1 ──┐
User 2 ──┼──▶ Load Balancer ──▶ Open WebUI Cluster ──▶ Ollama Pool ──▶ GPU Farm
User 3 ──┘
```

### Bottlenecks

1. **GPU**: Single GPU limits concurrent users
2. **Memory**: Large models require significant RAM
3. **Network**: Local setup, no remote access
4. **Storage**: Chat history grows over time

### Solutions

1. **GPU**: Multiple GPUs or cloud GPU instances
2. **Memory**: Model quantization, smaller models
3. **Network**: Deploy on server with public IP
4. **Storage**: Regular cleanup, archival strategy

---

**Architecture Version**: 1.0  
**Last Updated**: January 19, 2026  
**Status**: Production Ready ✅
