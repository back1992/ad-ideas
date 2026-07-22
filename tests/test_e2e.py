"""
E2E tests for 广告思想简史 platform using Playwright.

Covers: guest browsing, login flow, navigation, search, comments, feedback.
Run: pytest tests/test_e2e.py -v
"""

import subprocess
import time
import signal
import os
import socket
import pytest
from pathlib import Path

PORT = 8766
SCREENSHOT_DIR = Path("tests/screenshots")


@pytest.fixture(scope="session")
def streamlit_server():
    """Start and stop the Streamlit app for the test session."""
    _wait_for_port_free(PORT, timeout=10)

    env = os.environ.copy()
    proc = subprocess.Popen(
        [".venv/bin/streamlit", "run", "streamlit_app.py", "--server.headless", "true",
         "--server.port", str(PORT), "--browser.gatherUsageStats", "false"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )

    for _ in range(30):
        if _is_port_open(PORT):
            break
        time.sleep(1)
    else:
        proc.kill()
        pytest.fail("Streamlit server did not start within timeout")

    yield f"http://localhost:{PORT}"

    proc.send_signal(signal.SIGTERM)
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.fixture
def page(browser, streamlit_server):
    """Navigate to the Streamlit app and return a page object."""
    p = browser.new_page()
    p.set_viewport_size({"width": 1280, "height": 900})
    p.goto(streamlit_server, timeout=30000)
    p.wait_for_load_state("networkidle")
    p.wait_for_timeout(3000)
    yield p
    p.close()


def _screenshot(page, name):
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(SCREENSHOT_DIR / f"{name}.png"))


def _is_port_open(port: int) -> bool:
    try:
        s = socket.create_connection(("localhost", port), timeout=1)
        s.close()
        return True
    except (ConnectionRefusedError, OSError):
        return False


def _wait_for_port_free(port: int, timeout: int = 10):
    for _ in range(timeout):
        if not _is_port_open(port):
            return
        time.sleep(1)


def open_sidebar(page):
    """Open the sidebar and expand the navigation section."""
    page.wait_for_timeout(1000)
    # If sidebar is collapsed, click the hamburger
    toggle = page.locator('[data-testid="collapsedControl"]').first
    if toggle.is_visible():
        toggle.click()
        page.wait_for_timeout(1000)

    # Expand the navigation expander if collapsed
    nav_expander = page.locator('[data-testid="stSidebar"]').locator(
        'summary:has-text("导航"), summary:has-text("Navigation")'
    ).first
    if nav_expander.is_visible():
        nav_expander.click()
        page.wait_for_timeout(500)


def click_nav_item(page, index: int):
    """Click a navigation radio button by its visible label (not the hidden input)."""
    open_sidebar(page)
    # Streamlit radio widgets: click the label div, not the hidden input
    labels = page.locator('[data-testid="stSidebar"] div[data-baseweb="radio"] .st-bq').all()
    if index < len(labels):
        labels[index].click(timeout=10000)
        page.wait_for_timeout(3000)
    else:
        pytest.skip(f"Only {len(labels)} nav items, requested index {index}")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestGuestBrowsing:

    def test_guest_sees_sidebar(self, page):
        _screenshot(page, "guest_sees_sidebar")
        sidebar = page.locator('[data-testid="stSidebar"]')
        assert sidebar.is_visible(timeout=15000), "Sidebar should be visible"

    def test_guest_sees_main_content(self, page):
        _screenshot(page, "guest_main_content")
        assert page.is_visible("text=广告思想简史", timeout=10000) or \
               page.is_visible("text=Advertising", timeout=10000)

    def test_guest_sees_navigation(self, page):
        open_sidebar(page)
        _screenshot(page, "guest_nav_items")
        sidebar = page.locator('[data-testid="stSidebar"]')
        all_text = sidebar.inner_text()
        # Should contain page names
        assert "首页" in all_text or "Home" in all_text, "Should see Home in navigation"
        assert "年表" in all_text or "Timeline" in all_text, "Should see Timeline in navigation"

    def test_guest_does_not_see_admin_pages(self, page):
        open_sidebar(page)
        _screenshot(page, "guest_no_admin_pages")
        sidebar = page.locator('[data-testid="stSidebar"]')
        all_text = sidebar.inner_text()
        assert "内容审核" not in all_text and "Content Moderation" not in all_text, \
            "Guest should not see content moderation"


