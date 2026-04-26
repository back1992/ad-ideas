// App State
const API_BASE = '';  // Same origin in production, set in Capacitor config
let currentLang = 'zh';
let currentUser = null;
let currentPage = 'home';

// Translations
const T = {
    zh: {
        home: '首页', timeline: '大事年表', stars: '百位巨星',
        campaigns: '百大广告', articles: '文章', search: '搜索', data: '行业数据',
        login: '登录', logout: '退出', username: '用户名', password: '密码',
        loading: '加载中...', noData: '暂无数据', searchPlaceholder: '搜索...',
        welcome: '欢迎来到广告思想简史',
        welcomeDesc: '探索20世纪广告的发展历程，了解影响深远的广告大师与经典案例。',
        campaign: '广告', star: '巨星', article: '文章', event: '事件',
        back: '返回', views: '浏览', author: '作者', year: '年份',
        feedback: '您的看法', comments: '评论', submitComment: '发表评论',
        commentPlaceholder: '写下您的想法...', loginToComment: '请先登录',
        loginRequired: '请先登录以使用此功能', loginSuccess: '登录成功',
        loginFailed: '用户名或密码错误', thumbUp: '👍 赞同', thumbDown: '👎 反对',
        revenue: '广告收入(亿美元)', growth: '增长率(%)',
    },
    en: {
        home: 'Home', timeline: 'Timeline', stars: 'Top 100 Stars',
        campaigns: 'Top 100 Campaigns', articles: 'Articles', search: 'Search', data: 'Industry Data',
        login: 'Login', logout: 'Logout', username: 'Username', password: 'Password',
        loading: 'Loading...', noData: 'No data available', searchPlaceholder: 'Search...',
        welcome: 'Welcome to Advertising History',
        welcomeDesc: 'Explore the evolution of 20th century advertising, discover influential masters and classic campaigns.',
        campaign: 'Campaign', star: 'Star', article: 'Article', event: 'Event',
        back: 'Back', views: 'views', author: 'Author', year: 'Year',
        feedback: 'Your Feedback', comments: 'Comments', submitComment: 'Submit Comment',
        commentPlaceholder: 'Share your thoughts...', loginToComment: 'Please log in',
        loginRequired: 'Please log in to use this feature', loginSuccess: 'Login successful',
        loginFailed: 'Incorrect username or password', thumbUp: '👍 Like', thumbDown: '👎 Dislike',
        revenue: 'Revenue ($B)', growth: 'Growth (%)',
    }
};

function t(key) { return T[currentLang][key] || key; }

// DOM Helpers
function $(id) { return document.getElementById(id); }
function show(id) { $(id).classList.add('show'); }
function hide(id) { $(id).classList.remove('show'); }

// Loading
function showLoading() { show('loading'); }
function hideLoading() { hide('loading'); }

// API
async function api(path) {
    try {
        const res = await fetch(API_BASE + path, {
            headers: currentUser ? { 'X-Token': currentUser.token } : {}
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
    } catch (e) {
        console.error('API error:', e);
        return [];
    }
}

async function apiPost(path, body) {
    try {
        const res = await fetch(API_BASE + path, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(currentUser ? { 'X-Token': currentUser.token } : {})
            },
            body: JSON.stringify(body)
        });
        return await res.json();
    } catch (e) {
        console.error('API error:', e);
        return { error: e.message };
    }
}

// Navigation
function navigate(page) {
    currentPage = page;
    // Update active nav link
    document.querySelectorAll('.nav-link').forEach(el => {
        el.classList.toggle('active', el.dataset.page === page);
    });
    // Close sidebar
    closeSidebar();
    // Render page
    renderPage(page);
}

function renderPage(page) {
    const main = $('main-content');
    switch (page) {
        case 'home': renderHome(main); break;
        case 'timeline': renderTimeline(main); break;
        case 'stars': renderStars(main); break;
        case 'campaigns': renderCampaigns(main); break;
        case 'articles': renderArticles(main); break;
        case 'search': renderSearch(main); break;
        case 'data': renderData(main); break;
        case 'campaign-detail': renderCampaignDetail(main); break;
        case 'article-detail': renderArticleDetail(main); break;
        default: renderHome(main);
    }
}

// Sidebar
function toggleSidebar() {
    $('sidebar').classList.toggle('open');
    $('overlay').classList.toggle('show');
}

function closeSidebar() {
    $('sidebar').classList.remove('open');
    $('overlay').classList.remove('show');
}

