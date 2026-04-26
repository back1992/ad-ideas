# 中国部署解决方案：阿里云优化版 + Streamlit-Feedback

## 🎯 **最新发现：Streamlit-Feedback组件**

### **✅ Streamlit-Feedback优势：**
- **轻量级组件** - 专门为Streamlit设计
- **多种反馈类型** - 👍👎 (thumbs), ⭐⭐⭐⭐⭐ (stars), 😊😐😞 (faces)
- **可选文本输入** - 用户可以添加详细反馈
- **本地存储** - 无需外部服务，完美适合中国部署
- **简单集成** - 几行代码即可实现
- **自定义样式** - 可以定制外观

## 🚀 **终极推荐方案：四合一完美组合**

### **1. Streamlit-Authenticator** (用户认证)
### **2. Streamlit-Feedback** (用户反馈)  
### **3. SQLite数据库** (数据存储)
### **4. 阿里云服务** (部署环境)

## 💡 **为什么这是最佳选择：**

### **🎯 完美适合学术平台：**
- **简单直观** - 👍👎 按钮，用户一看就懂
- **多语言友好** - 表情符号无需翻译
- **学术场景** - 适合文章、内容的快速反馈
- **数据收集** - 可以收集用户对内容的满意度

### **📊 反馈类型对比：**

| 反馈类型 | 适用场景 | 用户体验 | 数据价值 |
|----------|----------|----------|----------|
| **Thumbs** 👍👎 | 文章质量评价 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐☆ |
| **Stars** ⭐⭐⭐⭐⭐ | 内容评分 | ⭐⭐⭐⭐☆ | ⭐⭐⭐⭐⭐ |
| **Faces** 😊😐😞 | 用户满意度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐☆ |

## 🔧 **完整实现方案：**