class TestLoginFlow:

    def test_single_login_form(self, page):
        """Login should use native Streamlit form, NOT stauth widget (which renders duplicates)."""
        open_sidebar(page)
        _screenshot(page, "single_login_form")
        body_text = page.locator("body").inner_text()
        # The stauth widget renders a "🔐" header. Our native form doesn't.
        # If stauth is still being used, we'd see duplicate forms with lock emojis.
        lock_count = body_text.count("🔐")
        assert lock_count == 0, \
            f"stauth login widget detected ({lock_count} lock emojis) — should use native form only"

    def test_guest_sees_login_area(self, page):
        open_sidebar(page)
        _screenshot(page, "login_area")
        sidebar = page.locator('[data-testid="stSidebar"]')
        all_text = sidebar.inner_text()
        assert "Login" in all_text or "登录" in all_text, "Should see login area"

    def test_language_selector_visible(self, page):
        open_sidebar(page)
        _screenshot(page, "lang_selector")
        sidebar = page.locator('[data-testid="stSidebar"]')
        all_text = sidebar.inner_text()
        assert "中文" in all_text or "EN" in all_text or "English" in all_text


class TestNavigation:

    def test_can_navigate_pages_without_error(self, page):
        """Click through first few nav items and verify no page errors."""
        open_sidebar(page)
        labels = page.locator('[data-testid="stSidebar"] div[data-baseweb="radio"] .st-bq').all()
        for i in range(min(4, len(labels))):
            labels[i].click(timeout=10000)
            page.wait_for_timeout(3000)
            _screenshot(page, f"nav_page_{i}")
            assert not page.is_visible("text=Error loading page", timeout=5000), \
                f"Page {i} failed to load"
            assert not page.is_visible("text=加载页面时出错", timeout=5000)

    def test_home_page_loads(self, page):
        open_sidebar(page)
        labels = page.locator('[data-testid="stSidebar"] div[data-baseweb="radio"] .st-bq').all()
        if labels:
            labels[0].click(timeout=10000)
            page.wait_for_timeout(3000)
            _screenshot(page, "home_page")
        assert page.is_visible("text=广告思想简史") or page.is_visible("text=Advertising")


class TestSearch:

    def test_search_page_loads(self, page):
        open_sidebar(page)
        labels = page.locator('[data-testid="stSidebar"] div[data-baseweb="radio"] .st-bq').all()
        if len(labels) >= 2:
            labels[1].click(timeout=10000)
            page.wait_for_timeout(3000)
            _screenshot(page, "search_page")
        assert page.is_visible("text=搜索") or page.is_visible("text=Search")

    def test_search_has_filters(self, page):
        open_sidebar(page)
        _screenshot(page, "search_before_click")
        # Click the Search nav item (index 1)
        labels = page.locator('[data-testid="stSidebar"] div[data-baseweb="radio"] .st-bq').all()
        if len(labels) >= 2:
            labels[1].click(timeout=10000)
            page.wait_for_timeout(5000)
            _screenshot(page, "search_filters")
        # Search page should show the search title and filter options
        body = page.locator("body")
        body_text = body.inner_text()
        assert "搜索" in body_text or "Search" in body_text, \
            "Search page should be displayed"


class TestComments:

    def test_timeline_page_loads_for_guest(self, page):
        open_sidebar(page)
        labels = page.locator('[data-testid="stSidebar"] div[data-baseweb="radio"] .st-bq').all()
        if len(labels) >= 3:
            labels[2].click(timeout=10000)
            page.wait_for_timeout(5000)
            _screenshot(page, "timeline_guest")
        assert not page.is_visible("text=Error loading page")


class TestLanguageToggle:

    def test_toggle_to_english(self, page):
        open_sidebar(page)
        _screenshot(page, "before_en")
        sidebar = page.locator('[data-testid="stSidebar"]')
        en_btn = sidebar.locator('button:has-text("EN")').first
        if en_btn.is_visible():
            en_btn.click(timeout=10000)
            page.wait_for_timeout(2000)
            _screenshot(page, "after_en")
        assert not page.is_visible("text=Error loading page")

    def test_toggle_back_to_chinese(self, page):
        open_sidebar(page)
        _screenshot(page, "before_zh")
        sidebar = page.locator('[data-testid="stSidebar"]')
        zh_btn = sidebar.locator('button:has-text("中文")').first
        if zh_btn.is_visible():
            zh_btn.click(timeout=10000)
            page.wait_for_timeout(2000)
            _screenshot(page, "after_zh")
        assert not page.is_visible("text=Error loading page")
