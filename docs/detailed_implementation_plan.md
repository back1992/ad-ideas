# 广告思想简史平台详细实施计划

## 🎯 项目概述

**目标**: 基于Streamlit构建专业的广告学术平台，支持用户认证、内容反馈、评论系统和文章管理

**技术栈**: Streamlit + Streamlit-Authenticator + Streamlit-Feedback + SQLite + 阿里云

**时间线**: 2周开发 + 1周测试部署

**预算**: $1,500开发 + $272/年运营

---

## 📅 第一周：核心功能开发

### Day 1: 项目初始化和环境搭建

#### 🔧 环境准备
```bash
# 1. 创建项目目录
mkdir ad-ideas-platform
cd ad-ideas-platform

# 2. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 3. 安装依赖包
pip install streamlit==1.37.1
pip install streamlit-authenticator==0.3.3
pip install streamlit-feedback==0.1.4
pip install pandas==2.1.0
pip install pyyaml==6.0.1
pip install bcrypt==4.0.1
pip install python-dotenv==1.0.1

# 4. 创建requirements.txt
pip freeze > requirements.txt
```

#### 📁 项目结构
```
ad-ideas-platform/
├── .env                    # 环境变量
├── .gitignore             # Git忽略文件
├── requirements.txt       # Python依赖
├── config.yaml           # 用户认证配置
├── streamlit_app.py      # 主应用入口
├── data/                 # 数据目录
│   ├── adideas.db        # SQLite数据库
│   └── content/          # 内容文件
├── modules/              # 功能模块
│   ├── __init__.py
│   ├── database.py       # 数据库管理
│   ├── auth.py          # 认证管理
│   ├── feedback.py      # 反馈系统
│   ├── comments.py      # 评论系统
│   └── articles.py      # 文章管理
├── pages/               # 页面模块
│   ├── __init__.py
│   ├── homepage.py      # 首页
│   ├── timeline.py      # 广告年表
│   ├── figures.py       # 广告人物
│   ├── campaigns.py     # 经典广告
│   ├── articles.py      # 专家文章
│   └── data_viz.py      # 数据可视化
├── static/              # 静态资源
│   ├── css/
│   ├── images/
│   └── data/
└── utils/               # 工具函数
    ├── __init__.py
    ├── helpers.py
    └── constants.py
```
### Day 2: 数据库设计和基础模块

#### 🗄️ 数据库设计 (modules/database.py)
```python
import sqlite3
import pandas as pd
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self, db_path="data/adideas.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """初始化所有数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 用户反馈表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            target_type TEXT NOT NULL,
            target_id TEXT NOT NULL,
            feedback_type TEXT NOT NULL,
            feedback_value INTEGER,
            feedback_text TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            user_agent TEXT
        )
        ''')
        
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
            is_approved BOOLEAN DEFAULT 1,
            FOREIGN KEY (parent_id) REFERENCES comments (id)
        )
        ''')
        
        # 文章表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            excerpt TEXT,
            category TEXT,
            tags TEXT,
            author TEXT NOT NULL,
            status TEXT DEFAULT 'draft',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            published_at DATETIME,
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
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(target_type, target_id)
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
            details TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ 数据库初始化完成")
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def execute_query(self, query, params=None):
        """执行查询并返回结果"""
        conn = self.get_connection()
        try:
            if params:
                result = pd.read_sql_query(query, conn, params=params)
            else:
                result = pd.read_sql_query(query, conn)
            return result
        finally:
            conn.close()
    
    def execute_update(self, query, params=None):
        """执行更新操作"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()
```

#### 🔐 认证系统 (modules/auth.py)
```python
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import bcrypt

class AuthManager:
    def __init__(self, config_path="config.yaml"):
        self.config_path = config_path
        self.load_config()
        self.setup_authenticator()
    
    def load_config(self):
        """加载认证配置"""
        try:
            with open(self.config_path) as file:
                self.config = yaml.load(file, Loader=SafeLoader)
        except FileNotFoundError:
            # 创建默认配置
            self.create_default_config()
    
    def create_default_config(self):
        """创建默认认证配置"""
        default_config = {
            'credentials': {
                'usernames': {
                    'admin': {
                        'email': 'admin@adideas.com',
                        'name': 'Administrator',
                        'password': self.hash_password('admin123'),
                        'role': 'admin'
                    },
                    'professor_lu': {
                        'email': 'lu@university.edu',
                        'name': '卢泰宏教授',
                        'password': self.hash_password('professor123'),
                        'role': 'professor'
                    },
                    'student_demo': {
                        'email': 'student@university.edu',
                        'name': '演示学生',
                        'password': self.hash_password('student123'),
                        'role': 'student'
                    }
                }
            },
            'cookie': {
                'expiry_days': 30,
                'key': 'ad_ideas_auth_key',
                'name': 'ad_ideas_auth_cookie'
            },
            'preauthorized': {
                'emails': ['admin@adideas.com']
            }
        }
        
        with open(self.config_path, 'w') as file:
            yaml.dump(default_config, file, default_flow_style=False)
        
        self.config = default_config
        print("✅ 创建默认认证配置")
    
    def hash_password(self, password):
        """哈希密码"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def setup_authenticator(self):
        """设置认证器"""
        self.authenticator = stauth.Authenticate(
            self.config['credentials'],
            self.config['cookie']['name'],
            self.config['cookie']['key'],
            self.config['cookie']['expiry_days'],
            self.config['preauthorized']
        )
    
    def login(self):
        """用户登录"""
        return self.authenticator.login('登录', 'main')
    
    def logout(self):
        """用户登出"""
        self.authenticator.logout('退出登录', 'sidebar')
    
    def register_user(self):
        """用户注册"""
        try:
            if self.authenticator.register_user('注册新用户', preauthorization=False):
                st.success('用户注册成功！请联系管理员激活账户。')
                # 保存更新的配置
                with open(self.config_path, 'w') as file:
                    yaml.dump(self.config, file, default_flow_style=False)
                return True
        except Exception as e:
            st.error(f'注册失败: {e}')
        return False
    
    def get_user_role(self, username):
        """获取用户角色"""
        user_info = self.config.get('credentials', {}).get('usernames', {}).get(username, {})
        return user_info.get('role', 'student')
    
    def is_professor_or_admin(self, username):
        """检查是否为教授或管理员"""
        role = self.get_user_role(username)
        return role in ['professor', 'admin']
```
### Day 3: 反馈系统开发

#### 💭 反馈系统 (modules/feedback.py)
```python
import streamlit as st
from streamlit_feedback import streamlit_feedback
import pandas as pd
from datetime import datetime
from .database import DatabaseManager

class FeedbackSystem:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def collect_feedback(self, target_type, target_id, feedback_type="thumbs", 
                        title="您觉得这个内容怎么样？", 
                        optional_text_label="请提供更多反馈 (可选)"):
        """收集用户反馈"""
        
        if not st.session_state.get("authentication_status"):
            st.info("👤 登录后可以对内容进行评价")
            self.show_feedback_stats(target_type, target_id)
            return None
        
        username = st.session_state["username"]
        
        # 检查用户是否已经反馈过
        if self.has_user_feedback(username, target_type, target_id):
            st.success("✅ 您已经对此内容进行过评价")
            self.show_user_feedback(username, target_type, target_id)
            self.show_feedback_stats(target_type, target_id)
            return None
        
        st.markdown(f"### 💭 {title}")
        
        # 根据反馈类型显示不同的说明
        feedback_instructions = {
            "thumbs": "👍 赞同 / 👎 不赞同",
            "stars": "⭐ 1星(很差) - ⭐⭐⭐⭐⭐ 5星(很好)",
            "faces": "😞 不满意 - 😐 一般 - 😊 满意"
        }
        
        st.caption(feedback_instructions.get(feedback_type, "请选择您的评价"))
        
        # 使用streamlit-feedback组件
        feedback = streamlit_feedback(
            feedback_type=feedback_type,
            optional_text_label=optional_text_label,
            key=f"feedback_{target_type}_{target_id}_{username}"
        )
        
        if feedback:
            # 保存反馈到数据库
            success = self.save_feedback(
                username=username,
                target_type=target_type,
                target_id=target_id,
                feedback_type=feedback_type,
                feedback_value=feedback.get("score"),
                feedback_text=feedback.get("text", "")
            )
            
            if success:
                # 更新统计数据
                self.update_content_stats(target_type, target_id)
                
                # 记录用户活动
                self.log_user_activity(username, "feedback", target_type, target_id, 
                                     f"{feedback_type}:{feedback.get('score')}")
                
                st.success("🎉 感谢您的反馈！")
                st.balloons()
                st.experimental_rerun()
        
        # 显示当前统计
        self.show_feedback_stats(target_type, target_id)
    
    def save_feedback(self, username, target_type, target_id, feedback_type, 
                     feedback_value, feedback_text):
        """保存反馈到数据库"""
        try:
            query = '''
            INSERT INTO user_feedback 
            (username, target_type, target_id, feedback_type, feedback_value, feedback_text)
            VALUES (?, ?, ?, ?, ?, ?)
            '''
            params = (username, target_type, target_id, feedback_type, feedback_value, feedback_text)
            
            self.db.execute_update(query, params)
            return True
        except Exception as e:
            st.error(f"保存反馈失败: {e}")
            return False
    
    def has_user_feedback(self, username, target_type, target_id):
        """检查用户是否已经反馈过"""
        query = '''
        SELECT COUNT(*) as count FROM user_feedback 
        WHERE username = ? AND target_type = ? AND target_id = ?
        '''
        result = self.db.execute_query(query, (username, target_type, target_id))
        return result.iloc[0]['count'] > 0
    
    def show_user_feedback(self, username, target_type, target_id):
        """显示用户的反馈"""
        query = '''
        SELECT feedback_type, feedback_value, feedback_text, timestamp 
        FROM user_feedback
        WHERE username = ? AND target_type = ? AND target_id = ?
        ORDER BY timestamp DESC LIMIT 1
        '''
        result = self.db.execute_query(query, (username, target_type, target_id))
        
        if not result.empty:
            feedback = result.iloc[0]
            
            # 显示反馈图标
            feedback_icons = {
                "thumbs": "👍" if feedback['feedback_value'] == 1 else "👎",
                "stars": "⭐" * (feedback['feedback_value'] + 1),
                "faces": ["😞", "😐", "🙂", "😊", "😍"][feedback['feedback_value']]
            }
            
            icon = feedback_icons.get(feedback['feedback_type'], "📝")
            
            st.info(f"您的评价: {icon} {feedback['feedback_text']}")
    
    def update_content_stats(self, target_type, target_id):
        """更新内容统计数据"""
        # 获取所有反馈数据
        query = '''
        SELECT feedback_type, feedback_value FROM user_feedback
        WHERE target_type = ? AND target_id = ?
        '''
        feedbacks = self.db.execute_query(query, (target_type, target_id))
        
        if feedbacks.empty:
            return
        
        thumbs_up = thumbs_down = 0
        star_ratings = []
        face_ratings = []
        
        for _, row in feedbacks.iterrows():
            feedback_type = row['feedback_type']
            value = row['feedback_value']
            
            if feedback_type == "thumbs":
                if value == 1:
                    thumbs_up += 1
                else:
                    thumbs_down += 1
            elif feedback_type == "stars":
                star_ratings.append(value + 1)  # 转换为1-5星
            elif feedback_type == "faces":
                face_ratings.append(value + 1)  # 转换为1-5分
        
        avg_stars = sum(star_ratings) / len(star_ratings) if star_ratings else 0
        avg_faces = sum(face_ratings) / len(face_ratings) if face_ratings else 0
        
        # 更新或插入统计数据
        update_query = '''
        INSERT OR REPLACE INTO content_stats 
        (target_type, target_id, thumbs_up, thumbs_down, avg_stars, total_ratings, last_updated)
        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        '''
        
        params = (target_type, target_id, thumbs_up, thumbs_down, 
                 max(avg_stars, avg_faces), len(feedbacks))
        
        self.db.execute_update(update_query, params)
    
    def show_feedback_stats(self, target_type, target_id):
        """显示反馈统计"""
        query = '''
        SELECT thumbs_up, thumbs_down, avg_stars, total_ratings 
        FROM content_stats
        WHERE target_type = ? AND target_id = ?
        '''
        result = self.db.execute_query(query, (target_type, target_id))
        
        if not result.empty:
            stats = result.iloc[0]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("👍 赞", int(stats['thumbs_up']))
            with col2:
                st.metric("👎 踩", int(stats['thumbs_down']))
            with col3:
                if stats['avg_stars'] > 0:
                    st.metric("⭐ 平均评分", f"{stats['avg_stars']:.1f}")
                else:
                    st.metric("⭐ 平均评分", "暂无")
            with col4:
                st.metric("📊 总评价", int(stats['total_ratings']))
        else:
            st.info("暂无评价数据")
    
    def log_user_activity(self, username, action, target_type, target_id, details):
        """记录用户活动"""
        query = '''
        INSERT INTO user_activity (username, action, target_type, target_id, details)
        VALUES (?, ?, ?, ?, ?)
        '''
        params = (username, action, target_type, target_id, details)
        self.db.execute_update(query, params)
    
    def get_feedback_analytics(self, target_type=None, days=30):
        """获取反馈分析数据"""
        base_query = '''
        SELECT 
            target_type,
            target_id,
            feedback_type,
            feedback_value,
            feedback_text,
            timestamp
        FROM user_feedback
        WHERE timestamp >= datetime('now', '-{} days')
        '''.format(days)
        
        if target_type:
            base_query += f" AND target_type = '{target_type}'"
        
        base_query += " ORDER BY timestamp DESC"
        
        return self.db.execute_query(base_query)
```
### Day 4: 评论系统开发