```python
# 完整的中国部署优化方案
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_feedback import streamlit_feedback
import sqlite3
import pandas as pd
from datetime import datetime
import yaml
import json

# 1. 数据库管理器 (增强版)
class DatabaseManager:
    def __init__(self, db_path="data/adideas.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 用户反馈表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            target_type TEXT NOT NULL,
            target_id TEXT NOT NULL,
            feedback_type TEXT NOT NULL,  -- 'thumbs', 'stars', 'faces'
            feedback_value INTEGER,       -- 0/1 for thumbs, 0-4 for stars/faces
            feedback_text TEXT,           -- 可选的文字反馈
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            session_id TEXT,
            user_agent TEXT
        )
        ''')
        
        # 评论表 (保留原有功能)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            target_type TEXT NOT NULL,
            target_id TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            likes INTEGER DEFAULT 0,
            parent_id INTEGER,
            FOREIGN KEY (parent_id) REFERENCES comments (id)
        )
        ''')
        
        # 文章表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT,
            tags TEXT,
            author TEXT NOT NULL,
            status TEXT DEFAULT 'draft',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            views INTEGER DEFAULT 0,
            avg_rating REAL DEFAULT 0.0,
            total_feedback INTEGER DEFAULT 0
        )
        ''')
        
        # 内容统计表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS content_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_type TEXT NOT NULL,
            target_id TEXT NOT NULL,
            thumbs_up INTEGER DEFAULT 0,
            thumbs_down INTEGER DEFAULT 0,
            avg_stars REAL DEFAULT 0.0,
            total_ratings INTEGER DEFAULT 0,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()

# 2. 反馈系统 (Streamlit-Feedback)
class FeedbackSystem:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def collect_feedback(self, target_type, target_id, feedback_type="thumbs", 
                        optional_text_label="请提供更多反馈 (可选)"):
        """收集用户反馈"""
        
        if not st.session_state.get("authentication_status"):
            st.info("👤 登录后可以对内容进行评价")
            return None
        
        # 检查用户是否已经反馈过
        if self.has_user_feedback(st.session_state["username"], target_type, target_id):
            st.success("✅ 您已经对此内容进行过评价")
            self.show_feedback_stats(target_type, target_id)
            return None
        
        st.markdown("### 💭 您觉得这个内容怎么样？")
        
        # 使用streamlit-feedback组件
        feedback = streamlit_feedback(
            feedback_type=feedback_type,
            optional_text_label=optional_text_label,
            key=f"feedback_{target_type}_{target_id}"
        )
        
        if feedback:
            # 保存反馈到数据库
            self.save_feedback(
                username=st.session_state["username"],
                target_type=target_type,
                target_id=target_id,
                feedback_type=feedback_type,
                feedback_value=feedback.get("score"),
                feedback_text=feedback.get("text", "")
            )
            
            # 更新统计数据
            self.update_content_stats(target_type, target_id)
            
            st.success("🎉 感谢您的反馈！")
            st.experimental_rerun()
        
        # 显示当前统计
        self.show_feedback_stats(target_type, target_id)
    
    def save_feedback(self, username, target_type, target_id, feedback_type, 
                     feedback_value, feedback_text):
        """保存反馈到数据库"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO user_feedback 
        (username, target_type, target_id, feedback_type, feedback_value, feedback_text)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, target_type, target_id, feedback_type, feedback_value, feedback_text))
        
        conn.commit()
        conn.close()
    
    def has_user_feedback(self, username, target_type, target_id):
        """检查用户是否已经反馈过"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT COUNT(*) FROM user_feedback 
        WHERE username = ? AND target_type = ? AND target_id = ?
        ''', (username, target_type, target_id))
        
        result = cursor.fetchone()[0] > 0
        conn.close()
        return result
    
    def update_content_stats(self, target_type, target_id):
        """更新内容统计数据"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # 获取所有反馈数据
        cursor.execute('''
        SELECT feedback_type, feedback_value FROM user_feedback
        WHERE target_type = ? AND target_id = ?
        ''', (target_type, target_id))
        
        feedbacks = cursor.fetchall()
        
        thumbs_up = thumbs_down = 0
        star_ratings = []
        
        for feedback_type, value in feedbacks:
            if feedback_type == "thumbs":
                if value == 1:
                    thumbs_up += 1
                else:
                    thumbs_down += 1
            elif feedback_type == "stars":
                star_ratings.append(value)
        
        avg_stars = sum(star_ratings) / len(star_ratings) if star_ratings else 0
        
        # 更新或插入统计数据
        cursor.execute('''
        INSERT OR REPLACE INTO content_stats 
        (target_type, target_id, thumbs_up, thumbs_down, avg_stars, total_ratings, last_updated)
        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (target_type, target_id, thumbs_up, thumbs_down, avg_stars, len(feedbacks)))
        
        conn.commit()
        conn.close()
    
    def show_feedback_stats(self, target_type, target_id):
        """显示反馈统计"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT thumbs_up, thumbs_down, avg_stars, total_ratings 
        FROM content_stats
        WHERE target_type = ? AND target_id = ?
        ''', (target_type, target_id))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            thumbs_up, thumbs_down, avg_stars, total_ratings = result
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("👍 赞", thumbs_up)
            with col2:
                st.metric("👎 踩", thumbs_down)
            with col3:
                if avg_stars > 0:
                    st.metric("⭐ 平均评分", f"{avg_stars:.1f}")
            with col4:
                st.metric("📊 总评价", total_ratings)

# 3. 评论系统 (保留原有功能)
class CommentSystem:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def display_comments(self, target_type, target_id):
        """显示评论界面"""
        st.markdown("### 💬 评论区")
        
        # 评论输入
        if st.session_state.get("authentication_status"):
            with st.form(f"comment_form_{target_id}"):
                comment_text = st.text_area(
                    "写下你的评论...", 
                    placeholder="分享你对这个内容的详细看法...",
                    height=100
                )
                submitted = st.form_submit_button("发表评论")
                
                if submitted and comment_text.strip():
                    self.add_comment(
                        st.session_state["username"],
                        target_type,
                        target_id,
                        comment_text.strip()
                    )
                    st.success("评论发表成功！")
                    st.experimental_rerun()
        else:
            st.info("👤 请登录后发表评论")
        
        # 显示评论
        self.show_comments(target_type, target_id)
    
    def add_comment(self, username, target_type, target_id, content):
        """添加评论"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO comments (username, target_type, target_id, content)
        VALUES (?, ?, ?, ?)
        ''', (username, target_type, target_id, content))
        
        conn.commit()
        conn.close()
    
    def show_comments(self, target_type, target_id):
        """显示评论列表"""
        conn = self.db.get_connection()
        
        df = pd.read_sql_query('''
        SELECT * FROM comments 
        WHERE target_type = ? AND target_id = ?
        ORDER BY timestamp DESC
        ''', conn, params=(target_type, target_id))
        
        conn.close()
        
        if not df.empty:
            st.markdown(f"**{len(df)} 条评论**")
            
            for _, comment in df.iterrows():
                with st.container():
                    col1, col2 = st.columns([1, 8])
                    
                    with col1:
                        # 用户头像
                        st.markdown(f"""
                        <div style="
                            width: 40px; 
                            height: 40px; 
                            border-radius: 50%; 
                            background: #1976d2; 
                            color: white; 
                            display: flex; 
                            align-items: center; 
                            justify-content: center; 
                            font-weight: bold;
                        ">
                            {comment['username'][0].upper()}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"**{comment['username']}**")
                        st.markdown(f"*{pd.to_datetime(comment['timestamp']).strftime('%Y-%m-%d %H:%M')}*")
                        st.markdown(comment['content'])
                    
                    st.markdown("---")
        else:
            st.markdown("*还没有评论，来发表第一条评论吧！*")

# 4. 主应用 (集成所有功能)
def main():
    st.set_page_config(
        page_title="广告思想简史",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 应用样式
    apply_china_friendly_styling()
    
    # 初始化服务
    db_manager = DatabaseManager()
    feedback_system = FeedbackSystem(db_manager)
    comment_system = CommentSystem(db_manager)
    
    # 认证系统
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=yaml.SafeLoader)
    
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )
    
    name, authentication_status, username = authenticator.login('登录', 'main')
    
    if authentication_status == False:
        st.error('❌ 用户名或密码错误')
    elif authentication_status == None:
        st.warning('👋 请输入用户名和密码')
    elif authentication_status:
        # 主应用界面
        authenticator.logout('退出登录', 'sidebar')
        st.sidebar.write(f'欢迎 **{name}**！ 👋')
        
        # 导航菜单
        page = st.sidebar.selectbox("导航", [
            "🏠 首页",
            "📅 广告年表", 
            "👥 广告人物",
            "🎯 经典广告",
            "📝 专家文章",
            "📊 行业数据"
        ])
        
        # 页面路由
        if page == "🏠 首页":
            show_homepage()
        elif page == "📅 广告年表":
            show_timeline()
            # 反馈 + 评论
            feedback_system.collect_feedback("timeline", "main", "thumbs")
            comment_system.display_comments("timeline", "main")
        elif page == "👥 广告人物":
            show_figures()
            feedback_system.collect_feedback("figures", "main", "stars")
            comment_system.display_comments("figures", "main")
        elif page == "🎯 经典广告":
            show_classic_campaigns()
            feedback_system.collect_feedback("campaigns", "main", "faces")
            comment_system.display_comments("campaigns", "main")
        elif page == "📝 专家文章":
            show_articles()
            feedback_system.collect_feedback("articles", "main", "stars")
            comment_system.display_comments("articles", "main")
        elif page == "📊 行业数据":
            show_data_visualization()
            feedback_system.collect_feedback("data", "main", "thumbs")
            comment_system.display_comments("data", "main")

# 页面函数示例
def show_homepage():
    st.markdown("# 🏠 欢迎来到广告思想简史")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## 📖 关于本书
        
        本书是广告思想史的开创之作，将广告史从"WHAT"(是什么）为主的记事模式转向"WHY+HOW"(为何和如何）为主的探究模式...
        
        ### 🎯 主要特色
        - 📚 **权威内容**: 基于卢泰宏教授的专业著作
        - 🌍 **国际视野**: 涵盖全球广告发展历程
        - 💡 **思想深度**: 深入分析广告背后的思想变迁
        - 🎨 **案例丰富**: 包含大量经典广告案例
        """)
    
    with col2:
        st.image("statics/cover.jpeg", caption="广告思想简史", width=300)

def apply_china_friendly_styling():
    """应用适合中国用户的样式"""
    st.markdown("""
    <style>
    /* 中国用户友好的样式 */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'PingFang SC', 'Microsoft YaHei', 'SimHei', sans-serif;
    }
    
    /* 反馈组件样式优化 */
    .streamlit-feedback {
        margin: 1rem 0;
        padding: 1rem;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* 统计卡片样式 */
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
```

