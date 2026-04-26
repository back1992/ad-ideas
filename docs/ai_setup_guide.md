# 🤖 AI后端配置指南

广告思想简史平台支持多种AI后端，您可以根据需求选择最适合的AI服务。

## 🎯 支持的AI后端

| AI后端 | 优势 | 适用场景 | 成本 |
|--------|------|----------|------|
| **Gemini** | 免费额度、响应快、中文支持好 | 个人使用、快速原型 | 免费/低成本 |
| **Ollama** | 完全本地、隐私保护、无API费用 | 企业内网、隐私敏感 | 免费 |
| **Azure OpenAI** | 企业级、稳定性高、GPT模型 | 生产环境、企业应用 | 按量付费 |

---

## 🌟 方案一：Gemini (推荐)

### 优势
- ✅ **免费使用**: 每月有免费API调用额度
- ✅ **响应速度快**: 通常1-3秒内响应
- ✅ **中文支持优秀**: 专门优化过中文对话
- ✅ **部署简单**: 只需API密钥即可使用
- ✅ **适合中国用户**: 在中国可以正常访问

### 配置步骤

#### 1. 获取API密钥
1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 登录Google账户
3. 点击"Create API Key"
4. 复制生成的API密钥

#### 2. 配置环境变量
在项目根目录的 `.env` 文件中添加：

```bash
# AI后端选择
AI_BACKEND=gemini

# Gemini配置
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```

#### 3. 安装依赖
```bash
pip install google-generativeai
```

#### 4. 测试配置
运行以下命令测试配置：
```bash
python -c "
import google.generativeai as genai
import os
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content('你好')
print('Gemini配置成功:', response.text)
"
```

---

## 🦙 方案二：Ollama (本地部署)

### 优势
- ✅ **完全免费**: 无API调用费用
- ✅ **数据隐私**: 所有数据在本地处理
- ✅ **离线使用**: 无需网络连接
- ✅ **多模型支持**: 支持Llama2、Mistral等多种模型
- ✅ **企业友好**: 适合内网部署

### 配置步骤

#### 1. 安装Ollama

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
下载安装包：https://ollama.ai/download/windows

#### 2. 启动Ollama服务
```bash
ollama serve
```

#### 3. 下载模型
```bash
# 下载Llama2模型 (推荐)
ollama pull llama2

# 或下载其他模型
ollama pull mistral
ollama pull codellama
```

#### 4. 配置环境变量
在 `.env` 文件中添加：

```bash
# AI后端选择
AI_BACKEND=ollama

# Ollama配置
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

#### 5. 测试配置
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama2",
  "prompt": "你好",
  "stream": false
}'
```

### 推荐模型

| 模型 | 大小 | 内存需求 | 特点 | 适用场景 |
|------|------|----------|------|----------|
| **llama2:7b** | 3.8GB | 8GB | 通用对话 | 日常问答 |
| **llama2:13b** | 7.3GB | 16GB | 更强性能 | 复杂任务 |
| **mistral:7b** | 4.1GB | 8GB | 高效快速 | 快速响应 |
| **codellama:7b** | 3.8GB | 8GB | 代码专用 | 编程助手 |

---

## ☁️ 方案三：Azure OpenAI

### 优势
- ✅ **企业级稳定性**: 99.9%可用性保证
- ✅ **强大的GPT模型**: GPT-4、GPT-3.5-turbo
- ✅ **合规性**: 符合企业安全要求
- ✅ **可控成本**: 精确的使用量计费
- ✅ **中国可用**: 在中国有数据中心

### 配置步骤