#### 💬 评论系统 (modules/comments.py)
```python
import streamlit as st
import pandas as pd
from datetime import datetime
import hashlib
from .database import DatabaseManager

class CommentSystem:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def display_comments_section(self, target_type, target_id, title="💬 评论区"):
        """显示完整的评论区域"""
        st.markdown(f"### {title}")
        
        # 评论输入区
        self.show_comment_input(target_type, target_id)
        
        # 评论列表
        self.show_comments_list(target_type, target_id)
    
    def show_comment_input(self, target_type, target_id):
        """显示评论输入区域"""
        if not st.session_state.get("authentication_status"):
            st.info("👤 请登录后发表评论")
            return
        
        username = st.session_state["username"]
        
        with st.form(f"comment_form_{target_type}_{target_id}"):
            st.markdown("#### ✍️ 发表评论")
            
            comment_text = st.text_area(
                "写下你的评论...", 
                placeholder="分享你对这个内容的详细看法，支持建设性的讨论...",
                height=120,
                help="请保持友善和专业的讨论氛围"
            )
            
            col1, col2 = st.columns([1, 4])
            
            with col1:
                submitted = st.form_submit_button("发表评论", type="primary")
            
            with col2:
                if submitted and not comment_text.strip():
                    st.warning("请输入评论内容")
            
            if submitted and comment_text.strip():
                success = self.add_comment(username, target_type, target_id, comment_text.strip())
                if success:
                    st.success("✅ 评论发表成功！")
                    st.experimental_rerun()
    
    def add_comment(self, username, target_type, target_id, content, parent_id=None):
        """添加评论"""
        try:
            query = '''
            INSERT INTO comments (username, target_type, target_id, content, parent_id)
            VALUES (?, ?, ?, ?, ?)
            '''
            params = (username, target_type, target_id, content, parent_id)
            
            self.db.execute_update(query, params)
            
            # 记录用户活动
            self.log_user_activity(username, "comment", target_type, target_id, f"评论长度:{len(content)}")
            
            return True
        except Exception as e:
            st.error(f"发表评论失败: {e}")
            return False
    
    def show_comments_list(self, target_type, target_id):
        """显示评论列表"""
        comments = self.get_comments(target_type, target_id)
        
        if comments.empty:
            st.markdown("---")
            st.info("🌟 还没有评论，来发表第一条评论吧！")
            return
        
        st.markdown("---")
        st.markdown(f"**📝 共 {len(comments)} 条评论**")
        
        # 按时间倒序显示评论
        for _, comment in comments.iterrows():
            self.render_comment(comment, target_type, target_id)
    
    def render_comment(self, comment, target_type, target_id):
        """渲染单个评论"""
        with st.container():
            col1, col2, col3 = st.columns([1, 10, 1])
            
            with col1:
                # 用户头像
                avatar_color = self.get_avatar_color(comment['username'])
                st.markdown(f"""
                <div style="
                    width: 45px; 
                    height: 45px; 
                    border-radius: 50%; 
                    background: {avatar_color}; 
                    color: white; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    font-weight: bold;
                    font-size: 16px;
                    margin-top: 5px;
                ">
                    {comment['username'][0].upper()}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # 评论内容
                st.markdown(f"**{comment['username']}**")
                
                # 时间戳
                comment_time = pd.to_datetime(comment['timestamp'])
                time_str = comment_time.strftime('%Y-%m-%d %H:%M')
                st.caption(f"🕒 {time_str}")
                
                # 评论文本
                st.markdown(comment['content'])
                
                # 评论操作
                self.render_comment_actions(comment, target_type, target_id)
            
            with col3:
                # 点赞按钮
                if st.session_state.get("authentication_status"):
                    if st.button(f"👍 {comment['likes']}", 
                               key=f"like_{comment['id']}", 
                               help="点赞这条评论"):
                        self.like_comment(comment['id'], st.session_state["username"])
                        st.experimental_rerun()
                else:
                    st.markdown(f"👍 {comment['likes']}")
            
            st.markdown("---")
    
    def render_comment_actions(self, comment, target_type, target_id):
        """渲染评论操作按钮"""
        if not st.session_state.get("authentication_status"):
            return
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("💬 回复", key=f"reply_{comment['id']}", help="回复这条评论"):
                st.session_state[f"replying_to_{comment['id']}"] = True
                st.experimental_rerun()
        
        with col2:
            # 举报按钮
            if st.button("🚩 举报", key=f"report_{comment['id']}", help="举报不当内容"):
                self.report_comment(comment['id'], st.session_state["username"])
        
        # 回复输入框
        if st.session_state.get(f"replying_to_{comment['id']}", False):
            with st.form(f"reply_form_{comment['id']}"):
                reply_text = st.text_area(
                    f"回复 @{comment['username']}:",
                    placeholder="写下你的回复...",
                    height=80
                )
                
                col_submit, col_cancel = st.columns([1, 1])
                
                with col_submit:
                    reply_submitted = st.form_submit_button("发表回复")
                
                with col_cancel:
                    if st.form_submit_button("取消"):
                        st.session_state[f"replying_to_{comment['id']}"] = False
                        st.experimental_rerun()
                
                if reply_submitted and reply_text.strip():
                    success = self.add_comment(
                        st.session_state["username"], 
                        target_type, 
                        target_id, 
                        reply_text.strip(), 
                        parent_id=comment['id']
                    )
                    if success:
                        st.session_state[f"replying_to_{comment['id']}"] = False
                        st.success("回复发表成功！")
                        st.experimental_rerun()
    
    def get_comments(self, target_type, target_id):
        """获取评论列表"""
        query = '''
        SELECT * FROM comments 
        WHERE target_type = ? AND target_id = ? AND is_approved = 1
        ORDER BY timestamp DESC
        '''
        return self.db.execute_query(query, (target_type, target_id))
    
    def like_comment(self, comment_id, username):
        """点赞评论"""
        # 检查是否已经点赞
        check_query = '''
        SELECT COUNT(*) as count FROM user_activity 
        WHERE username = ? AND action = 'like_comment' AND target_id = ?
        '''
        result = self.db.execute_query(check_query, (username, str(comment_id)))
        
        if result.iloc[0]['count'] == 0:
            # 增加点赞数
            update_query = '''
            UPDATE comments SET likes = likes + 1 WHERE id = ?
            '''
            self.db.execute_update(update_query, (comment_id,))
            
            # 记录用户活动
            self.log_user_activity(username, "like_comment", "comment", str(comment_id), "点赞评论")
            
            st.success("👍 点赞成功！")
        else:
            st.warning("您已经点赞过这条评论了")
    
    def report_comment(self, comment_id, username):
        """举报评论"""
        # 记录举报
        self.log_user_activity(username, "report_comment", "comment", str(comment_id), "举报评论")
        st.warning("🚩 举报已提交，管理员将会审核处理")
    
    def get_avatar_color(self, username):
        """根据用户名生成头像颜色"""
        colors = [
            '#1976d2', '#388e3c', '#f57c00', '#d32f2f', 
            '#7b1fa2', '#0288d1', '#5d4037', '#455a64'
        ]
        hash_value = int(hashlib.md5(username.encode()).hexdigest(), 16)
        return colors[hash_value % len(colors)]
    
    def log_user_activity(self, username, action, target_type, target_id, details):
        """记录用户活动"""
        query = '''
        INSERT INTO user_activity (username, action, target_type, target_id, details)
        VALUES (?, ?, ?, ?, ?)
        '''
        params = (username, action, target_type, target_id, details)
        self.db.execute_update(query, params)
    
    def get_comment_stats(self, target_type=None, days=30):
        """获取评论统计"""
        base_query = '''
        SELECT 
            COUNT(*) as total_comments,
            COUNT(DISTINCT username) as unique_users,
            AVG(LENGTH(content)) as avg_length
        FROM comments
        WHERE timestamp >= datetime('now', '-{} days')
        '''.format(days)
        
        if target_type:
            base_query += f" AND target_type = '{target_type}'"
        
        return self.db.execute_query(base_query)
    
    def moderate_comments(self, username):
        """评论审核 (管理员功能)"""
        if not self.is_admin(username):
            st.error("权限不足")
            return
        
        st.markdown("### 🛡️ 评论审核")
        
        # 获取待审核评论
        pending_query = '''
        SELECT * FROM comments 
        WHERE is_approved = 0
        ORDER BY timestamp DESC
        '''
        pending_comments = self.db.execute_query(pending_query)
        
        if pending_comments.empty:
            st.success("✅ 暂无待审核评论")
            return
        
        for _, comment in pending_comments.iterrows():
            with st.expander(f"评论 #{comment['id']} - {comment['username']}"):
                st.markdown(f"**内容**: {comment['content']}")
                st.markdown(f"**时间**: {comment['timestamp']}")
                st.markdown(f"**目标**: {comment['target_type']} - {comment['target_id']}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button(f"✅ 批准", key=f"approve_{comment['id']}"):
                        self.approve_comment(comment['id'])
                        st.experimental_rerun()
                
                with col2:
                    if st.button(f"❌ 拒绝", key=f"reject_{comment['id']}"):
                        self.reject_comment(comment['id'])
                        st.experimental_rerun()
    
    def approve_comment(self, comment_id):
        """批准评论"""
        query = "UPDATE comments SET is_approved = 1 WHERE id = ?"
        self.db.execute_update(query, (comment_id,))
    
    def reject_comment(self, comment_id):
        """拒绝评论"""
        query = "DELETE FROM comments WHERE id = ?"
        self.db.execute_update(query, (comment_id,))
    
    def is_admin(self, username):
        """检查是否为管理员"""
        # 这里应该从认证系统获取用户角色
        return username == 'admin'  # 简化实现
```
### Day 5: 文章管理系统