## 🎯 **最终方案优势总结：**

### **✅ 完美的四合一组合：**
1. **Streamlit-Authenticator** - 用户认证管理
2. **Streamlit-Feedback** - 专业反馈收集
3. **SQLite数据库** - 本地数据存储
4. **阿里云部署** - 中国网络环境优化

### **📊 成本效益分析：**

| 项目 | 成本 | 说明 |
|------|------|------|
| 开发成本 | $1,500 | 2周开发时间 |
| 年运营成本 | $307 | 阿里云服务 |
| 组件成本 | $0 | 全部开源免费 |
| **总计第一年** | **$1,807** | 极具性价比 |

### **🚀 核心功能：**
- ✅ **用户认证** - 教授、学生、管理员角色
- ✅ **内容反馈** - 👍👎、⭐⭐⭐⭐⭐、😊😐😞
- ✅ **详细评论** - 文字评论系统
- ✅ **数据统计** - 实时反馈统计
- ✅ **文章管理** - 教授发布文章
- ✅ **中国优化** - 完全适合中国网络环境

### **🎯 为什么这是最佳选择：**
1. **零外部依赖** - 所有数据本地存储
2. **用户体验佳** - 直观的反馈界面
3. **数据价值高** - 收集用户满意度和详细反馈
4. **维护成本低** - SQLite + 开源组件
5. **扩展性强** - 可以轻松添加新功能

