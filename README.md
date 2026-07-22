# 📚 广告思想简史 (Advertising History Platform)

一个基于 Streamlit 的广告历史教育平台，集成 AI 智能助手，帮助学生探索广告思想的发展历程。

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ad-ideas.streamlit.app/)
[![Tests](https://img.shields.io/badge/tests-169%20passing-green)]()
[![Python](https://img.shields.io/badge/python-3.14-blue)]()

## ✨ 核心功能

- **📖 广告历史时间线** - 探索广告思想的发展脉络
- **🌟 广告大师风云录** - 了解传奇广告人的故事
- **📊 数据可视化** - 交互式图表展示广告趋势
- **🏆 百年经典广告** - 20世纪最成功的100个广告活动
- **💬 AI 智能助手** - 基于 Pydantic AI 的广告学专家问答系统
- **📝 文章系统** - 教授发布专业文章，学生评论互动
- **🔍 全文搜索** - 跨文章、时间线、人物的智能搜索
- **👥 用户角色** - 管理员、教授、学生三种角色权限
- **📬 评论审核** - 学生评论需审核，教授/管理员评论自动通过
- **🔔 文章审核通知** - 文章提交/审核/拒绝时自动通知相关用户

## 🤖 AI 智能助手

平台集成了基于 **Pydantic AI** 的智能助手，可以：

- 🔍 **搜索平台文章** - 自动检索相关广告学内容
- 📖 **获取文章详情** - 根据ID获取完整文章内容
- 💡 **智能推荐** - 根据主题推荐相关文章
- 📈 **热门浏览** - 获取最受欢迎的文章
- 📂 **分类浏览** - 按分类查看文章

### AI 后端配置

平台支持多种 AI 后端，通过环境变量配置。**默认使用 OpenWebUI**。

#### 1. OpenWebUI（默认）- 推荐

```bash
# .env 配置
AI_BACKEND=openwebui
OPENWEBUI_BASE_URL=https://your-openwebui-instance.com
OPENWEBUI_JWT_TOKEN=your_jwt_token
OPENWEBUI_MODEL=qwen3.5-plus
```

**特点：**
- ✅ 默认后端，开箱即用
- ✅ 支持多种模型（Qwen、GPT、Claude 等）
- ✅ 统一的 API 接口
- ✅ 易于部署和维护

#### 2. Pydantic AI - 智能代理模式

```bash
# .env 配置
AI_BACKEND=pydantic_ai
PYDANTIC_AI_PROVIDER=groq          # 可选: groq, ollama, gemini, openai
PYDANTIC_AI_MODEL=llama-3.3-70b-versatile
GROQ_API_KEY=your_groq_api_key     # 如使用 Groq
```

**特点：**
- ✅ 结构化输出（答案 + 来源 + 后续问题）
- ✅ 工具调用（自动搜索、推荐文章）
- ✅ 运行时切换模型（管理员可在界面中切换）
- ✅ 智能缓存（提升响应速度）
- ✅ 对话记忆（持久化聊天记录）

#### 3. Groq（高速推理）

```bash
AI_BACKEND=groq
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
```

#### 4. Ollama（本地部署）

```bash
AI_BACKEND=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

#### 5. Gemini（Google）

```bash
AI_BACKEND=gemini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash
```

#### 6. Azure OpenAI

```bash
AI_BACKEND=azure_openai
AZURE_OPENAI_KEY=your_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_VERSION=2024-06-01
AZURE_OPENAI_CHATGPT_DEPLOYMENT=gpt-4o
```

### 使用 AI 助手

1. **启动应用**
   ```bash
   streamlit run streamlit_app.py
   ```

2. **登录系统**
   - 使用管理员/教授/学生账号登录
   - 或作为访客浏览（部分功能受限）

3. **进入 AI 聊天**
   - 在侧边栏选择 "AI 助手"
   - 输入广告学相关问题，例如：
     - "介绍万宝路广告的历史意义"
     - "推荐关于品牌重塑的文章"
     - "20世纪50年代有哪些经典广告？"

4. **查看结构化回答**（仅 Pydantic AI 后端）
   - AI 会返回：
     - 📝 **答案** - 详细的专业解答
     - 📚 **参考来源** - 引用的平台文章
     - 💡 **延伸问题** - 建议的后续探索方向

### 管理员功能

管理员可以在界面中实时切换 AI 模型（仅 Pydantic AI 后端）：

1. 登录管理员账号
2. 进入 AI 聊天页面
3. 在侧边栏找到 "运行时模型切换"
4. 选择提供商（Groq/Ollama/Gemini/OpenAI）
5. 输入模型名称
6. 点击 "应用更改"
7. 系统立即切换到新模型（无需重启）

### AI 助手技术架构

```
用户提问
  ↓
AIChat (路由层)
  ↓
┌─────────────────────────────────────┐
│  OpenWebUI (默认)                    │
│  或 Pydantic AI Agent               │
│  ├─ 工具: search_articles()         │
│  ├─ 工具: get_article_detail()      │
│  ├─ 工具: get_recommendations()     │
│  ├─ 工具: get_trending_articles()   │
│  └─ 工具: get_articles_by_category()│
└─────────────────────────────────────┘
  ↓
结构化输出 (ChatResponse) [Pydantic AI]
  ├─ answer: 答案文本
  ├─ sources: 引用来源
  ─ follow_up_questions: 延伸问题
  ↓
对话记忆 (SQLite) [Pydantic AI]
  └─ 持久化聊天记录
  ↓
Streamlit UI 渲染
```

##  快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

创建 `.env` 文件（默认使用 OpenWebUI）：

```bash
# 数据库
DATABASE_PATH=platform.db

# AI 后端（默认: openwebui）
AI_BACKEND=openwebui
OPENWEBUI_BASE_URL=https://your-openwebui-instance.com
OPENWEBUI_JWT_TOKEN=your_jwt_token
OPENWEBUI_MODEL=qwen3.5-plus

# 其他可选后端配置见上方 "AI 后端配置" 部分
```

### 初始化数据库

首次运行时会自动创建数据库和表结构。

### 创建管理员账号

编辑 `config.yaml` 添加用户：

```yaml
credentials:
  usernames:
    admin:
      email: admin@example.com
      name: Admin User
      password: hashed_password  # 使用 bcrypt 哈希
      role: admin
```

### 启动应用

```bash
streamlit run streamlit_app.py
```

访问 http://localhost:8501

## 🏗️ 项目结构

```
ad-ideas/
├── streamlit_app.py              # 主应用入口
├── modules/
│   ├── ai_chat.py               # AI 聊天后端路由
│   ├── ai_agent.py              # Pydantic AI 代理定义
│   ├── ai_models.py             # Pydantic 输出模型
│   ├── ai_tools.py              # AI 工具函数（搜索、推荐等）
│   ├── conversation_memory.py   # 对话记忆系统
│   ├── database.py              # 数据库管理
│   ├── auth.py                  # 认证系统
│   ├── articles.py              # 文章管理（1400+ 行）
│   ├── article_notifications.py # 文章审核通知系统
│   ├── comments.py              # 评论管理（1700+ 行）
│   ├── search.py                # 搜索系统
│   ├── recommendations.py       # 推荐引擎
│   ├── moderation.py            # 内容审核系统
│   ├── feedback.py              # 反馈系统
│   ├── analytics.py             # 数据分析面板
│   ├── activity.py              # 活动日志
│   ── user_management.py       # 用户管理
├── tests/
│   ├── test_article_properties.py       # 文章属性测试
│   ├── test_comment_properties.py       # 评论属性测试
│   ├── test_comment_new_features.py     # 评论新功能测试（32 个）
│   ├── test_moderation_properties.py    # 审核属性测试
│   ├── test_complete_workflows.py       # 完整工作流测试
│   ├── test_integration_checkpoint.py   # 集成测试
│   ├── test_ai_agent.py                 # AI 代理测试
│   ├── test_ai_chat_backend.py          # AI 聊天后端测试
│   ├── test_e2e.py                      # 端到端测试
│   └── ...（共 17 个测试文件，169 个测试）
├── docs/
│   ├── design-pydantic-ai-integration.md
│   ├── phase2-summary.md
│   └── phase3-summary.md
├── config.yaml                  # 用户配置
├── .env                         # 环境变量
├── Makefile                     # 构建和测试命令
└── requirements.txt             # 依赖
```

## 🧪 测试

项目使用 **pytest + Hypothesis** 进行基于属性的测试，共 **169 个测试用例**。

### 运行所有测试

```bash
make test
```

### 按模块运行测试

```bash
make test-articles     # 文章系统测试
make test-comments     # 评论系统测试
make test-moderation   # 审核系统测试
make test-auth         # 认证系统测试
make test-db           # 数据库测试
make test-search       # 搜索系统测试
make test-ai           # AI 系统测试
make test-e2e          # 端到端测试
```

### 测试覆盖

| 模块 | 测试文件 | 用例数 | 状态 |
|------|---------|--------|------|
| 文章系统 | `test_article_properties.py` | 5 | ✅ |
| 评论系统 | `test_comment_properties.py` | 6 | ✅ |
| 评论新功能 | `test_comment_new_features.py` | 32 | ✅ |
| 审核系统 | `test_moderation_properties.py` | 7 | ✅ |
| 完整工作流 | `test_complete_workflows.py` | 8 | ✅ |
| 集成测试 | `test_integration_checkpoint.py` | 20 | ✅ |
| AI 代理 | `test_ai_agent.py` | 23 | ✅ |
| AI 聊天后端 | `test_ai_chat_backend.py` | 12 | ✅ |
| 端到端 | `test_e2e.py` | 18 | ✅ |
| 其他 | 多个文件 | 38 | ✅ |

## 📋 角色权限

| 功能 | 访客 | 学生 | 教授 | 管理员 |
|------|------|------|------|--------|
| 浏览内容 | ✅ | ✅ | ✅ | ✅ |
| AI 助手 | ✅ | ✅ | ✅ | ✅ |
| 评论 | ❌ | ⚠️ 需审核 | ✅ 自动通过 | ✅ 自动通过 |
| 发布文章 | ❌ |  | ⚠️ 需审核 | ✅ 直接发布 |
| 审核文章 | ❌ | ❌ | ❌ | ✅ |
| 审核评论 | ❌ | ❌ | ✅ | ✅ |
| 管理用户 | ❌ | ❌ | ❌ | ✅ |
| 切换 AI 模型 | ❌ | ❌ | ❌ | ✅ |

## 🔧 技术栈

- **前端**: Streamlit
- **后端**: Python 3.14
- **数据库**: SQLite
- **AI 框架**: Pydantic AI 2.14.0
- **默认 AI 后端**: OpenWebUI
- **认证**: streamlit-authenticator
- **测试**: pytest + Hypothesis

## 📝 更新日志

### v3.1 (2026-07-22)
- ✅ 文章审核通知系统（`article_notifications.py`）
- ✅ 学生评论需审核机制（教授/管理员自动通过）
- ✅ `review_feedback` 字段用于存储审核反馈
- ✅ 文章内容 XSS 防护
- ✅ 文章详情页导航优化（session state）
- ✅ 169 个测试全部通过

### v3.0 (2026-07-21)
- ✅ 对话记忆系统（SQLite 持久化）
- ✅ 管理员运行时模型切换 UI
- ✅ 工具结果缓存（TTL 配置）
- ✅ 默认后端改为 OpenWebUI

### v2.0 (2026-07-21)
- ✅ Pydantic AI 后端集成
- ✅ 结构化输出（ChatResponse）
- ✅ 5 个 AI 工具（搜索、详情、推荐、热门、分类）

### v1.0 (2026-07-21)
- ✅ Pydantic AI 基础架构
- ✅ 输出模型定义
- ✅ 工具函数封装

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

##  联系方式

如有问题，请提交 Issue 或联系开发团队。