// Language
function toggleLang() {
    currentLang = currentLang === 'zh' ? 'en' : 'zh';
    document.querySelector('.lang-btn').textContent = currentLang === 'zh' ? 'EN' : '中文';
    renderPage(currentPage);
    // Update sidebar nav labels
    const navLinks = document.querySelectorAll('.nav-link');
    const keys = ['home', 'timeline', 'stars', 'campaigns', 'articles', 'search', 'data'];
    navLinks.forEach((el, i) => {
        const icons = ['🏠', '📅', '⭐', '🎬', '📝', '', '📊'];
        el.textContent = `${icons[i]} ${t(keys[i])}`;
    });
}

// Auth
function showLogin() {
    $('login-modal').classList.add('show');
    $('login-error').textContent = '';
    $('login-user').value = '';
    $('login-pass').value = '';
}

function closeLogin() {
    $('login-modal').classList.remove('show');
}

async function doLogin() {
    const username = $('login-user').value.trim();
    const password = $('login-pass').value;
    if (!username || !password) {
        $('login-error').textContent = '请填写完整';
        return;
    }
    showLoading();
    const res = await apiPost('/api/auth/login', { username, password });
    hideLoading();
    if (res.error) {
        $('login-error').textContent = t('loginFailed');
    } else {
        currentUser = res;
        localStorage.setItem('token', res.token);
        localStorage.setItem('user', JSON.stringify({ name: res.name, role: res.role }));
        closeLogin();
        updateAuthUI();
    }
}

function logout() {
    currentUser = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    updateAuthUI();
}

function updateAuthUI() {
    const guestUI = $('guest-ui');
    const userUI = $('user-ui');
    if (currentUser) {
        guestUI.style.display = 'none';
        userUI.style.display = 'block';
        $('user-name').textContent = `👤 ${currentUser.name} (${currentUser.role})`;
    } else {
        guestUI.style.display = 'block';
        userUI.style.display = 'none';
    }
}

// Restore session
function restoreSession() {
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');
    if (token && user) {
        currentUser = { ...JSON.parse(user), token };
        updateAuthUI();
    }
}

// ---- Page Renderers ----

function renderHome(container) {
    container.innerHTML = `
        <div class="hero">
            <h2>${t('welcome')}</h2>
            <p>${t('welcomeDesc')}</p>
            <div class="hero-stats">
                <div class="hero-stat"><div class="num">100</div><div class="label">${t('campaign')}</div></div>
                <div class="hero-stat"><div class="num">100</div><div class="label">${t('star')}</div></div>
                <div class="hero-stat"><div class="num">∞</div><div class="label">${t('event')}</div></div>
            </div>
        </div>
        <div class="quick-links">
            <div class="quick-link" onclick="navigate('timeline')">
                <div class="icon">📅</div><div class="title">${t('timeline')}</div>
            </div>
            <div class="quick-link" onclick="navigate('stars')">
                <div class="icon">⭐</div><div class="title">${t('stars')}</div>
            </div>
            <div class="quick-link" onclick="navigate('campaigns')">
                <div class="icon">🎬</div><div class="title">${t('campaigns')}</div>
            </div>
            <div class="quick-link" onclick="navigate('articles')">
                <div class="icon">📝</div><div class="title">${t('articles')}</div>
            </div>
        </div>
    `;
}

async function renderTimeline(container) {
    container.innerHTML = `<div class="section-title">${t('timeline')}</div><div id="timeline-list"></div>`;
    showLoading();
    const data = await api('/api/timeline');
    hideLoading();
    const list = $('timeline-list');
    if (!data || data.length === 0) {
        list.innerHTML = `<div class="empty-state"><div class="icon">📅</div><p>${t('noData')}</p></div>`;
        return;
    }
    list.innerHTML = data.map(item => `
        <div class="timeline-item">
            <div class="timeline-year">${item.year || ''}</div>
            <div class="timeline-content">
                <h4>${item.event || item.title || ''}</h4>
                <p>${(item.description || '').substring(0, 100)}${(item.description || '').length > 100 ? '...' : ''}</p>
            </div>
        </div>
    `).join('');
}

async function renderStars(container) {
    container.innerHTML = `<div class="section-title">${t('stars')}</div><div id="stars-list"></div>`;
    showLoading();
    const data = await api('/api/stars');
    hideLoading();
    const list = $('stars-list');
    if (!data || data.length === 0) {
        list.innerHTML = `<div class="empty-state"><div class="icon">⭐</div><p>${t('noData')}</p></div>`;
        return;
    }
    list.innerHTML = data.map(item => `
        <div class="list-item">
            <div class="list-rank">${item.ranking || '#'}</div>
            <div class="list-info">
                <h4>${item.name || ''}</h4>
                <p>${item.title || item.role || ''}</p>
            </div>
        </div>
    `).join('');
}

