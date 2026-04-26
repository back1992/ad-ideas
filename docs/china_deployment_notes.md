# China Deployment Notes

## Overview

This document outlines the changes made to ensure the 广告思想简史 platform works properly when deployed to Aliyun in China, where Google services are blocked.

## Changes Made

### 1. Database System (✅ Completed)

**Issue**: Original `utils/db.py` used Google Sheets API which is blocked in China.

**Solution**: 
- Replaced Google Sheets integration with SQLite database
- Maintained API compatibility for any existing code
- Uses the robust `modules/database.py` system instead

**Files Modified**:
- `utils/db.py` - Replaced Google Sheets with SQLite
- `utils/constans.py` - Updated constants for China compatibility

### 2. AI Services (⚠️ Requires Attention)

**Issue**: The platform uses Google Gemini AI API which is blocked in China.

**Current Usage**:
- `chat_gemini.py` - Direct Gemini API usage
- `modules/ai_chat.py` - Gemini integration in AI chat module

**Recommended Solutions**:
1. **Use Alibaba Cloud's Tongyi Qianwen** (通义千问) - China's leading AI service
2. **Use Baidu's ERNIE** - Another popular Chinese AI service  
3. **Use OpenAI via proxy** - If available through approved channels
4. **Use local AI models** - Deploy models like Qwen locally

### 3. Other Google Services

**Google Drive Downloads** (`chatbot/data.py`):
- Currently commented out
- If needed, replace with Aliyun OSS or local file storage

## Recommended Next Steps

### For AI Services
1. **Register with Alibaba Cloud** and get Tongyi Qianwen API access
2. **Update AI configuration** to use Chinese AI services
3. **Test AI functionality** with Chinese language content
4. **Add fallback mechanisms** for service availability

### For File Storage
1. **Set up Aliyun OSS** for file storage needs
2. **Replace Google Drive** references with OSS
3. **Update download mechanisms** for China compatibility

### For Monitoring
1. **Use Aliyun monitoring** instead of Google Analytics
2. **Set up Chinese CDN** for better performance
3. **Configure Chinese domain** and ICP filing

## Configuration for China

Add these environment variables for China deployment:

```bash
# China deployment flag
CHINA_DEPLOYMENT=true

# Database settings
DATABASE_PATH=platform.db

# AI Service (choose one)
AI_PROVIDER=tongyi  # or 'baidu', 'openai', 'local'
TONGYI_API_KEY=your_tongyi_api_key
BAIDU_API_KEY=your_baidu_api_key

# File storage
STORAGE_PROVIDER=aliyun_oss
ALIYUN_OSS_ENDPOINT=your_oss_endpoint
ALIYUN_OSS_BUCKET=your_bucket_name
```

## Testing Checklist

- [ ] Database operations work without Google APIs
- [ ] AI chat functions with Chinese AI services
- [ ] File uploads/downloads work with Aliyun OSS
- [ ] All features accessible from China mainland
- [ ] Performance optimized for Chinese networks
- [ ] Compliance with Chinese regulations

## Performance Considerations

1. **Use Chinese CDN** for static assets
2. **Optimize for Chinese networks** (different latency patterns)
3. **Consider Chinese user preferences** (WeChat integration, mobile-first)
4. **Use simplified Chinese** for better user experience

## Compliance Notes

1. **ICP filing required** for domain hosting in China
2. **Data residency** requirements for user data
3. **Content moderation** may be required
4. **Privacy policy** should comply with Chinese regulations