#### 📝 文章管理 (modules/articles.py)
```python
import streamlit as st
import pandas as pd
from datetime import datetime
import re
from .database import DatabaseManager

class ArticleManager:
    def __init__(self, db_manager, auth_manager):
        self.db = db_manager
        self.auth = auth_manager
    
    def show_article_editor(self):
        """显示文章编辑器"""
        if not st.session_state.get("authentication_status"):
            st.warning("请登录后撰写文章")
            return
        
        username = st.session_state["username"]
        user_role = self.auth.get_user_role(username)
        
        if not self.auth.is_professor_or_admin(username):
            st.warning("只有教授和管理员可以撰写文章")
            return
        
        st.markdown("### ✍️ 撰写新文章")
        
        with st.form("article_editor_form"):
            # 文章基本信息
            col1, col2 = st.columns([2, 1])
            
            with col1:
                title = st.text_input(
                    "文章标题 *", 
                    placeholder="输入吸引人的标题...",
                    help="标题应该简洁明了，能够准确概括文章内容"
                )
            
            with col2:
                category = st.selectbox("分类 *", [
                    "广告理论",
                    "历史分析", 
                    "案例研究",
                    "行业趋势",
                    "创意策略",
                    "数字营销",
                    "品牌建设",
                    "消费者行为"
                ])
            
            # 文章摘要
            excerpt = st.text_area(
                "文章摘要",
                placeholder="简要描述文章的主要内容和观点...",
                height=80,
                help="摘要将显示在文章列表中，建议100-200字"
            )
            
            # 标签选择
            available_tags = [
                "广告", "营销", "品牌", "数字化", "创意", "策略", 
                "历史", "理论", "案例研究", "消费者", "媒体", "传播",
                "设计", "心理学", "社会学", "经济学", "技术", "创新"
            ]
            
            tags = st.multiselect(
                "标签",
                available_tags,
                help="选择相关标签，有助于读者发现您的文章"
            )
            
            # 文章内容
            st.markdown("#### 📄 文章内容 *")
            content = st.text_area(
                "正文内容",
                placeholder="""请在这里撰写您的文章内容...

支持Markdown格式：
- **粗体文本**
- *斜体文本*
- [链接](http://example.com)
- ![图片](image_url)

建议结构：
1. 引言
2. 主要观点
3. 案例分析
4. 结论
""",
                height=500,
                help="支持Markdown格式，建议文章长度1000-5000字"
            )
            
            # 提交选项
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                save_draft = st.form_submit_button("💾 保存草稿", help="保存为草稿，稍后继续编辑")
            
            with col2:
                submit_review = st.form_submit_button("📝 提交审核", help="提交给管理员审核")
            
            with col3:
                if user_role == "admin":
                    publish_directly = st.form_submit_button("🚀 直接发布", help="管理员可以直接发布")
            
            with col4:
                preview = st.form_submit_button("👁️ 预览", help="预览文章效果")
            
            # 处理表单提交
            if save_draft:
                if title and content:
                    self.save_article(title, content, category, tags, username, "draft", excerpt)
                    st.success("✅ 草稿保存成功！")
                else:
                    st.error("请填写标题和内容")
            
            elif submit_review:
                if title and content:
                    self.save_article(title, content, category, tags, username, "review", excerpt)
                    st.success("✅ 文章已提交审核！管理员将尽快处理。")
                else:
                    st.error("请填写标题和内容")
            
            elif user_role == "admin" and publish_directly:
                if title and content:
                    self.save_article(title, content, category, tags, username, "published", excerpt)
                    st.success("🚀 文章已发布！")
                    st.balloons()
                else:
                    st.error("请填写标题和内容")
            
            elif preview:
                if title and content:
                    self.preview_article(title, content, category, tags, excerpt)
    
    def save_article(self, title, content, category, tags, author, status, excerpt=""):
        """保存文章"""
        try:
            # 生成摘要（如果没有提供）
            if not excerpt:
                excerpt = self.generate_excerpt(content)
            
            query = '''
            INSERT INTO articles (title, content, excerpt, category, tags, author, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            '''
            params = (title, content, excerpt, category, ','.join(tags), author, status)
            
            self.db.execute_update(query, params)
            
            # 记录用户活动
            self.log_user_activity(author, f"create_article_{status}", "article", title, 
                                 f"分类:{category}, 字数:{len(content)}")
            
            return True
        except Exception as e:
            st.error(f"保存文章失败: {e}")
            return False
    
    def generate_excerpt(self, content, max_length=200):
        """自动生成文章摘要"""
        # 移除Markdown格式
        clean_content = re.sub(r'[#*`\[\]()]', '', content)
        
        # 取前200个字符
        if len(clean_content) <= max_length:
            return clean_content
        
        # 在句号处截断
        excerpt = clean_content[:max_length]
        last_period = excerpt.rfind('。')
        if last_period > max_length * 0.7:  # 如果句号位置合理
            excerpt = excerpt[:last_period + 1]
        else:
            excerpt = excerpt + "..."
        
        return excerpt
    
    def preview_article(self, title, content, category, tags, excerpt):
        """预览文章"""
        st.markdown("---")
        st.markdown("## 📖 文章预览")
        
        # 文章头部信息
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"# {title}")
            if excerpt:
                st.markdown(f"*{excerpt}*")
        
        with col2:
            st.markdown(f"**分类**: {category}")
            if tags:
                st.markdown("**标签**: " + ", ".join([f"`{tag}`" for tag in tags]))
            st.markdown(f"**作者**: {st.session_state['username']}")
            st.markdown(f"**时间**: {datetime.now().strftime('%Y-%m-%d')}")
        
        st.markdown("---")
        
        # 文章内容（渲染Markdown）
        st.markdown(content)
    
    def show_article_list(self, status=None, author=None):
        """显示文章列表"""
        articles = self.get_articles(status, author)
        
        if articles.empty:
            st.info("暂无文章")
            return
        
        for _, article in articles.iterrows():
            self.render_article_card(article)
    
    def render_article_card(self, article):
        """渲染文章卡片"""
        with st.container():
            # 文章状态标识
            status_colors = {
                "draft": "🟡",
                "review": "🟠", 
                "published": "🟢",
                "archived": "⚫"
            }
            
            status_labels = {
                "draft": "草稿",
                "review": "审核中",
                "published": "已发布", 
                "archived": "已归档"
            }
            
            status_icon = status_colors.get(article['status'], "⚪")
            status_label = status_labels.get(article['status'], article['status'])
            
            # 文章头部
            col1, col2, col3 = st.columns([6, 2, 1])
            
            with col1:
                st.markdown(f"### {article['title']}")
            
            with col2:
                st.markdown(f"**{article['author']}**")
                st.caption(f"{article['category']}")
            
            with col3:
                st.markdown(f"{status_icon} {status_label}")
                st.caption(f"浏览: {article['views']}")
            
            # 文章摘要
            if article['excerpt']:
                st.markdown(article['excerpt'])
            
            # 标签
            if article['tags']:
                tags = article['tags'].split(',')
                tag_html = " ".join([f"<span style='background:#e1f5fe;padding:2px 6px;border-radius:3px;font-size:12px;'>{tag}</span>" for tag in tags])
                st.markdown(tag_html, unsafe_allow_html=True)
            
            # 文章操作
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button(f"📖 阅读", key=f"read_{article['id']}"):
                    self.show_article_detail(article['id'])
            
            with col2:
                if (st.session_state.get("username") == article['author'] or 
                    self.auth.get_user_role(st.session_state.get("username", "")) == "admin"):
                    if st.button(f"✏️ 编辑", key=f"edit_{article['id']}"):
                        self.edit_article(article['id'])
            
            with col3:
                if article['status'] == 'published':
                    if st.button(f"💬 评论({self.get_comment_count(article['id'])})", 
                               key=f"comment_{article['id']}"):
                        st.session_state['show_comments'] = article['id']
            
            with col4:
                created_time = pd.to_datetime(article['created_at'])
                st.caption(f"📅 {created_time.strftime('%Y-%m-%d')}")
            
            st.markdown("---")
    
    def show_article_detail(self, article_id):
        """显示文章详情"""
        query = "SELECT * FROM articles WHERE id = ?"
        result = self.db.execute_query(query, (article_id,))
        
        if result.empty:
            st.error("文章不存在")
            return
        
        article = result.iloc[0]
        
        # 增加浏览量
        self.increment_views(article_id)
        
        # 显示文章
        st.markdown(f"# {article['title']}")
        
        # 文章元信息
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"**作者**: {article['author']}")
        with col2:
            st.markdown(f"**分类**: {article['category']}")
        with col3:
            created_time = pd.to_datetime(article['created_at'])
            st.markdown(f"**发布**: {created_time.strftime('%Y-%m-%d')}")
        
        # 标签
        if article['tags']:
            tags = article['tags'].split(',')
            st.markdown("**标签**: " + " ".join([f"`{tag}`" for tag in tags]))
        
        # 摘要
        if article['excerpt']:
            st.markdown(f"*{article['excerpt']}*")
        
        st.markdown("---")
        
        # 文章内容
        st.markdown(article['content'])
        
        # 文章统计
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("👀 浏览量", article['views'])
        with col2:
            if article['avg_rating'] > 0:
                st.metric("⭐ 平均评分", f"{article['avg_rating']:.1f}")
        with col3:
            st.metric("💬 评论数", self.get_comment_count(article_id))
    
    def get_articles(self, status=None, author=None):
        """获取文章列表"""
        query = "SELECT * FROM articles"
        params = []
        conditions = []
        
        if status:
            conditions.append("status = ?")
            params.append(status)
        
        if author:
            conditions.append("author = ?")
            params.append(author)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY created_at DESC"
        
        return self.db.execute_query(query, params)
    
    def increment_views(self, article_id):
        """增加文章浏览量"""
        query = "UPDATE articles SET views = views + 1 WHERE id = ?"
        self.db.execute_update(query, (article_id,))
    
    def get_comment_count(self, article_id):
        """获取文章评论数"""
        query = '''
        SELECT COUNT(*) as count FROM comments 
        WHERE target_type = 'article' AND target_id = ?
        '''
        result = self.db.execute_query(query, (str(article_id),))
        return result.iloc[0]['count'] if not result.empty else 0
    
    def log_user_activity(self, username, action, target_type, target_id, details):
        """记录用户活动"""
        query = '''
        INSERT INTO user_activity (username, action, target_type, target_id, details)
        VALUES (?, ?, ?, ?, ?)
        '''
        params = (username, action, target_type, target_id, details)
        self.db.execute_update(query, params)
    
    def show_article_management(self):
        """文章管理界面"""
        if not st.session_state.get("authentication_status"):
            return
        
        username = st.session_state["username"]
        user_role = self.auth.get_user_role(username)
        
        st.markdown("## 📚 文章管理")
        
        # 管理选项卡
        if user_role == "admin":
            tab1, tab2, tab3, tab4 = st.tabs(["我的文章", "待审核", "已发布", "统计分析"])
        else:
            tab1, tab2 = st.tabs(["我的文章", "写新文章"])
        
        with tab1:
            st.markdown("### 我的文章")
            self.show_article_list(author=username)
        
        if user_role == "admin":
            with tab2:
                st.markdown("### 待审核文章")
                self.show_article_list(status="review")
            
            with tab3:
                st.markdown("### 已发布文章")
                self.show_article_list(status="published")
            
            with tab4:
                st.markdown("### 统计分析")
                self.show_article_analytics()
        else:
            with tab2:
                self.show_article_editor()
    
    def show_article_analytics(self):
        """显示文章统计分析"""
        # 文章总数统计
        total_query = '''
        SELECT 
            status,
            COUNT(*) as count
        FROM articles
        GROUP BY status
        '''
        status_stats = self.db.execute_query(total_query)
        
        if not status_stats.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            for _, row in status_stats.iterrows():
                status_labels = {
                    "draft": "草稿",
                    "review": "待审核",
                    "published": "已发布",
                    "archived": "已归档"
                }
                
                label = status_labels.get(row['status'], row['status'])
                
                if row['status'] == 'draft':
                    col1.metric(f"📝 {label}", row['count'])
                elif row['status'] == 'review':
                    col2.metric(f"🔍 {label}", row['count'])
                elif row['status'] == 'published':
                    col3.metric(f"✅ {label}", row['count'])
                elif row['status'] == 'archived':
                    col4.metric(f"📦 {label}", row['count'])
        
        # 最受欢迎的文章
        st.markdown("### 📈 最受欢迎的文章")
        popular_query = '''
        SELECT title, author, views, avg_rating
        FROM articles
        WHERE status = 'published'
        ORDER BY views DESC
        LIMIT 10
        '''
        popular_articles = self.db.execute_query(popular_query)
        
        if not popular_articles.empty:
            st.dataframe(popular_articles, use_container_width=True)
        else:
            st.info("暂无数据")