async function renderCampaigns(container) {
    container.innerHTML = `<div class="section-title">${t('campaigns')}</div><div id="campaigns-list"></div>`;
    showLoading();
    const data = await api('/api/campaigns');
    hideLoading();
    const list = $('campaigns-list');
    if (!data || data.length === 0) {
        list.innerHTML = `<div class="empty-state"><div class="icon">🎬</div><p>${t('noData')}</p></div>`;
        return;
    }
    list.innerHTML = data.map(item => `
        <div class="list-item" onclick="viewCampaign(${item.id})">
            <div class="list-rank">${item.ranking || '#'}</div>
            <div class="list-info">
                <h4>${item.title || item.name || ''}</h4>
                <p>${item.brand || item.company || ''}</p>
            </div>
        </div>
    `).join('');
}

window.viewCampaign = async function(id) {
    showLoading();
    const data = await api(`/api/campaigns/${id}`);
    hideLoading();
    if (!data || data.error) return;
    const main = $('main-content');
    main.innerHTML = `
        <div class="detail-header">
            <button onclick="navigate('campaigns')" style="background:none;border:none;color:white;font-size:18px;padding:4px 0">${t('back')}</button>
            <h2>#${data.ranking || ''} ${data.title || ''}</h2>
            <div class="meta">${data.brand || ''} · ${data.year || ''}</div>
        </div>
        <div class="detail-body">
            <p>${data.description || ''}</p>
            ${data.agency ? `<p><strong>Agency:</strong> ${data.agency}</p>` : ''}
            ${data.creator ? `<p><strong>Creator:</strong> ${data.creator}</p>` : ''}
        </div>
        <div class="feedback-bar">
            <button class="feedback-btn" onclick="submitFeedback('campaign',${id},1)">👍</button>
            <button class="feedback-btn" onclick="submitFeedback('campaign',${id},0)">👎</button>
        </div>
        <div class="comments-section" id="comments-section">
            <h4>${t('comments')}</h4>
            <div class="comment-input">
                <textarea id="comment-text" placeholder="${t('commentPlaceholder')}"></textarea>
                <button onclick="submitComment('campaign',${id})">${t('submitComment')}</button>
            </div>
            <div id="comments-list"></div>
        </div>
    `;
    loadComments('campaign', id);
};

async function renderArticles(container) {
    container.innerHTML = `<div class="section-title">${t('articles')}</div><div id="articles-list"></div>`;
    showLoading();
    const data = await api('/api/articles');
    hideLoading();
    const list = $('articles-list');
    if (!data || data.length === 0) {
        list.innerHTML = `<div class="empty-state"><div class="icon">📝</div><p>${t('noData')}</p></div>`;
        return;
    }
    list.innerHTML = data.map(item => `
        <div class="list-item" onclick="viewArticle(${item.id})">
            <div class="list-info">
                <h4>${item.title || ''}</h4>
                <p>${item.author || ''} · ${item.category || ''}</p>
            </div>
        </div>
    `).join('');
}

window.viewArticle = async function(id) {
    showLoading();
    const data = await api(`/api/articles/${id}`);
    hideLoading();
    if (!data || data.error) return;
    const main = $('main-content');
    main.innerHTML = `
        <div class="detail-header">
            <button onclick="navigate('articles')" style="background:none;border:none;color:white;font-size:18px;padding:4px 0">${t('back')}</button>
            <h2>${data.title || ''}</h2>
            <div class="meta">${data.author || ''} · ${data.category || ''}</div>
        </div>
        <div class="detail-body">
            <p>${(data.content || '').replace(/\n/g, '<br>')}</p>
        </div>
        <div class="feedback-bar">
            <button class="feedback-btn" onclick="submitFeedback('article',${id},1)">👍</button>
            <button class="feedback-btn" onclick="submitFeedback('article',${id},0)">👎</button>
        </div>
    `;
};

async function renderSearch(container) {
    container.innerHTML = `
        <div class="section-title">${t('search')}</div>
        <div class="search-bar">
            <input type="text" id="search-input" placeholder="${t('searchPlaceholder')}">
            <button onclick="doSearch()">${t('search')}</button>
        </div>
        <div id="search-results"></div>
    `;
}

