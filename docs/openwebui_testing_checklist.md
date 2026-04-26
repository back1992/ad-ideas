# Open WebUI Integration - Testing Checklist

## Pre-Testing Setup

### Environment Verification

- [ ] `.env` file exists in project root
- [ ] `AI_BACKEND=openwebui` is set
- [ ] `OPENWEBUI_BASE_URL` is configured
- [ ] `OPENWEBUI_API_KEY` is set (not placeholder)
- [ ] `OPENWEBUI_MODEL` is specified

### Service Status

- [ ] Docker is running
- [ ] Open WebUI container is running (`docker ps | grep open-webui`)
- [ ] Ollama service is running (`ollama list`)
- [ ] At least one model is pulled (`ollama list` shows models)

### Network Connectivity

- [ ] Can access Open WebUI web interface (http://localhost:3000)
- [ ] Can access Streamlit app (http://localhost:8501)
- [ ] Open WebUI can connect to Ollama
- [ ] API key is valid (test in Open WebUI settings)

## Functional Testing

### 1. Connection Testing

#### Test 1.1: Initial Connection
- [ ] Start Streamlit app
- [ ] Login to platform
- [ ] Navigate to "与大师对话 / Chat with Masters"
- [ ] **Expected**: Sidebar shows "✅ Open WebUI 连接正常"
- [ ] **Expected**: No error messages displayed

#### Test 1.2: Connection Failure Handling
- [ ] Stop Open WebUI container (`docker stop open-webui`)
- [ ] Refresh chat page
- [ ] **Expected**: Sidebar shows "❌ Open WebUI 连接失败"
- [ ] **Expected**: Error message with troubleshooting tips
- [ ] Start Open WebUI container (`docker start open-webui`)
- [ ] Refresh page
- [ ] **Expected**: Connection restored

### 2. Model Selection Testing

#### Test 2.1: Model List Display
- [ ] Check sidebar for model dropdown
- [ ] **Expected**: Dropdown shows available models
- [ ] **Expected**: Current model is displayed
- [ ] **Expected**: At least one model is available

#### Test 2.2: Model Switching
- [ ] Select different model from dropdown
- [ ] **Expected**: Success message appears
- [ ] **Expected**: "当前模型" updates to new model
- [ ] Send a test message
- [ ] **Expected**: Response uses new model

### 3. Chat Functionality Testing

#### Test 3.1: Basic Message Send/Receive
- [ ] Type message: "你好" (Hello)
- [ ] Press Enter or click send
- [ ] **Expected**: Message appears in chat
- [ ] **Expected**: AI response appears
- [ ] **Expected**: Response is in Chinese
- [ ] **Expected**: Response is relevant

#### Test 3.2: Streaming Response
- [ ] Enable "流式回复" checkbox
- [ ] Send message: "请详细介绍广告的历史" (Please introduce advertising history in detail)
- [ ] **Expected**: Response appears word-by-word
- [ ] **Expected**: Cursor indicator (▌) shows during streaming
- [ ] **Expected**: Full response appears when complete

#### Test 3.3: Non-Streaming Response
- [ ] Disable "流式回复" checkbox
- [ ] Send message: "什么是广告？" (What is advertising?)
- [ ] **Expected**: Spinner shows "AI正在思考中..."
- [ ] **Expected**: Full response appears at once
- [ ] **Expected**: No streaming effect

#### Test 3.4: Multi-Turn Conversation
- [ ] Send: "什么是广告的黄金时代？" (What is the golden age of advertising?)
- [ ] Wait for response
- [ ] Send: "请举例说明" (Please give examples)
- [ ] **Expected**: Second response references first question
- [ ] **Expected**: Context is maintained
- [ ] **Expected**: Examples are relevant

#### Test 3.5: Long Conversation
- [ ] Send 15+ messages back and forth
- [ ] **Expected**: All messages display correctly
- [ ] **Expected**: History is maintained
- [ ] **Expected**: No memory errors
- [ ] **Expected**: Older messages are trimmed (MAX_HISTORY = 10)

### 4. Chat History Management

#### Test 4.1: History Persistence
- [ ] Send several messages
- [ ] Note the message count in sidebar
- [ ] Refresh the page (F5)
- [ ] **Expected**: Messages are lost (session-based)
- [ ] **Note**: This is expected behavior for session state

#### Test 4.2: Clear Conversation
- [ ] Send several messages
- [ ] Click "🗑️ 清空对话" button
- [ ] **Expected**: Confirmation or immediate clear
- [ ] **Expected**: All messages disappear
- [ ] **Expected**: Message count resets to 0
- [ ] **Expected**: Can start new conversation

#### Test 4.3: Message Timestamps
- [ ] Send a message
- [ ] Check sidebar for "最后消息" timestamp
- [ ] **Expected**: Timestamp shows current time
- [ ] **Expected**: Format is readable (YYYY-MM-DD HH:MM)

### 5. Error Handling Testing

#### Test 5.1: Invalid API Key
- [ ] Edit `.env`: Set `OPENWEBUI_API_KEY=invalid_key`
- [ ] Restart app
- [ ] Try to send message
- [ ] **Expected**: Error message about authentication
- [ ] **Expected**: Clear guidance on fixing
- [ ] Restore valid API key

#### Test 5.2: Network Timeout
- [ ] Stop Ollama service
- [ ] Send message
- [ ] **Expected**: Timeout error after ~60 seconds
- [ ] **Expected**: Error message: "请求超时，请稍后重试"
- [ ] Start Ollama service

#### Test 5.3: Invalid Model
- [ ] Edit `.env`: Set `OPENWEBUI_MODEL=nonexistent_model`
- [ ] Restart app
- [ ] Try to send message
- [ ] **Expected**: Error message about model not found
- [ ] Restore valid model

#### Test 5.4: Empty Message
- [ ] Try to send empty message
- [ ] **Expected**: Nothing happens or validation message
- [ ] **Expected**: No API call made

### 6. UI/UX Testing

#### Test 6.1: Responsive Layout
- [ ] Resize browser window (narrow)
- [ ] **Expected**: Chat interface adapts
- [ ] **Expected**: Sidebar collapses appropriately
- [ ] Resize browser window (wide)
- [ ] **Expected**: Layout uses available space

#### Test 6.2: Message Formatting
- [ ] Send message with markdown: "**Bold** and *italic*"
- [ ] **Expected**: Formatting is rendered
- [ ] Send message with code: "`code block`"
- [ ] **Expected**: Code formatting is applied
- [ ] Send message with list
- [ ] **Expected**: List is formatted correctly

#### Test 6.3: Long Messages
- [ ] Send very long message (500+ characters)
- [ ] **Expected**: Message displays fully
- [ ] **Expected**: Scrolling works
- [ ] **Expected**: Response handles long input

#### Test 6.4: Special Characters
- [ ] Send message with emojis: "😀 👍 🎉"
- [ ] **Expected**: Emojis display correctly
- [ ] Send message with Chinese punctuation: "你好！这是测试。"
- [ ] **Expected**: Punctuation displays correctly

### 7. Performance Testing

#### Test 7.1: Response Time
- [ ] Send simple question
- [ ] Measure time to first response
- [ ] **Expected**: < 5 seconds for first token
- [ ] **Expected**: Smooth streaming

#### Test 7.2: Concurrent Messages
- [ ] Send message
- [ ] While streaming, try to send another
- [ ] **Expected**: Second message waits or queues
- [ ] **Expected**: No crashes or errors

#### Test 7.3: Large Response
- [ ] Ask for detailed explanation (triggers long response)
- [ ] **Expected**: Streaming continues smoothly
- [ ] **Expected**: Full response displays
- [ ] **Expected**: No truncation

### 8. Integration Testing

#### Test 8.1: Authentication Integration
- [ ] Logout from platform
- [ ] Try to access chat page
- [ ] **Expected**: Redirected to login
- [ ] Login again
- [ ] **Expected**: Can access chat

#### Test 8.2: Role-Based Access
- [ ] Login as student
- [ ] **Expected**: Can access chat
- [ ] Login as professor
- [ ] **Expected**: Can access chat
- [ ] Login as admin
- [ ] **Expected**: Can access chat

#### Test 8.3: Navigation
- [ ] From chat page, navigate to other pages
- [ ] **Expected**: Navigation works smoothly
- [ ] Return to chat page
- [ ] **Expected**: Chat state is reset (new session)

### 9. Edge Cases Testing

#### Test 9.1: Rapid Message Sending
- [ ] Send 5 messages quickly in succession
- [ ] **Expected**: All messages are processed
- [ ] **Expected**: Responses appear in order
- [ ] **Expected**: No messages lost

#### Test 9.2: Special Input
- [ ] Send only spaces: "     "
- [ ] **Expected**: Handled gracefully
- [ ] Send only punctuation: "!!!"
- [ ] **Expected**: AI responds appropriately

#### Test 9.3: Browser Refresh During Streaming
- [ ] Send message that triggers long response
- [ ] During streaming, refresh page (F5)
- [ ] **Expected**: Page reloads cleanly
- [ ] **Expected**: No errors
- [ ] **Expected**: Can start new conversation

### 10. Documentation Testing

#### Test 10.1: Setup Guide Accuracy
- [ ] Follow `docs/openwebui_setup_guide.md` step by step
- [ ] **Expected**: All steps work as described
- [ ] **Expected**: No missing information
- [ ] **Expected**: Commands execute successfully

#### Test 10.2: Quick Start Guide
- [ ] Follow `docs/openwebui_quick_start.md`
- [ ] **Expected**: Can complete setup in ~5 minutes
- [ ] **Expected**: All commands work
- [ ] **Expected**: Troubleshooting tips are helpful

#### Test 10.3: Architecture Documentation
- [ ] Review `docs/openwebui_architecture.md`
- [ ] **Expected**: Diagrams are accurate
- [ ] **Expected**: Component descriptions match implementation
- [ ] **Expected**: API endpoints are correct

## Regression Testing

### After Code Changes

- [ ] All connection tests pass
- [ ] All chat functionality tests pass
- [ ] No new errors in console
- [ ] Performance is not degraded
- [ ] Documentation is updated

### After Configuration Changes

- [ ] New configuration is documented
- [ ] Old configurations still work (backward compatible)
- [ ] Error messages are updated
- [ ] Examples are updated

## Security Testing

### Test S.1: API Key Exposure
- [ ] Check browser console for API key
- [ ] **Expected**: API key not visible in console
- [ ] Check network tab for API key
- [ ] **Expected**: API key only in Authorization header
- [ ] Check page source
- [ ] **Expected**: API key not in HTML

### Test S.2: Input Sanitization
- [ ] Send message with HTML: `<script>alert('xss')</script>`
- [ ] **Expected**: HTML is escaped or sanitized
- [ ] **Expected**: No script execution
- [ ] Send message with SQL-like syntax
- [ ] **Expected**: Handled as plain text

### Test S.3: Rate Limiting
- [ ] Send many messages rapidly
- [ ] **Expected**: No crashes
- [ ] **Expected**: Graceful handling
- [ ] **Note**: Check if rate limiting is needed

## Accessibility Testing

### Test A.1: Keyboard Navigation
- [ ] Use Tab key to navigate
- [ ] **Expected**: Can reach all interactive elements
- [ ] Use Enter to send message
- [ ] **Expected**: Message sends correctly

### Test A.2: Screen Reader Compatibility
- [ ] Enable screen reader
- [ ] Navigate chat interface
- [ ] **Expected**: Elements are announced
- [ ] **Expected**: Messages are readable

## Browser Compatibility

### Test B.1: Chrome
- [ ] All tests pass in Chrome
- [ ] **Expected**: Full functionality

### Test B.2: Firefox
- [ ] All tests pass in Firefox
- [ ] **Expected**: Full functionality

### Test B.3: Safari
- [ ] All tests pass in Safari
- [ ] **Expected**: Full functionality

### Test B.4: Edge
- [ ] All tests pass in Edge
- [ ] **Expected**: Full functionality

## Mobile Testing (if applicable)

### Test M.1: Mobile Browser
- [ ] Access on mobile device
- [ ] **Expected**: Responsive layout
- [ ] **Expected**: Chat input works
- [ ] **Expected**: Messages display correctly

## Test Results Summary

### Test Date: _______________
### Tester: _______________
### Environment: _______________

| Category | Tests Passed | Tests Failed | Notes |
|----------|--------------|--------------|-------|
| Connection | __ / __ | __ / __ | |
| Model Selection | __ / __ | __ / __ | |
| Chat Functionality | __ / __ | __ / __ | |
| History Management | __ / __ | __ / __ | |
| Error Handling | __ / __ | __ / __ | |
| UI/UX | __ / __ | __ / __ | |
| Performance | __ / __ | __ / __ | |
| Integration | __ / __ | __ / __ | |
| Edge Cases | __ / __ | __ / __ | |
| Documentation | __ / __ | __ / __ | |
| Security | __ / __ | __ / __ | |
| Accessibility | __ / __ | __ / __ | |
| Browser Compat | __ / __ | __ / __ | |

### Overall Status: ☐ PASS ☐ FAIL ☐ PARTIAL

### Critical Issues Found:
1. 
2. 
3. 

### Minor Issues Found:
1. 
2. 
3. 

### Recommendations:
1. 
2. 
3. 

---

**Testing Checklist Version**: 1.0  
**Last Updated**: January 19, 2026  
**Status**: Ready for Testing ✅