这个方案完美解决了您的所有需求，特别适合中国部署环境！🚀

### **被阻止的服务：**
- ❌ Google Sheets - 无法访问
- ❌ Google Drive API - 无法访问  
- ❌ Google Cloud Services - 不稳定
- ❌ Gmail API - 无法访问

### **可用的替代方案：**
- ✅ 阿里云数据库服务
- ✅ 腾讯云服务
- ✅ 本地SQLite数据库
- ✅ 阿里云OSS存储
- ✅ 国内邮件服务

## 🎯 **新推荐方案：阿里云原生解决方案**

### **架构调整：Streamlit + SQLite + 阿里云服务**

```python
# 中国部署优化的Streamlit应用
import streamlit as st
import streamlit_authenticator as stauth
import sqlite3
import pandas as pd
from datetime import datetime
import yaml
import smtplib
from email.mime.text import MIMEText
import hashlib

# 1. SQLite数据库管理器
class DatabaseManager:
    def __init__(self, db_path="data/adideas.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 评论表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            target_type TEXT NOT NULL,
            target_id TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            likes INTEGER DEFAULT 0,
            parent_id INTEGER,
            FOREIGN KEY (parent_id) REFERENCES comments (id)
        )
        ''')
        
        # 文章表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT,
            tags TEXT,
            author TEXT NOT NULL,
            status TEXT DEFAULT 'draft',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            views INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0
        )
        ''')
        
        # 用户活动日志
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            action TEXT NOT NULL,
            target_type TEXT,
            target_id TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)

# 2. 评论系统 (SQLite版本)
class CommentSystem:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def add_comment(self, username, target_type, target_id, content, parent_id=None):
        """添加评论"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO comments (username, target_type, target_id, content, parent_id)
        VALUES (?, ?, ?, ?, ?)
        ''', (username, target_type, target_id, content, parent_id))
        
        conn.commit()
        conn.close()
    
    def get_comments(self, target_type, target_id):
        """获取评论"""
        conn = self.db.get_connection()
        
        df = pd.read_sql_query('''
        SELECT * FROM comments 
        WHERE target_type = ? AND target_id = ?
        ORDER BY timestamp DESC
        ''', conn, params=(target_type, target_id))
        
        conn.close()
        return df
    
    def like_comment(self, comment_id, username):
        """点赞评论"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # 检查是否已经点赞
        cursor.execute('''
        SELECT COUNT(*) FROM user_activity 
        WHERE username = ? AND action = 'like_comment' AND target_id = ?
        ''', (username, str(comment_id)))
        
        if cursor.fetchone()[0] == 0:
            # 增加点赞数
            cursor.execute('''
            UPDATE comments SET likes = likes + 1 WHERE id = ?
            ''', (comment_id,))
            
            # 记录用户活动
            cursor.execute('''
            INSERT INTO user_activity (username, action, target_type, target_id)
            VALUES (?, 'like_comment', 'comment', ?)
            ''', (username, str(comment_id)))
            
            conn.commit()
        
        conn.close()
    
    def display_comments(self, target_type, target_id):
        """显示评论界面"""
        st.markdown("### 💬 评论区")
        
        # 评论输入
        if st.session_state.get("authentication_status"):
            with st.form(f"comment_form_{target_id}"):
                comment_text = st.text_area(
                    "写下你的评论...", 
                    placeholder="分享你对这个内容的看法...",
                    height=100
                )
                submitted = st.form_submit_button("发表评论")
                
                if submitted and comment_text.strip():
                    self.add_comment(
                        st.session_state["username"],
                        target_type,
                        target_id,
                        comment_text.strip()
                    )
                    st.success("评论发表成功！")
                    st.experimental_rerun()
        else:
            st.info("👤 请登录后发表评论")
        
        # 显示评论
        comments_df = self.get_comments(target_type, target_id)
        
        if not comments_df.empty:
            st.markdown(f"**{len(comments_df)} 条评论**")
            
            for _, comment in comments_df.iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([1, 8, 1])
                    
                    with col1:
                        # 用户头像
                        avatar_color = self.get_avatar_color(comment['username'])
                        st.markdown(f"""
                        <div style="
                            width: 40px; 
                            height: 40px; 
                            border-radius: 50%; 
                            background: {avatar_color}; 
                            color: white; 
                            display: flex; 
                            align-items: center; 
                            justify-content: center; 
                            font-weight: bold;
                            font-size: 14px;
                        ">
                            {comment['username'][0].upper()}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"**{comment['username']}**")
                        st.markdown(f"*{pd.to_datetime(comment['timestamp']).strftime('%Y-%m-%d %H:%M')}*")
                        st.markdown(comment['content'])
                    
                    with col3:
                        if st.session_state.get("authentication_status"):
                            if st.button(f"👍 {comment['likes']}", key=f"like_{comment['id']}"):
                                self.like_comment(comment['id'], st.session_state["username"])
                                st.experimental_rerun()
                    
                    st.markdown("---")
        else:
            st.markdown("*还没有评论，来发表第一条评论吧！*")
    
    def get_avatar_color(self, username):
        """根据用户名生成头像颜色"""
        colors = ['#1976d2', '#388e3c', '#f57c00', '#d32f2f', '#7b1fa2', '#0288d1']
        hash_value = int(hashlib.md5(username.encode()).hexdigest(), 16)
        return colors[hash_value % len(colors)]

# 3. 文章管理系统
class ArticleManager:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def save_article(self, title, content, category, tags, author, status='draft'):
        """保存文章"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO articles (title, content, category, tags, author, status)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, content, category, ','.join(tags), author, status))
        
        conn.commit()
        conn.close()
    
    def get_articles(self, status=None, author=None):
        """获取文章列表"""
        conn = self.db.get_connection()
        
        query = "SELECT * FROM articles"
        params = []
        
        if status or author:
            query += " WHERE "
            conditions = []
            if status:
                conditions.append("status = ?")
                params.append(status)
            if author:
                conditions.append("author = ?")
                params.append(author)
            query += " AND ".join(conditions)
        
        query += " ORDER BY created_at DESC"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    
    def create_article_editor(self):
        """文章编辑器"""
        if not st.session_state.get("authentication_status"):
            st.warning("请登录后撰写文章")
            return
        
        user_role = self.get_user_role(st.session_state["username"])
        
        if user_role not in ["professor", "admin"]:
            st.warning("只有教授和管理员可以撰写文章")
            return
        
        st.markdown("### ✍️ 撰写新文章")
        
        with st.form("article_form"):
            title = st.text_input("文章标题", placeholder="输入吸引人的标题...")
            
            col1, col2 = st.columns(2)
            with col1:
                category = st.selectbox("分类", [
                    "广告理论",
                    "历史分析", 
                    "案例研究",
                    "行业趋势",
                    "创意策略"
                ])
            
            with col2:
                tags = st.multiselect("标签", [
                    "广告", "营销", "品牌", "数字化", 
                    "创意", "策略", "历史", "理论", "案例研究"
                ])
            
            content = st.text_area(
                "文章内容", 
                height=400,
                placeholder="在这里撰写你的文章内容，支持Markdown格式..."
            )
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                save_draft = st.form_submit_button("💾 保存草稿")
            with col2:
                submit_review = st.form_submit_button("📝 提交审核")
            with col3:
                if user_role == "admin":
                    publish = st.form_submit_button("🚀 发布")
            
            if save_draft and title and content:
                self.save_article(title, content, category, tags, 
                                st.session_state["username"], "draft")
                st.success("草稿保存成功！")
            
            elif submit_review and title and content:
                self.save_article(title, content, category, tags, 
                                st.session_state["username"], "review")
                st.success("文章已提交审核！")
            
            elif user_role == "admin" and publish and title and content:
                self.save_article(title, content, category, tags, 
                                st.session_state["username"], "published")
                st.success("文章已发布！")
    
    def get_user_role(self, username):
        """获取用户角色"""
        # 从配置文件获取用户角色
        with open('config.yaml') as file:
            config = yaml.load(file, Loader=yaml.SafeLoader)
        
        user_info = config.get('credentials', {}).get('usernames', {}).get(username, {})
        return user_info.get('role', 'student')

# 4. 邮件服务 (使用国内邮件服务)
class EmailService:
    def __init__(self):
        # 使用阿里云邮件服务或其他国内邮件服务
        self.smtp_server = "smtpdm.aliyun.com"  # 阿里云邮件服务
        self.smtp_port = 465
        self.username = st.secrets.get("EMAIL_USERNAME", "")
        self.password = st.secrets.get("EMAIL_PASSWORD", "")
    
    def send_notification(self, to_email, subject, content):
        """发送邮件通知"""
        try:
            msg = MIMEText(content, 'html', 'utf-8')
            msg['Subject'] = subject
            msg['From'] = self.username
            msg['To'] = to_email
            
            server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            st.error(f"邮件发送失败: {e}")
            return False

# 5. 主应用
def main():
    st.set_page_config(
        page_title="广告思想简史",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 应用中国用户友好的样式
    apply_china_friendly_styling()
    
    # 初始化服务
    db_manager = DatabaseManager()
    comment_system = CommentSystem(db_manager)
    article_manager = ArticleManager(db_manager)
    email_service = EmailService()
    
    # 认证系统
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=yaml.SafeLoader)
    
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )
    
    name, authentication_status, username = authenticator.login('登录', 'main')
    
    if authentication_status == False:
        st.error('❌ 用户名或密码错误')
    elif authentication_status == None:
        st.warning('👋 请输入用户名和密码')
        
        # 注册选项
        with st.expander("🆕 新用户注册"):
            try:
                if authenticator.register_user('注册用户', preauthorization=False):
                    st.success('用户注册成功！')
                    # 更新配置文件
                    with open('config.yaml', 'w') as file:
                        yaml.dump(config, file, default_flow_style=False)
            except Exception as e:
                st.error(e)
    
    elif authentication_status:
        # 主应用界面
        authenticator.logout('退出登录', 'sidebar')
        st.sidebar.write(f'欢迎 **{name}**！ 👋')
        
        # 导航菜单
        page = st.sidebar.selectbox("导航", [
            "🏠 首页",
            "📅 广告年表", 
            "👥 广告人物",
            "🎯 经典广告",
            "📝 专家文章",
            "📊 行业数据"
        ])
        
        # 页面路由
        if page == "🏠 首页":
            show_homepage()
        elif page == "📅 广告年表":
            show_timeline()
            comment_system.display_comments("timeline", "main")
        elif page == "👥 广告人物":
            show_figures()
            comment_system.display_comments("figures", "main")
        elif page == "🎯 经典广告":
            show_classic_campaigns()
            comment_system.display_comments("campaigns", "main")
        elif page == "📝 专家文章":
            show_articles(article_manager)
            article_manager.create_article_editor()
        elif page == "📊 行业数据":
            show_data_visualization()
            comment_system.display_comments("data", "main")

def apply_china_friendly_styling():
    """应用适合中国用户的样式"""
    st.markdown("""
    <style>
    /* 中国用户友好的样式 */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'PingFang SC', 'Microsoft YaHei', 'SimHei', sans-serif;
    }
    
    /* 主容器 */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* 中文标题优化 */
    h1, h2, h3 {
        font-family: 'PingFang SC', 'Microsoft YaHei', 'SimHei', sans-serif;
        font-weight: 500;
    }
    
    h1 {
        color: #d32f2f;
        border-bottom: 3px solid #d32f2f;
        padding-bottom: 0.5rem;
    }
    
    h2 {
        color: #1976d2;
    }
    
    h3 {
        color: #388e3c;
    }
    
    /* 卡片样式 */
    .stContainer > div {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #d32f2f;
    }
    
    /* 按钮样式 - 中国红主题 */
    .stButton > button {
        background: linear-gradient(45deg, #d32f2f, #f44336);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(211, 47, 47, 0.3);
    }
    
    /* 侧边栏样式 */
    .css-1d391kg {
        background: linear-gradient(180deg, #d32f2f, #c62828);
    }
    
    /* 表单优化 */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
        border-radius: 8px;
        border: 2px solid #e0e0e0;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #d32f2f;
        box-shadow: 0 0 0 2px rgba(211, 47, 47, 0.2);
    }
    
    /* 移动端优化 */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }
        
        .stContainer > div {
            padding: 1rem;
        }
        
        h1 {
            font-size: 1.5rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# 页面函数示例
def show_homepage():
    st.markdown("# 🏠 欢迎来到广告思想简史")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## 📖 关于本书
        
        本书是广告思想史的开创之作，将广告史从"WHAT"(是什么）为主的记事模式转向"WHY+HOW"(为何和如何）为主的探究模式...
        
        ### 🎯 主要特色
        - 📚 **权威内容**: 基于卢泰宏教授的专业著作
        - 🌍 **国际视野**: 涵盖全球广告发展历程
        - 💡 **思想深度**: 深入分析广告背后的思想变迁
        - 🎨 **案例丰富**: 包含大量经典广告案例
        """)
    
    with col2:
        st.image("statics/cover.jpeg", caption="广告思想简史", width=300)
    
    # 统计数据
    st.markdown("## 📊 平台数据")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("历史跨度", "120+年", "1450-2020")
    with col2:
        st.metric("广告人物", "100+位", "行业巨星")
    with col3:
        st.metric("经典广告", "100+个", "成功案例")
    with col4:
        st.metric("专家文章", "50+篇", "持续更新")

def show_articles(article_manager):
    st.markdown("# 📝 专家文章")
    
    # 显示已发布的文章
    published_articles = article_manager.get_articles(status='published')
    
    if not published_articles.empty:
        for _, article in published_articles.iterrows():
            with st.expander(f"📄 {article['title']} - {article['author']}"):
                st.markdown(f"**分类**: {article['category']}")
                st.markdown(f"**标签**: {article['tags']}")
                st.markdown(f"**发布时间**: {pd.to_datetime(article['created_at']).strftime('%Y-%m-%d')}")
                st.markdown("---")
                st.markdown(article['content'])
    else:
        st.info("暂无已发布的文章")

if __name__ == "__main__":
    main()
```