window.doSearch = async function() {
    const q = $('search-input').value.trim();
    if (!q) return;
    showLoading();
    const results = await api(`/api/search?q=${encodeURIComponent(q)}`);
    hideLoading();
    const container = $('search-results');
    let html = '';
    if (results.articles?.length) {
        html += `<div class="section-title">${t('article')} (${results.articles.length})</div>`;
        html += results.articles.map(a => `
            <div class="list-item" onclick="viewArticle(${a.id})">
                <div class="list-info"><h4>${a.title}</h4><p>${(a.excerpt || '').substring(0, 80)}</p></div>
            </div>
        `).join('');
    }
    if (results.timeline?.length) {
        html += `<div class="section-title">${t('event')} (${results.timeline.length})</div>`;
        html += results.timeline.map(e => `
            <div class="timeline-item">
                <div class="timeline-year">${e.year || ''}</div>
                <div class="timeline-content"><h4>${e.event || e.title || ''}</h4></div>
            </div>
        `).join('');
    }
    if (!html) {
        html = `<div class="empty-state"><div class="icon">🔍</div><p>${t('noData')}</p></div>`;
    }
    container.innerHTML = html;
};

async function renderData(container) {
    container.innerHTML = `<div class="section-title">${t('data')}</div><div class="chart-container"><canvas id="chart-revenue"></canvas></div>`;
    showLoading();
    const data = await api('/api/industry-data');
    hideLoading();
    if (!data || data.length === 0) {
        document.querySelector('.chart-container').innerHTML = `<div class="empty-state"><p>${t('noData')}</p></div>`;
        return;
    }

    // Simple canvas chart (no external dependency)
    const canvas = $('chart-revenue');
    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    canvas.width = canvas.offsetWidth * dpr;
    canvas.height = 250 * dpr;
    ctx.scale(dpr, dpr);

    const w = canvas.offsetWidth;
    const h = 250;
    const pad = 40;
    const chartW = w - pad * 2;
    const chartH = h - pad * 2;

    const maxVal = Math.max(...data.map(d => parseFloat(d.revenue) || 0));
    const barW = Math.max(4, (chartW / data.length) - 2);

    // Grid
    ctx.strokeStyle = '#eee';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
        const y = pad + (chartH / 4) * i;
        ctx.beginPath();
        ctx.moveTo(pad, y);
        ctx.lineTo(w - pad, y);
        ctx.stroke();
    }

    // Bars
    data.forEach((d, i) => {
        const val = parseFloat(d.revenue) || 0;
        const barH = maxVal > 0 ? (val / maxVal) * chartH : 0;
        const x = pad + (chartW / data.length) * i + (chartW / data.length - barW) / 2;
        const y = pad + chartH - barH;

        ctx.fillStyle = '#2E86AB';
        ctx.fillRect(x, y, barW, barH);

        // Label
        ctx.fillStyle = '#999';
        ctx.font = '9px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(d.year || '', x + barW / 2, h - 4);
    });
}

// Feedback
window.submitFeedback = async function(targetType, targetId, value) {
    if (!currentUser) {
        alert(t('loginRequired'));
        return;
    }
    const res = await apiPost('/api/feedback', {
        target_type: targetType,
        target_id: String(targetId),
        feedback_type: 'thumbs',
        feedback_value: value
    });
    if (res.error) alert(res.error);
    else alert('✓');
};

// Comments
async function loadComments(targetType, targetId) {
    const data = await api(`/api/comments?target_type=${targetType}&target_id=${targetId}`);
    const list = $('comments-list');
    if (!data || data.length === 0) {
        list.innerHTML = `<p style="color:#999;font-size:13px">${t('noData')}</p>`;
        return;
    }
    list.innerHTML = data.map(c => `
        <div class="comment-item">
            <div class="comment-author">${c.username || 'Anonymous'}</div>
            <div class="comment-text">${c.content || ''}</div>
            <div class="comment-time">${c.created_at ? c.created_at.substring(0, 16) : ''}</div>
        </div>
    `).join('');
}

window.submitComment = async function(targetType, targetId) {
    if (!currentUser) {
        alert(t('loginRequired'));
        return;
    }
    const text = $('comment-text').value.trim();
    if (!text) return;
    showLoading();
    const res = await apiPost('/api/comments', {
        target_type: targetType,
        target_id: String(targetId),
        content: text
    });
    hideLoading();
    if (res.error) alert(res.error);
    else {
        $('comment-text').value = '';
        loadComments(targetType, targetId);
    }
};

// Init
document.addEventListener('DOMContentLoaded', () => {
    restoreSession();
    updateAuthUI();
    // Handle enter key in search
    document.addEventListener('keydown', e => {
        if (e.key === 'Enter' && currentPage === 'search' && document.activeElement?.id === 'search-input') {
            doSearch();
        }
    });
});