#### 1. 创建Azure OpenAI资源
1. 登录 [Azure Portal](https://portal.azure.com)
2. 创建"Azure OpenAI"资源
3. 等待审批通过（通常需要几天）
4. 部署GPT模型

#### 2. 获取配置信息
- **Endpoint**: 在资源概览页面找到
- **API Key**: 在"Keys and Endpoint"页面
- **Deployment Name**: 您部署的模型名称

#### 3. 配置环境变量
在 `.env` 文件中添加：

```bash
# AI后端选择
AI_BACKEND=azure_openai

# Azure OpenAI配置
AZURE_OPENAI_KEY=your_azure_openai_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_CHATGPT_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-06-01
```

#### 4. 安装依赖
```bash
pip install openai
```

#### 5. 测试配置
```bash
python -c "
from openai import AzureOpenAI
import os
client = AzureOpenAI(
    api_key=os.getenv('AZURE_OPENAI_KEY'),
    api_version=os.getenv('AZURE_OPENAI_API_VERSION'),
    azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT')
)
response = client.chat.completions.create(
    model=os.getenv('AZURE_OPENAI_CHATGPT_DEPLOYMENT'),
    messages=[{'role': 'user', 'content': '你好'}]
)
print('Azure OpenAI配置成功:', response.choices[0].message.content)
"
```

---

## 🔄 如何切换AI后端

### 方法一：修改环境变量
1. 编辑 `.env` 文件
2. 修改 `AI_BACKEND` 的值
3. 重启Streamlit应用

```bash
# 切换到Gemini
AI_BACKEND=gemini

# 切换到Ollama  
AI_BACKEND=ollama

# 切换到Azure OpenAI
AI_BACKEND=azure_openai
```

### 方法二：运行时切换
```bash
# 临时使用Gemini
AI_BACKEND=gemini streamlit run streamlit_app.py

# 临时使用Ollama
AI_BACKEND=ollama streamlit run streamlit_app.py
```

---

## 🛠️ 故障排除

### Gemini常见问题

**问题**: API密钥无效
```
解决方案:
1. 检查API密钥是否正确复制
2. 确认API密钥未过期
3. 检查是否有API调用额度
```

**问题**: 网络连接失败
```
解决方案:
1. 检查网络连接
2. 尝试使用VPN
3. 检查防火墙设置
```

### Ollama常见问题

**问题**: 无法连接到Ollama服务
```
解决方案:
1. 确认Ollama服务正在运行: ollama serve
2. 检查端口11434是否被占用
3. 尝试重启Ollama服务
```

**问题**: 模型下载失败
```
解决方案:
1. 检查网络连接
2. 尝试使用代理: HTTPS_PROXY=http://proxy:port ollama pull llama2
3. 手动下载模型文件
```

**问题**: 内存不足
```
解决方案:
1. 使用更小的模型 (如llama2:7b而不是13b)
2. 增加系统内存
3. 关闭其他占用内存的程序
```

### Azure OpenAI常见问题

**问题**: 认证失败
```
解决方案:
1. 检查API密钥和Endpoint是否正确
2. 确认资源未被暂停
3. 检查API版本是否匹配
```

**问题**: 模型部署不存在
```
解决方案:
1. 在Azure Portal中检查模型部署状态
2. 确认部署名称正确
3. 等待部署完成
```

---

## 📊 性能对比

### 响应速度测试 (平均值)

| AI后端 | 首次响应 | 流式响应 | 长文本 |
|--------|----------|----------|--------|
| Gemini | 1-2秒 | 支持 | 2-4秒 |
| Ollama (本地) | 3-5秒 | 支持 | 5-10秒 |
| Azure OpenAI | 1-3秒 | 支持 | 2-5秒 |

### 成本对比 (每1000次调用)

| AI后端 | 成本 | 说明 |
|--------|------|------|
| Gemini | $0-2 | 有免费额度 |
| Ollama | $0 | 完全免费 |
| Azure OpenAI | $2-20 | 按模型计费 |

---

## 🎯 推荐配置

### 个人开发者
```bash
AI_BACKEND=gemini
GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-1.5-flash
```

### 企业内网
```bash
AI_BACKEND=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

### 生产环境
```bash
AI_BACKEND=azure_openai
AZURE_OPENAI_KEY=your_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_CHATGPT_DEPLOYMENT=gpt-4o
```

---

## 📞 技术支持

如果您在配置过程中遇到问题，请：

1. 查看应用日志获取详细错误信息
2. 检查网络连接和防火墙设置
3. 确认API密钥和配置信息正确
4. 参考官方文档进行故障排除

**相关链接:**
- [Gemini API文档](https://ai.google.dev/docs)
- [Ollama官方文档](https://ollama.ai/docs)
- [Azure OpenAI文档](https://docs.microsoft.com/azure/cognitive-services/openai/)

---

## 🔮 未来计划

我们计划支持更多AI后端：
- **Claude** (Anthropic)
- **文心一言** (百度)
- **通义千问** (阿里云)
- **ChatGLM** (智谱AI)

敬请期待！🚀