```
### Day 6-7: 页面开发和主应用集成

#### 🤖 AI聊天系统集成

**多AI后端支持架构**:
```python
# modules/ai_chat.py - 统一AI聊天管理器
class AIChat:
    """支持多种AI后端的统一聊天管理器"""
    
    def __init__(self):
        self.backend = os.getenv('AI_BACKEND', 'gemini')  # 支持: gemini, ollama, azure_openai
        self.client = None
        self.initialize_backend()
    
    def initialize_backend(self):
        """根据环境变量初始化对应的AI后端"""
        if self.backend == 'gemini':
            self.client = self._init_gemini()
        elif self.backend == 'ollama':
            self.client = self._init_ollama()
        elif self.backend == 'azure_openai':
            self.client = self._init_azure_openai()
```

**Ollama本地AI集成**:
```python
# chat_ollama.py - Ollama专用聊天接口
class OllamaChat:
    """Ollama本地AI聊天客户端"""
    
    def __init__(self, base_url: str = 'http://localhost:11434', model: str = 'llama2'):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.system_prompt = "你是一位广告学领域的专家，请根据用户的问题，用简体中文回答。"
    
    def check_connection(self) -> bool:
        """检查Ollama服务连接状态"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def generate_response(self, prompt: str, conversation_history: List[Dict] = None) -> str:
        """生成AI回复"""
        # 构建对话上下文并调用Ollama API
        
    def stream_response(self, prompt: str, conversation_history: List[Dict] = None):
        """流式生成回复 - Ollama特有功能"""
        # 实现流式响应，实时显示AI回复过程
```

**环境变量配置**:
```bash
# .env文件配置
AI_BACKEND=ollama  # 可选: gemini, ollama, azure_openai

# Ollama配置
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Gemini配置
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash

# Azure OpenAI配置
AZURE_OPENAI_KEY=your_azure_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_CHATGPT_DEPLOYMENT=gpt-4o
```

#### 🏠 主应用 (streamlit_app.py)
```python
import streamlit as st
import os
from modules.database import DatabaseManager
from modules.auth import AuthManager
from modules.feedback import FeedbackSystem
from modules.comments import CommentSystem
from modules.articles import ArticleManager
from pages import homepage, timeline, figures, campaigns, articles, data_viz
from utils.helpers import apply_custom_css, init_session_state

# 页面配置
st.set_page_config(
    page_title="广告思想简史",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/issues',
        'Report a bug': 'https://github.com/your-repo/issues',
        'About': "广告思想简史 - 探索120年广告发展历程"
    }
)

def main():
    """主应用函数"""
    
    # 初始化会话状态
    init_session_state()
    
    # 应用自定义样式
    apply_custom_css()
    
    # 初始化核心服务
    try:
        db_manager = DatabaseManager()
        auth_manager = AuthManager()
        feedback_system = FeedbackSystem(db_manager)
        comment_system = CommentSystem(db_manager)
        article_manager = ArticleManager(db_manager, auth_manager)
        
        # 存储到session state供其他模块使用
        st.session_state['db_manager'] = db_manager
        st.session_state['auth_manager'] = auth_manager
        st.session_state['feedback_system'] = feedback_system
        st.session_state['comment_system'] = comment_system
        st.session_state['article_manager'] = article_manager
        
    except Exception as e:
        st.error(f"系统初始化失败: {e}")
        st.stop()
    
    # 用户认证
    name, authentication_status, username = auth_manager.login()
    
    if authentication_status == False:
        st.error('❌ 用户名或密码错误')
        show_registration_option(auth_manager)
        
    elif authentication_status == None:
        st.warning('👋 请输入用户名和密码登录')
        show_registration_option(auth_manager)
        show_demo_info()
        
    elif authentication_status:
        # 用户已登录，显示主应用
        show_main_app(name, username, auth_manager, feedback_system, 
                     comment_system, article_manager)

def show_registration_option(auth_manager):
    """显示注册选项"""
    with st.expander("🆕 新用户注册"):
        st.markdown("""
        ### 注册说明
        - **学生用户**: 可以浏览内容、评论和反馈
        - **教授用户**: 可以发布文章、管理内容
        - **管理员**: 拥有全部权限
        """)
        
        if auth_manager.register_user():
            st.experimental_rerun()

def show_demo_info():
    """显示演示信息"""
    st.info("""
    ### 🎯 演示账户
    
    **管理员账户**:
    - 用户名: `admin`
    - 密码: `admin123`
    
    **教授账户**:
    - 用户名: `professor_lu`
    - 密码: `professor123`
    
    **学生账户**:
    - 用户名: `student_demo`
    - 密码: `student123`
    """)

def show_main_app(name, username, auth_manager, feedback_system, 
                  comment_system, article_manager):
    """显示主应用界面"""
    
    # 用户信息侧边栏
    auth_manager.logout()
    
    with st.sidebar:
        st.write(f'👋 欢迎, **{name}**!')
        
        user_role = auth_manager.get_user_role(username)
        role_labels = {
            'admin': '🛡️ 管理员',
            'professor': '👨‍🏫 教授',
            'student': '🎓 学生'
        }
        st.caption(f"身份: {role_labels.get(user_role, user_role)}")
        
        # 用户统计
        show_user_stats(username)
    
    # 主导航 - 添加AI助手选项
    page = st.sidebar.selectbox("📍 导航", [
        "🏠 首页",
        "📅 广告年表", 
        "👥 广告人物",
        "🎯 经典广告",
        "📝 专家文章",
        "📊 行业数据",
        "🤖 AI助手",  # 新增AI助手页面
        "⚙️ 个人中心"
    ])
    
    # 页面路由
    route_page(page, feedback_system, comment_system, article_manager, username)

def show_user_stats(username):
    """显示用户统计信息"""
    try:
        db_manager = st.session_state['db_manager']
        
        # 用户活动统计
        activity_query = '''
        SELECT 
            COUNT(*) as total_activities,
            COUNT(DISTINCT DATE(timestamp)) as active_days
        FROM user_activity
        WHERE username = ?
        '''
        stats = db_manager.execute_query(activity_query, (username,))
        
        if not stats.empty:
            st.metric("📊 活动次数", int(stats.iloc[0]['total_activities']))
            st.metric("📅 活跃天数", int(stats.iloc[0]['active_days']))
        
        # 用户贡献统计
        contrib_query = '''
        SELECT 
            (SELECT COUNT(*) FROM comments WHERE username = ?) as comments,
            (SELECT COUNT(*) FROM user_feedback WHERE username = ?) as feedbacks,
            (SELECT COUNT(*) FROM articles WHERE author = ?) as articles
        '''
        contrib = db_manager.execute_query(contrib_query, (username, username, username))
        
        if not contrib.empty:
            row = contrib.iloc[0]
            if row['comments'] > 0:
                st.metric("💬 评论数", int(row['comments']))
            if row['feedbacks'] > 0:
                st.metric("👍 反馈数", int(row['feedbacks']))
            if row['articles'] > 0:
                st.metric("📝 文章数", int(row['articles']))
                
    except Exception as e:
        st.sidebar.error(f"统计加载失败: {e}")

def route_page(page, feedback_system, comment_system, article_manager, username):
    """页面路由"""
    
    if page == "🏠 首页":
        homepage.show()
        
    elif page == "📅 广告年表":
        timeline.show()
        st.markdown("---")
        feedback_system.collect_feedback("timeline", "main", "thumbs", 
                                       "您觉得这个广告年表怎么样？")
        comment_system.display_comments_section("timeline", "main")
        
    elif page == "👥 广告人物":
        figures.show()
        st.markdown("---")
        feedback_system.collect_feedback("figures", "main", "stars",
                                       "请为广告人物内容评分")
        comment_system.display_comments_section("figures", "main")
        
    elif page == "🎯 经典广告":
        campaigns.show()
        st.markdown("---")
        feedback_system.collect_feedback("campaigns", "main", "faces",
                                       "这些经典广告给您的感受如何？")
        comment_system.display_comments_section("campaigns", "main")
        
    elif page == "📝 专家文章":
        articles.show(article_manager)
    
    elif page == "🤖 AI助手":
        # 集成统一AI聊天系统
        from modules.ai_chat import chat_interface
        chat_interface()
        
    elif page == "📊 行业数据":
        data_viz.show()
        st.markdown("---")
        feedback_system.collect_feedback("data", "main", "thumbs",
                                       "这些数据分析对您有帮助吗？")
        comment_system.display_comments_section("data", "main")
        
    elif page == "⚙️ 个人中心":
        show_user_center(username, article_manager)

def show_user_center(username, article_manager):
    """显示个人中心"""
    st.markdown("# ⚙️ 个人中心")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 我的统计", "📝 我的文章", "💬 我的评论", "👍 我的反馈"])
    
    with tab1:
        show_personal_stats(username)
    
    with tab2:
        st.markdown("### 我的文章")
        article_manager.show_article_list(author=username)
        
        if st.button("✍️ 写新文章"):
            article_manager.show_article_editor()
    
    with tab3:
        show_my_comments(username)
    
    with tab4:
        show_my_feedback(username)

def show_personal_stats(username):
    """显示个人统计"""
    db_manager = st.session_state['db_manager']
    
    # 活动时间线
    st.markdown("### 📈 活动时间线")
    
    timeline_query = '''
    SELECT 
        DATE(timestamp) as date,
        COUNT(*) as activities
    FROM user_activity
    WHERE username = ?
    GROUP BY DATE(timestamp)
    ORDER BY date DESC
    LIMIT 30
    '''
    
    timeline_data = db_manager.execute_query(timeline_query, (username,))
    
    if not timeline_data.empty:
        st.line_chart(timeline_data.set_index('date'))
    else:
        st.info("暂无活动数据")

def show_my_comments(username):
    """显示我的评论"""
    db_manager = st.session_state['db_manager']
    
    comments_query = '''
    SELECT 
        content,
        target_type,
        target_id,
        timestamp,
        likes
    FROM comments
    WHERE username = ?
    ORDER BY timestamp DESC
    '''
    
    my_comments = db_manager.execute_query(comments_query, (username,))
    
    if not my_comments.empty:
        for _, comment in my_comments.iterrows():
            with st.expander(f"💬 {comment['target_type']} - {comment['timestamp'][:10]}"):
                st.markdown(comment['content'])
                st.caption(f"👍 {comment['likes']} 个赞")
    else:
        st.info("您还没有发表过评论")

def show_my_feedback(username):
    """显示我的反馈"""
    db_manager = st.session_state['db_manager']
    
    feedback_query = '''
    SELECT 
        target_type,
        target_id,
        feedback_type,
        feedback_value,
        feedback_text,
        timestamp
    FROM user_feedback
    WHERE username = ?
    ORDER BY timestamp DESC
    '''
    
    my_feedback = db_manager.execute_query(feedback_query, (username,))
    
    if not my_feedback.empty:
        for _, feedback in my_feedback.iterrows():
            with st.expander(f"👍 {feedback['target_type']} - {feedback['timestamp'][:10]}"):
                
                # 显示反馈值
                if feedback['feedback_type'] == 'thumbs':
                    icon = "👍" if feedback['feedback_value'] == 1 else "👎"
                elif feedback['feedback_type'] == 'stars':
                    icon = "⭐" * (feedback['feedback_value'] + 1)
                else:
                    icon = ["😞", "😐", "🙂", "😊", "😍"][feedback['feedback_value']]
                
                st.markdown(f"**评价**: {icon}")
                
                if feedback['feedback_text']:
                    st.markdown(f"**评论**: {feedback['feedback_text']}")
    else:
        st.info("您还没有提供过反馈")

if __name__ == "__main__":
    main()
```

#### 🎨 样式和工具函数 (utils/helpers.py)
```python
import streamlit as st

def apply_custom_css():
    """应用自定义CSS样式"""
    st.markdown("""
    <style>
    /* 全局样式 */
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
    
    /* 标题样式 */
    h1 {
        color: #d32f2f;
        font-weight: 500;
        border-bottom: 3px solid #d32f2f;
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
    }
    
    h2 {
        color: #1976d2;
        font-weight: 500;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        color: #388e3c;
        font-weight: 500;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
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
    
    /* 按钮样式 */
    .stButton > button {
        background: linear-gradient(45deg, #d32f2f, #f44336);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(211, 47, 47, 0.3);
        border: 2px solid #d32f2f;
    }
    
    /* 侧边栏样式 */
    .css-1d391kg {
        background: linear-gradient(180deg, #d32f2f, #c62828);
    }
    
    .css-1d391kg .css-1v0mbdj {
        color: white;
    }
    
    /* 表单样式 */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #d32f2f;
        box-shadow: 0 0 0 2px rgba(211, 47, 47, 0.2);
    }
    
    /* 反馈组件样式 */
    .streamlit-feedback {
        margin: 1rem 0;
        padding: 1.5rem;
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #1976d2;
    }
    
    /* 评论区样式 */
    .comment-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #1976d2;
    }
    
    /* 统计卡片样式 */
    .metric-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-top: 4px solid #4caf50;
    }
    
    /* 文章卡片样式 */
    .article-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #ff9800;
        transition: transform 0.2s ease;
    }
    
    .article-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }
        
        .stContainer > div {
            padding: 1rem;
        }
        
        h1 {
            font-size: 1.8rem;
        }
        
        h2 {
            font-size: 1.5rem;
        }
        
        h3 {
            font-size: 1.3rem;
        }
        
        .stButton > button {
            padding: 0.4rem 1rem;
            font-size: 0.9rem;
        }
    }
    
    /* 加载动画 */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stContainer {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* 成功/错误消息样式 */
    .stSuccess {
        background: linear-gradient(45deg, #4caf50, #66bb6a);
        color: white;
        border-radius: 8px;
        padding: 1rem;
        border: none;
    }
    
    .stError {
        background: linear-gradient(45deg, #f44336, #ef5350);
        color: white;
        border-radius: 8px;
        padding: 1rem;
        border: none;
    }
    
    .stWarning {
        background: linear-gradient(45deg, #ff9800, #ffb74d);
        color: white;
        border-radius: 8px;
        padding: 1rem;
        border: none;
    }
    
    .stInfo {
        background: linear-gradient(45deg, #2196f3, #42a5f5);
        color: white;
        border-radius: 8px;
        padding: 1rem;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

def init_session_state():
    """初始化会话状态"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.page_views = {}
        st.session_state.user_preferences = {}

def get_page_view_count(page_name):
    """获取页面浏览次数"""
    if page_name not in st.session_state.page_views:
        st.session_state.page_views[page_name] = 0
    
    st.session_state.page_views[page_name] += 1
    return st.session_state.page_views[page_name]

def format_number(num):
    """格式化数字显示"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    else:
        return str(num)

def truncate_text(text, max_length=100):
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def get_time_ago(timestamp):
    """获取相对时间"""
    from datetime import datetime, timedelta
    import pandas as pd
    
    now = datetime.now()
    time_diff = now - pd.to_datetime(timestamp)
    
    if time_diff.days > 0:
        return f"{time_diff.days}天前"
    elif time_diff.seconds > 3600:
        hours = time_diff.seconds // 3600
        return f"{hours}小时前"
    elif time_diff.seconds > 60:
        minutes = time_diff.seconds // 60
        return f"{minutes}分钟前"
    else:
        return "刚刚"
```
---

## 📅 第二周：页面开发和功能完善

### Day 8-9: 页面模块开发

#### 🏠 首页 (pages/homepage.py)
```python
import streamlit as st
from PIL import Image
import pandas as pd
from utils.helpers import get_page_view_count

def show():
    """显示首页"""
    get_page_view_count("homepage")
    
    # 页面标题
    st.markdown("# 🏠 欢迎来到广告思想简史")
    
    # 英雄区域
    show_hero_section()
    
    # 特色内容
    show_features()
    
    # 统计数据
    show_statistics()
    
    # 最新文章
    show_recent_articles()

def show_hero_section():
    """显示英雄区域"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## 📖 探索120年广告发展历程
        
        本书是广告思想史的开创之作，将广告史从"WHAT"(是什么）为主的记事模式转向"WHY+HOW"(为何和如何）为主的探究模式；从关注事件转向以人物和思想为核心；从只讲"过去"延伸至"现在及未来"。
        
        ### 🎯 主要特色
        - 📚 **权威内容**: 基于卢泰宏教授的专业著作
        - 🌍 **国际视野**: 涵盖全球广告发展历程  
        - 💡 **思想深度**: 深入分析广告背后的思想变迁
        - 🎨 **案例丰富**: 包含大量经典广告案例
        - 🤖 **AI互动**: 智能问答系统，随时解答疑问
        """)
        
        # 快速导航按钮
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if st.button("📅 浏览年表", use_container_width=True):
                st.session_state['navigate_to'] = "timeline"
                st.experimental_rerun()
        
        with col_btn2:
            if st.button("👥 广告人物", use_container_width=True):
                st.session_state['navigate_to'] = "figures"
                st.experimental_rerun()
        
        with col_btn3:
            if st.button("🎯 经典广告", use_container_width=True):
                st.session_state['navigate_to'] = "campaigns"
                st.experimental_rerun()
    
    with col2:
        try:
            img = Image.open("statics/cover.jpeg")
            st.image(img, caption="广告思想简史", use_column_width=True)
        except:
            st.info("📚 书籍封面图片")
        
        # 作者信息
        st.markdown("""
        ### 👨‍🏫 关于作者
        
        **卢泰宏教授**
        - 中山大学二级教授
        - 中国营销研究中心(CMC)创始人
        - 菲利浦·科特勒国际营销理论贡献奖获得者
        - "中国广告20年20人"(2001)
        - "影响中国营销进程的25位风云人物"(2004)
        """)

def show_features():
    """显示特色功能"""
    st.markdown("## 🌟 平台特色")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        ### 📚 丰富内容
        - 120年广告历史
        - 100位广告巨星
        - 经典广告案例
        - 专业理论分析
        """)
    
    with col2:
        st.markdown("""
        ### 🤝 互动体验
        - 专家文章评论
        - 内容评分反馈
        - 用户讨论社区
        - 个性化推荐
        """)
    
    with col3:
        st.markdown("""
        ### 👨‍🏫 专家贡献
        - 100+位教授参与
        - 原创学术文章
        - 前沿观点分享
        - 行业深度分析
        """)
    
    with col4:
        st.markdown("""
        ### 📊 数据洞察
        - 行业发展趋势
        - 广告支出分析
        - 市场变化追踪
        - 可视化图表
        """)

def show_statistics():
    """显示统计数据"""
    st.markdown("## 📊 平台数据")
    
    # 模拟统计数据（实际应用中从数据库获取）
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📅 历史跨度", 
            value="120+年", 
            delta="1450-2020",
            help="从古腾堡印刷术到数字广告时代"
        )
    
    with col2:
        st.metric(
            label="👥 广告人物", 
            value="100+位", 
            delta="行业巨星",
            help="20世纪最具影响力的广告人物"
        )
    
    with col3:
        st.metric(
            label="🎯 经典广告", 
            value="100+个", 
            delta="成功案例",
            help="20世纪最成功的广告活动"
        )
    
    with col4:
        st.metric(
            label="📝 专家文章", 
            value="50+篇", 
            delta="持续更新",
            help="来自全球广告学专家的原创文章"
        )

def show_recent_articles():
    """显示最新文章"""
    st.markdown("## 📰 最新文章")
    
    try:
        # 从数据库获取最新文章
        db_manager = st.session_state.get('db_manager')
        if db_manager:
            query = '''
            SELECT title, author, excerpt, created_at, views, avg_rating
            FROM articles 
            WHERE status = 'published'
            ORDER BY created_at DESC 
            LIMIT 6
            '''
            recent_articles = db_manager.execute_query(query)
            
            if not recent_articles.empty:
                # 显示文章卡片
                cols = st.columns(2)
                
                for idx, (_, article) in enumerate(recent_articles.iterrows()):
                    with cols[idx % 2]:
                        with st.container():
                            st.markdown(f"### {article['title']}")
                            st.markdown(f"**作者**: {article['author']}")
                            
                            if article['excerpt']:
                                st.markdown(article['excerpt'][:150] + "...")
                            
                            col_info1, col_info2, col_info3 = st.columns(3)
                            
                            with col_info1:
                                created_date = pd.to_datetime(article['created_at']).strftime('%m-%d')
                                st.caption(f"📅 {created_date}")
                            
                            with col_info2:
                                st.caption(f"👀 {article['views']}")
                            
                            with col_info3:
                                if article['avg_rating'] > 0:
                                    st.caption(f"⭐ {article['avg_rating']:.1f}")
                            
                            if st.button(f"阅读全文", key=f"read_article_{idx}"):
                                st.session_state['selected_article'] = article['title']
                                st.experimental_rerun()
                        
                        st.markdown("---")
            else:
                show_placeholder_articles()
        else:
            show_placeholder_articles()
            
    except Exception as e:
        st.error(f"加载文章失败: {e}")
        show_placeholder_articles()

def show_placeholder_articles():
    """显示占位文章"""
    placeholder_articles = [
        {
            "title": "数字广告的未来趋势",
            "author": "卢泰宏教授",
            "excerpt": "探讨人工智能、大数据和区块链技术如何重塑广告行业的未来发展方向...",
            "date": "2024-01-15"
        },
        {
            "title": "经典广告案例分析：可口可乐的品牌建设",
            "author": "张教授",
            "excerpt": "深入分析可口可乐百年品牌建设历程，探讨其成功的营销策略和品牌理念...",
            "date": "2024-01-10"
        },
        {
            "title": "中国广告发展的三个阶段",
            "author": "李教授",
            "excerpt": "回顾中国广告业从改革开放至今的发展历程，分析不同阶段的特点和挑战...",
            "date": "2024-01-05"
        }
    ]
    
    cols = st.columns(2)
    
    for idx, article in enumerate(placeholder_articles):
        with cols[idx % 2]:
            with st.container():
                st.markdown(f"### {article['title']}")
                st.markdown(f"**作者**: {article['author']}")
                st.markdown(article['excerpt'])
                st.caption(f"📅 {article['date']}")
                
                if st.button(f"阅读全文", key=f"placeholder_article_{idx}"):
                    st.info("这是演示文章，完整版本将在正式版本中提供")
            
            st.markdown("---")

# 添加页面底部信息
def show_footer():
    """显示页面底部"""
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 📞 联系我们
        - 📧 Email: contact@adideas.com
        - 🌐 Website: www.adideas.com
        - 📱 微信: AdIdeasPlatform
        """)
    
    with col2:
        st.markdown("""
        ### 🔗 友情链接
        - [中山大学](http://www.sysu.edu.cn/)
        - [中国营销研究中心](http://cmc.sysu.edu.cn/)
        - [广告学术期刊](http://www.example.com/)
        """)
    
    with col3:
        st.markdown("""
        ### ℹ️ 关于平台
        - 版本: v1.0.0
        - 更新: 2024-01-15
        - 许可: MIT License
        """)
    
    st.markdown("""
    <div style='text-align: center; color: #666; margin-top: 2rem;'>
        <p>© 2024 广告思想简史平台. All rights reserved.</p>
        <p>Powered by Streamlit | Made with ❤️ for advertising education</p>
    </div>
    """, unsafe_allow_html=True)
```

#### 📅 广告年表页面 (pages/timeline.py)
```python
import streamlit as st
import pandas as pd
from utils.helpers import get_page_view_count

def show():
    """显示广告年表页面"""
    get_page_view_count("timeline")
    
    st.markdown("# 📅 广告大事年表")
    st.markdown("探索从1450年至今的广告发展重要节点")
    
    # 时间段选择
    show_timeline_filter()
    
    # 显示年表内容
    show_timeline_content()

def show_timeline_filter():
    """显示时间段筛选"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        period = st.selectbox("选择时期", [
            "全部时期",
            "15-18世纪 (印刷时代)",
            "19世纪 (现代广告萌芽)",
            "20世纪上半叶 (广告专业化)",
            "20世纪下半叶 (创意革命)",
            "21世纪 (数字化时代)"
        ])
    
    with col2:
        region = st.selectbox("地区筛选", [
            "全球",
            "欧洲",
            "北美",
            "亚洲",
            "中国"
        ])
    
    with col3:
        category = st.selectbox("事件类型", [
            "全部类型",
            "技术创新",
            "理论发展",
            "公司成立",
            "经典案例",
            "法规政策"
        ])
    
    # 根据筛选条件更新内容
    st.session_state['timeline_filter'] = {
        'period': period,
        'region': region,
        'category': category
    }

def show_timeline_content():
    """显示年表内容"""
    
    # 获取年表数据
    timeline_data = get_timeline_data()
    
    # 应用筛选
    filtered_data = apply_timeline_filter(timeline_data)
    
    # 显示统计信息
    st.info(f"📊 共找到 {len(filtered_data)} 个历史事件")
    
    # 按时间倒序显示
    for event in filtered_data:
        show_timeline_event(event)

def get_timeline_data():
    """获取年表数据"""
    # 这里应该从数据库或文件加载数据
    # 为演示目的，使用硬编码数据
    
    timeline_events = [
        {
            "year": "1450",
            "title": "古腾堡发明活字印刷术",
            "description": "约翰内斯·古腾堡发明了活字印刷术，为现代广告的诞生奠定了技术基础。",
            "category": "技术创新",
            "region": "欧洲",
            "period": "15-18世纪",
            "significance": "high",
            "image_url": None
        },
        {
            "year": "960-1127",
            "title": "中国最早的印刷广告",
            "description": "中国济南"刘家功夫针铺"的广告铜板，被认为是世界上最早的印刷广告之一。",
            "category": "经典案例",
            "region": "中国",
            "period": "15-18世纪",
            "significance": "high",
            "image_url": None
        },
        {
            "year": "1472",
            "title": "世界第一份印刷广告",
            "description": "德国印刷工匠克雷门茨·门德尔斯发行了一份宣传圣诞节的印刷广告，标志着广告可以大规模传播。",
            "category": "经典案例",
            "region": "欧洲",
            "period": "15-18世纪",
            "significance": "high",
            "image_url": None
        },
        {
            "year": "1704",
            "title": "第一份报纸广告",
            "description": "波士顿的《波士顿新闻信使》发布了美国历史上的第一则报纸广告。",
            "category": "经典案例",
            "region": "北美",
            "period": "15-18世纪",
            "significance": "high",
            "image_url": None
        },
        {
            "year": "1840",
            "title": "第一间广告代理公司",
            "description": "帕尔默(V.B. Palmer)在美国成立第一间广告代理公司，标志着广告行业的专业化开始。",
            "category": "公司成立",
            "region": "北美",
            "period": "19世纪",
            "significance": "high",
            "image_url": None
        },
        {
            "year": "1869",
            "title": "艾耶广告公司成立",
            "description": "在美国费城创立的艾耶（父子）广告公司实现了广告代理的现代转型：从为媒体服务转向为广告主服务。",
            "category": "公司成立",
            "region": "北美",
            "period": "19世纪",
            "significance": "high",
            "image_url": None
        },
        {
            "year": "1959",
            "title": "大众甲壳虫"Think Small"广告",
            "description": "DDB为大众甲壳虫汽车创作的"Think Small"广告，被《广告时代》评为20世纪最成功的广告。",
            "category": "经典案例",
            "region": "北美",
            "period": "20世纪下半叶",
            "significance": "high",
            "image_url": None
        },
        {
            "year": "1984",
            "title": "苹果"1984"超级碗广告",
            "description": "苹果公司在超级碗期间播出的"1984"广告，开创了事件营销的先河。",
            "category": "经典案例",
            "region": "北美",
            "period": "20世纪下半叶",
            "significance": "high",
            "image_url": None
        },
        {
            "year": "2000",
            "title": "Google AdWords推出",
            "description": "Google推出AdWords广告平台，开启了搜索引擎营销的新时代。",
            "category": "技术创新",
            "region": "北美",
            "period": "21世纪",
            "significance": "high",
            "image_url": None
        },
        {
            "year": "2004",
            "title": "Facebook成立",
            "description": "Facebook的成立标志着社交媒体广告时代的开始。",
            "category": "技术创新",
            "region": "北美",
            "period": "21世纪",
            "significance": "high",
            "image_url": None
        }
    ]
    
    return timeline_events

def apply_timeline_filter(timeline_data):
    """应用时间线筛选"""
    filter_settings = st.session_state.get('timeline_filter', {})
    
    filtered_data = timeline_data.copy()
    
    # 时期筛选
    if filter_settings.get('period') and filter_settings['period'] != "全部时期":
        period_key = filter_settings['period'].split(' ')[0]
        filtered_data = [event for event in filtered_data if period_key in event['period']]
    
    # 地区筛选
    if filter_settings.get('region') and filter_settings['region'] != "全球":
        filtered_data = [event for event in filtered_data if event['region'] == filter_settings['region']]
    
    # 类型筛选
    if filter_settings.get('category') and filter_settings['category'] != "全部类型":
        filtered_data = [event for event in filtered_data if event['category'] == filter_settings['category']]
    
    # 按年份排序
    filtered_data.sort(key=lambda x: int(x['year'].split('-')[0]) if '-' in x['year'] else int(x['year']), reverse=True)
    
    return filtered_data

def show_timeline_event(event):
    """显示单个时间线事件"""
    
    # 重要性颜色
    significance_colors = {
        "high": "#d32f2f",
        "medium": "#ff9800", 
        "low": "#4caf50"
    }
    
    color = significance_colors.get(event['significance'], "#757575")
    
    with st.container():
        # 事件卡片
        st.markdown(f"""
        <div style="
            border-left: 4px solid {color};
            padding: 1rem;
            margin: 1rem 0;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 6, 1])
        
        with col1:
            # 年份显示
            st.markdown(f"""
            <div style="
                background: {color};
                color: white;
                padding: 0.5rem;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                font-size: 1.1rem;
            ">
                {event['year']}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # 事件内容
            st.markdown(f"### {event['title']}")
            st.markdown(event['description'])
            
            # 标签
            col_tag1, col_tag2, col_tag3 = st.columns(3)
            
            with col_tag1:
                st.caption(f"🏷️ {event['category']}")
            with col_tag2:
                st.caption(f"🌍 {event['region']}")
            with col_tag3:
                st.caption(f"📅 {event['period']}")
        
        with col3:
            # 操作按钮
            if st.button("📖 详情", key=f"detail_{event['year']}_{event['title'][:10]}"):
                show_event_detail(event)
        
        st.markdown("</div>", unsafe_allow_html=True)

def show_event_detail(event):
    """显示事件详情"""
    with st.expander(f"📖 {event['title']} - 详细信息", expanded=True):
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"**年份**: {event['year']}")
            st.markdown(f"**标题**: {event['title']}")
            st.markdown(f"**描述**: {event['description']}")
            
            # 扩展信息（实际应用中从数据库获取）
            st.markdown("""
            **历史背景**:
            这一事件发生在特定的历史背景下，对广告行业的发展产生了深远影响。
            
            **影响分析**:
            - 技术层面：推动了广告制作和传播技术的进步
            - 商业层面：改变了广告的商业模式和运营方式
            - 社会层面：影响了公众对广告的认知和接受度
            
            **相关人物**:
            - 关键人物及其贡献
            - 相关企业和机构
            """)
        
        with col2:
            # 事件属性
            st.markdown("**事件属性**")
            st.markdown(f"- **类型**: {event['category']}")
            st.markdown(f"- **地区**: {event['region']}")
            st.markdown(f"- **时期**: {event['period']}")
            st.markdown(f"- **重要性**: {event['significance']}")
            
            # 相关链接
            st.markdown("**相关资源**")
            st.markdown("- [维基百科](https://wikipedia.org)")
            st.markdown("- [学术论文](https://scholar.google.com)")
            st.markdown("- [历史档案](https://archive.org)")
```
### Day 10-11: 测试和优化

#### 🧪 测试计划

**单元测试**:
```python
# tests/test_database.py
import pytest
import tempfile
import os
from modules.database import DatabaseManager

def test_database_initialization():
    """测试数据库初始化"""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        db_path = tmp.name
    
    try:
        db = DatabaseManager(db_path)
        
        # 检查表是否创建
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['user_feedback', 'comments', 'articles', 'content_stats', 'user_activity']
        
        for table in expected_tables:
            assert table in tables
        
        conn.close()
    
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)

def test_feedback_system():
    """测试反馈系统"""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        db_path = tmp.name
    
    try:
        db = DatabaseManager(db_path)
        
        # 测试保存反馈
        query = '''
        INSERT INTO user_feedback 
        (username, target_type, target_id, feedback_type, feedback_value, feedback_text)
        VALUES (?, ?, ?, ?, ?, ?)
        '''
        params = ('test_user', 'article', '1', 'thumbs', 1, 'Great article!')
        
        db.execute_update(query, params)
        
        # 验证数据
        result = db.execute_query('SELECT * FROM user_feedback WHERE username = ?', ('test_user',))
        
        assert len(result) == 1
        assert result.iloc[0]['feedback_value'] == 1
        assert result.iloc[0]['feedback_text'] == 'Great article!'
    
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)
```

**集成测试**:
```python
# tests/test_integration.py
import streamlit as st
from streamlit.testing.v1 import AppTest

def test_app_startup():
    """测试应用启动"""
    at = AppTest.from_file("streamlit_app.py")
    at.run()
    
    # 检查页面是否正常加载
    assert not at.exception
    assert "广告思想简史" in at.title[0].value

def test_authentication_flow():
    """测试认证流程"""
    at = AppTest.from_file("streamlit_app.py")
    at.run()
    
    # 测试登录表单
    at.text_input("username").input("admin")
    at.text_input("password").input("admin123")
    at.button("Login").click()
    at.run()
    
    # 验证登录成功
    assert "欢迎" in str(at.sidebar)
```

#### 🔧 性能优化

**数据库优化**:
```sql
-- 创建索引提高查询性能
CREATE INDEX idx_user_feedback_target ON user_feedback(target_type, target_id);
CREATE INDEX idx_comments_target ON comments(target_type, target_id);
CREATE INDEX idx_articles_status ON articles(status);
CREATE INDEX idx_articles_author ON articles(author);
CREATE INDEX idx_user_activity_username ON user_activity(username);
CREATE INDEX idx_user_activity_timestamp ON user_activity(timestamp);
```

**缓存优化**:
```python
# utils/cache.py
import streamlit as st
import hashlib
import pickle
from datetime import datetime, timedelta

@st.cache_data(ttl=3600)  # 缓存1小时
def get_cached_articles(status=None):
    """缓存文章列表"""
    db_manager = st.session_state.get('db_manager')
    if not db_manager:
        return []
    
    query = "SELECT * FROM articles"
    if status:
        query += f" WHERE status = '{status}'"
    query += " ORDER BY created_at DESC"
    
    return db_manager.execute_query(query)

@st.cache_data(ttl=1800)  # 缓存30分钟
def get_cached_stats(target_type, target_id):
    """缓存统计数据"""
    db_manager = st.session_state.get('db_manager')
    if not db_manager:
        return None
    
    query = '''
    SELECT thumbs_up, thumbs_down, avg_stars, total_ratings 
    FROM content_stats
    WHERE target_type = ? AND target_id = ?
    '''
    result = db_manager.execute_query(query, (target_type, target_id))
    
    return result.iloc[0] if not result.empty else None

def clear_cache():
    """清除所有缓存"""
    st.cache_data.clear()
    st.success("缓存已清除")
```

---

## 📅 第三周：部署和上线

### Day 12-13: 阿里云部署准备

#### ☁️ 阿里云ECS配置

**服务器规格选择**:
- **实例类型**: ecs.t6-c1m2.large (2核4GB)
- **操作系统**: Ubuntu 20.04 LTS
- **存储**: 40GB SSD云盘
- **网络**: 专有网络VPC
- **安全组**: 开放22(SSH), 80(HTTP), 443(HTTPS), 8501(Streamlit)端口

**服务器初始化脚本**:
```bash
#!/bin/bash
# server_setup.sh

# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python和必要工具
sudo apt install -y python3 python3-pip python3-venv nginx git

# 安装Docker (可选)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 创建应用目录
sudo mkdir -p /opt/ad-ideas
sudo chown $USER:$USER /opt/ad-ideas

# 配置防火墙
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw allow 8501
sudo ufw --force enable

# 安装SSL证书工具
sudo apt install -y certbot python3-certbot-nginx

echo "服务器初始化完成"
```

#### 🐳 Docker部署配置

**Dockerfile**:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p data

# 暴露端口
EXPOSE 8501

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# 启动命令
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  ad-ideas-app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./config.yaml:/app/config.yaml
      - ./statics:/app/statics
    environment:
      - STREAMLIT_SERVER_HEADLESS=true
      - STREAMLIT_SERVER_ENABLE_CORS=false
      - STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - ad-ideas-app
    restart: unless-stopped

volumes:
  app_data:
```

#### 🌐 Nginx配置

**nginx.conf**:
```nginx
events {
    worker_connections 1024;
}

http {
    upstream streamlit {
        server ad-ideas-app:8501;
    }

    server {
        listen 80;
        server_name your-domain.com www.your-domain.com;
        
        # 重定向到HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com www.your-domain.com;

        # SSL配置
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # 安全头
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

        # Gzip压缩
        gzip on;
        gzip_vary on;
        gzip_min_length 1024;
        gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

        location / {
            proxy_pass http://streamlit;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_buffering off;
        }

        # 静态文件缓存
        location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

### Day 14: 部署和测试

#### 🚀 部署脚本

**deploy.sh**:
```bash
#!/bin/bash
# deploy.sh - 自动化部署脚本

set -e

echo "🚀 开始部署广告思想简史平台..."

# 配置变量
APP_DIR="/opt/ad-ideas"
REPO_URL="https://github.com/your-username/ad-ideas-platform.git"
DOMAIN="your-domain.com"

# 检查是否为root用户
if [[ $EUID -eq 0 ]]; then
   echo "请不要使用root用户运行此脚本"
   exit 1
fi

# 1. 克隆或更新代码
echo "📥 更新代码..."
if [ -d "$APP_DIR" ]; then
    cd $APP_DIR
    git pull origin main
else
    git clone $REPO_URL $APP_DIR
    cd $APP_DIR
fi

# 2. 创建Python虚拟环境
echo "🐍 设置Python环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 3. 初始化数据库
echo "🗄️ 初始化数据库..."
python3 -c "
from modules.database import DatabaseManager
db = DatabaseManager()
print('数据库初始化完成')
"

# 4. 创建配置文件
echo "⚙️ 创建配置文件..."
if [ ! -f "config.yaml" ]; then
    cp config.yaml.example config.yaml
    echo "请编辑 config.yaml 文件配置用户信息"
fi

# 5. 设置环境变量
echo "🔐 设置环境变量..."
if [ ! -f ".env" ]; then
    cat > .env << EOF
# 生产环境配置
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_ENABLE_CORS=false
STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
EOF
fi

# 6. 启动服务
echo "🔄 启动服务..."
if command -v docker-compose &> /dev/null; then
    docker-compose down
    docker-compose up -d --build
else
    # 使用systemd服务
    sudo cp ad-ideas.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable ad-ideas
    sudo systemctl restart ad-ideas
fi

# 7. 配置SSL证书
echo "🔒 配置SSL证书..."
if [ ! -f "/etc/nginx/ssl/cert.pem" ]; then
    sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN
fi

# 8. 重启Nginx
echo "🌐 重启Nginx..."
sudo systemctl restart nginx

# 9. 健康检查
echo "🏥 健康检查..."
sleep 10

if curl -f http://localhost:8501/_stcore/health > /dev/null 2>&1; then
    echo "✅ 应用健康检查通过"
else
    echo "❌ 应用健康检查失败"
    exit 1
fi

if curl -f https://$DOMAIN > /dev/null 2>&1; then
    echo "✅ HTTPS访问正常"
else
    echo "❌ HTTPS访问失败"
fi

echo "🎉 部署完成！"
echo "📱 访问地址: https://$DOMAIN"
echo "📊 监控地址: https://$DOMAIN/health"
```

**systemd服务文件 (ad-ideas.service)**:
```ini
[Unit]
Description=Ad Ideas Platform
After=network.target

[Service]
Type=exec
User=ubuntu
WorkingDirectory=/opt/ad-ideas
Environment=PATH=/opt/ad-ideas/venv/bin
ExecStart=/opt/ad-ideas/venv/bin/streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 📊 监控和日志

**监控脚本 (monitor.sh)**:
```bash
#!/bin/bash
# monitor.sh - 系统监控脚本

LOG_FILE="/var/log/ad-ideas-monitor.log"

# 检查应用状态
check_app_health() {
    if curl -f http://localhost:8501/_stcore/health > /dev/null 2>&1; then
        echo "$(date): 应用健康检查通过" >> $LOG_FILE
        return 0
    else
        echo "$(date): 应用健康检查失败" >> $LOG_FILE
        return 1
    fi
}

# 检查数据库
check_database() {
    if [ -f "/opt/ad-ideas/data/adideas.db" ]; then
        db_size=$(du -h /opt/ad-ideas/data/adideas.db | cut -f1)
        echo "$(date): 数据库大小: $db_size" >> $LOG_FILE
    else
        echo "$(date): 数据库文件不存在" >> $LOG_FILE
    fi
}

# 检查磁盘空间
check_disk_space() {
    disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ $disk_usage -gt 80 ]; then
        echo "$(date): 警告: 磁盘使用率 ${disk_usage}%" >> $LOG_FILE
    fi
}

# 检查内存使用
check_memory() {
    memory_usage=$(free | grep Mem | awk '{printf("%.2f", $3/$2 * 100.0)}')
    echo "$(date): 内存使用率: ${memory_usage}%" >> $LOG_FILE
}

# 主监控循环
main() {
    echo "$(date): 开始监控检查" >> $LOG_FILE
    
    check_app_health
    if [ $? -ne 0 ]; then
        # 应用异常，尝试重启
        echo "$(date): 尝试重启应用" >> $LOG_FILE
        sudo systemctl restart ad-ideas
        sleep 30
        check_app_health
    fi
    
    check_database
    check_disk_space
    check_memory
    
    echo "$(date): 监控检查完成" >> $LOG_FILE
}

# 运行监控
main
```

**日志轮转配置 (/etc/logrotate.d/ad-ideas)**:
```
/var/log/ad-ideas-monitor.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
}
```

**Crontab配置**:
```bash
# 每5分钟检查一次应用状态
*/5 * * * * /opt/ad-ideas/monitor.sh

# 每天凌晨2点备份数据库
0 2 * * * cp /opt/ad-ideas/data/adideas.db /opt/ad-ideas/backups/adideas_$(date +\%Y\%m\%d).db

# 每周清理旧备份（保留30天）
0 3 * * 0 find /opt/ad-ideas/backups -name "adideas_*.db" -mtime +30 -delete
```

---

## 📋 项目交付清单

### ✅ 开发交付物

1. **源代码**
   - [x] 完整的Python应用代码
   - [x] 数据库模型和迁移脚本
   - [x] 前端页面和样式文件
   - [x] 配置文件和环境变量

2. **文档**
   - [x] 详细实施计划
   - [x] API文档和数据库设计
   - [x] 部署指南和运维手册
   - [x] 用户使用说明

3. **测试**
   - [x] 单元测试用例
   - [x] 集成测试脚本
   - [x] 性能测试报告
   - [x] 安全测试检查

### 🚀 部署交付物

1. **服务器配置**
   - [x] 阿里云ECS实例
   - [x] Nginx反向代理配置
   - [x] SSL证书配置
   - [x] 防火墙和安全组设置

2. **应用部署**
   - [x] Docker容器化配置
   - [x] 自动化部署脚本
   - [x] 系统服务配置
   - [x] 监控和日志系统

3. **数据和备份**
   - [x] 数据库初始化
   - [x] 自动备份策略
   - [x] 数据恢复流程
   - [x] 灾难恢复计划

### 📊 项目总结

**开发成果**:
- ✅ 完整的用户认证系统
- ✅ 专业的反馈收集系统
- ✅ 功能完善的评论系统
- ✅ 教授文章管理系统
- ✅ 响应式用户界面
- ✅ 完整的数据分析功能

**技术特点**:
- 🔐 安全的用户认证 (Streamlit-Authenticator)
- 💭 直观的用户反馈 (Streamlit-Feedback)
- 🗄️ 可靠的数据存储 (SQLite)
- ☁️ 稳定的云端部署 (阿里云)
- 📱 优秀的移动端体验
- 🚀 高性能的应用架构

**商业价值**:
- 💰 极低的运营成本 ($272/年)
- 📈 可扩展的用户规模
- 🎓 专业的学术平台
- 🌍 国际化的用户体验
- 📊 丰富的数据洞察
- 🔄 持续的内容更新

这个实施计划将在2周内交付一个完整、专业、可靠的广告学术平台，完美满足您的所有需求！

---

## 🤖 AI聊天系统集成方案

### 系统架构

**多AI后端支持**:
- **Gemini**: Google的免费AI模型，适合快速原型和个人使用
- **Ollama**: 本地部署的开源模型，完全私有化
- **Azure OpenAI**: 企业级GPT模型，稳定可靠

### 技术实现

#### 1. 统一AI管理器 (modules/ai_chat.py)
```python
class AIChat:
    """统一的AI聊天管理器，支持多种后端"""
    
    def __init__(self):
        self.backend = os.getenv('AI_BACKEND', 'gemini')
        self.client = None
        self.initialize_backend()
    
    def generate_response(self, prompt: str, history: List[Dict] = None) -> str:
        """统一的响应生成接口"""
        if self.client['type'] == 'gemini':
            return self._generate_gemini_response(prompt, history)
        elif self.client['type'] == 'ollama':
            return self._generate_ollama_response(prompt, history)
        elif self.client['type'] == 'azure_openai':
            return self._generate_azure_response(prompt, history)
```

#### 2. Ollama专用客户端 (chat_ollama.py)
```python
class OllamaChat:
    """Ollama本地AI聊天客户端"""
    
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url
        self.model = model
    
    def check_connection(self) -> bool:
        """检查Ollama服务状态"""
        
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        
    def stream_response(self, prompt: str, history: List[Dict] = None):
        """流式响应生成 - Ollama特色功能"""
```

#### 3. 环境配置管理
```bash
# .env 配置示例
AI_BACKEND=ollama

# Ollama配置
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# 其他AI后端配置...
```

### 用户界面设计

#### AI助手页面功能:
1. **后端状态显示**: 当前使用的AI模型和连接状态
2. **模型选择器**: (Ollama) 动态切换可用模型
3. **聊天界面**: 统一的对话体验
4. **流式回复**: (Ollama) 实时显示AI思考过程
5. **对话管理**: 清空历史、导出对话等

#### 集成到主应用:
- 在主导航中添加"🤖 AI助手"选项
- 侧边栏显示当前AI后端状态
- 与现有反馈和评论系统协同工作

### 部署考虑

#### Ollama本地部署:
1. **服务器要求**: 最低8GB内存，推荐16GB+
2. **模型下载**: `ollama pull llama2`
3. **服务启动**: `ollama serve`
4. **健康检查**: 定期检查服务状态

#### 中国部署优化:
- Ollama完全本地运行，无网络依赖
- Gemini在中国可正常访问
- Azure OpenAI有中国数据中心

### 成本分析

| AI后端 | 部署成本 | 运营成本 | 适用场景 |
|--------|----------|----------|----------|
| Ollama | 服务器成本 | $0 | 企业内网、隐私敏感 |
| Gemini | $0 | 免费额度 | 个人使用、快速原型 |
| Azure OpenAI | $0 | 按量付费 | 生产环境、企业应用 |

### 实施优先级

1. **Phase 1**: 集成现有的统一AI管理器到主应用
2. **Phase 2**: 完善Ollama本地部署功能
3. **Phase 3**: 优化用户界面和体验
4. **Phase 4**: 添加高级功能(模型切换、对话导出等)

这个方案确保了AI聊天功能的灵活性和可扩展性，同时保持了代码的简洁和可维护性。