## 🎯 **中国部署优化方案总结**

### **✅ 完全适合中国环境：**

1. **SQLite数据库** - 本地存储，无网络依赖
2. **阿里云邮件服务** - 替代Gmail
3. **本地文件存储** - 替代Google Drive
4. **中文优化界面** - 适合中国用户习惯
5. **阿里云OSS** - 文件存储服务

### **📊 成本分析：**

| 服务 | 月费用 | 年费用 | 说明 |
|------|--------|--------|------|
| 阿里云ECS | ¥100 | ¥1,200 | 2核4G服务器 |
| 阿里云邮件服务 | ¥50 | ¥600 | 基础版 |
| 阿里云OSS | ¥20 | ¥240 | 文件存储 |
| 域名+SSL | ¥10 | ¥120 | .com域名 |
| **总计** | **¥180** | **¥2,160** |

### **🚀 部署优势：**

- ✅ **完全合规** - 符合中国网络环境
- ✅ **访问稳定** - 无需翻墙，速度快
- ✅ **数据安全** - 数据存储在中国境内
- ✅ **成本可控** - 年费用仅¥2,160
- ✅ **易于维护** - SQLite简单可靠

### **🎯 实施建议：**

1. **立即采用SQLite方案** - 避免Google服务依赖
2. **使用阿里云全家桶** - 邮件、存储、服务器一体化
3. **优化中文体验** - 字体、颜色、交互习惯
4. **备份策略** - 定期备份SQLite数据库到阿里云OSS

这个方案完美解决了中国部署的所有问题！