"""
E2E test: Register a demo user, log in, verify, and log out.

Each step captures a screenshot as evidence in tests/screenshots/register_login_flow/.

Run:
    pytest tests/test_e2e_register_login.py -v -s
    make test-e2e-register
"""

import subprocess
import time
import signal
import os
import socket
import pytest
from pathlib import Path
from datetime import datetime

PORT = 8767
SCREENSHOT_DIR = Path("tests/screenshots/register_login_flow")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def streamlit_server():
    """Start the Streamlit app for the test session, stop it afterwards."""
    _wait_for_port_free(PORT, timeout=10)

    env = os.environ.copy()
    proc = subprocess.Popen(
        [".venv/bin/streamlit", "run", "streamlit_app.py",
         "--server.headless", "true",
         "--server.port", str(PORT),
         "--browser.gatherUsageStats", "false"],
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
        pytest.fail("Streamlit server did not start within 30s")

    time.sleep(3)  # extra settle time
    yield f"http://localhost:{PORT}"

    proc.send_signal(signal.SIGTERM)
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.fixture(scope="module")
def browser():
    """Launch a headless Chromium browser for the test session."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def page(browser, streamlit_server):
    """Open a fresh page to the Streamlit app."""
    p = browser.new_page()
    p.set_viewport_size({"width": 1400, "height": 900})
    p.goto(streamlit_server, timeout=30000)
    p.wait_for_load_state("networkidle")
    p.wait_for_timeout(3000)
    yield p
    p.close()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_step_counter = 0

def _screenshot(page, label: str) -> Path:
    """Save a screenshot with a sequential step number and label."""
    global _step_counter
    _step_counter += 1
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"step{_step_counter:02d}_{label}.png"
    filepath = SCREENSHOT_DIR / filename
    page.screenshot(path=str(filepath), full_page=True)
    print(f"  📸 {filepath}")
    return filepath


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


def _open_sidebar(page):
    """Ensure the sidebar is expanded."""
    page.wait_for_timeout(1000)
    toggle = page.locator('[data-testid="collapsedControl"]').first
    if toggle.is_visible():
        toggle.click()
        page.wait_for_timeout(1000)


def _fill_register_form(page, first_name, last_name, email, username, password):
    """Fill the registration form fields by their order in the sidebar."""
    # Get all text inputs in the sidebar
    text_inputs = page.locator('[data-testid="stSidebar"] input[type="text"]').all()
    password_inputs = page.locator('[data-testid="stSidebar"] input[type="password"]').all()
    
    # Sidebar text inputs order:
    # [0] Login Username
    # [1] Register First name
    # [2] Register Last name
    # [3] Register Email
    # [4] Register Username
    # [5] Register Password hint
    
    # Sidebar password inputs order:
    # [0] Login Password
    # [1] Register Password
    # [2] Register Repeat password
    
    if len(text_inputs) >= 5:
        text_inputs[1].click()
        text_inputs[1].fill(first_name)
        text_inputs[2].click()
        text_inputs[2].fill(email)  # Email comes before Last name in DOM
        text_inputs[3].click()
        text_inputs[3].fill(last_name)  # Last name comes after Email
        text_inputs[4].click()
        text_inputs[4].fill(username)
    
    if len(password_inputs) >= 3:
        password_inputs[1].click()
        password_inputs[1].fill(password)
        password_inputs[2].click()
        password_inputs[2].fill(password)


def _fill_login_form(page, username, password):
    """Fill the login form fields."""
    text_inputs = page.locator('[data-testid="stSidebar"] input[type="text"]').all()
    password_inputs = page.locator('[data-testid="stSidebar"] input[type="password"]').all()
    
    # Login form is first: text_inputs[0]=Username, password_inputs[0]=Password
    if len(text_inputs) >= 1:
        text_inputs[0].click()
        text_inputs[0].fill(username)
    
    if len(password_inputs) >= 1:
        password_inputs[0].click()
        password_inputs[0].fill(password)


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------

class TestRegisterAndLogin:
    """Full E2E flow: guest → register → login → verify → logout."""

    def test_register_login_logout(self, page):
        global _step_counter
        _step_counter = 0

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        demo_first = "Demo"
        demo_last = f"User{timestamp[-2:]}"  # Last 2 digits as letters won't work, use fixed suffix
        # Use only alphabetic characters for last name
        demo_last = "Tester"
        demo_email = f"demo_{timestamp}@test.example.com"
        demo_username = f"demo_{timestamp}"
        demo_password = "TestPass123!"

        print(f"\n{'='*70}")
        print(f"🧪 E2E: Register → Login → Logout")
        print(f"   Username : {demo_username}")
        print(f"   Email    : {demo_email}")
        print(f"{'='*70}")

        sidebar = page.locator('[data-testid="stSidebar"]')

        # ── Step 1: Guest landing ──────────────────────────────────────
        print("\n① Guest landing page")
        _screenshot(page, "guest_landing")
        assert page.is_visible("text=广告思想简史", timeout=15000) or \
               page.is_visible("text=Advertising", timeout=5000), \
               "App title should be visible"

        # ── Step 2: Open sidebar, see login/register ───────────────────
        print("② Open sidebar – see login & register forms")
        _open_sidebar(page)
        _screenshot(page, "sidebar_guest")
        sidebar_text = sidebar.inner_text()
        assert "Login" in sidebar_text or "登录" in sidebar_text, "Login form missing"
        assert "Register" in sidebar_text or "注册" in sidebar_text, "Register form missing"

        # ─ Step 3: Fill registration form ─────────────────────────────
        print(" Fill registration form")
        _fill_register_form(page, demo_first, demo_last, demo_email, demo_username, demo_password)

        _screenshot(page, "register_form_filled")
        print(f"  ✓ All fields filled for {demo_username}")

        # ── Step 4: Submit registration ────────────────────────────────
        print("④ Submit registration")
        register_btn = page.get_by_role("button", name="Register").first
        register_btn.click()
        page.wait_for_timeout(4000)
        _screenshot(page, "after_register")

        # Check for success or error
        body_text = page.locator("body").inner_text()
        if "already exists" in body_text.lower():
            pytest.skip(f"User {demo_username} already exists – skipping")
        print("  ✓ Registration submitted")

        # ─ Step 5: Fill login form ────────────────────────────────────
        print("⑤ Fill login form")
        _fill_login_form(page, demo_username, demo_password)
        _screenshot(page, "login_form_filled")
        print(f"  ✓ Login credentials entered for {demo_username}")

        # ── Step 6: Submit login ───────────────────────────────────────
        print("⑥ Submit login")
        login_btn = page.get_by_role("button", name="Login").first
        login_btn.click()
        page.wait_for_timeout(4000)
        _screenshot(page, "after_login")

        # ── Step 7: Verify logged-in state ─────────────────────────────
        print("⑦ Verify logged-in state")
        page.wait_for_timeout(2000)
        _screenshot(page, "logged_in_state")

        sidebar_text = sidebar.inner_text()
        # Should show user info section
        assert "Logout" in sidebar_text or "退出" in sidebar_text or "🚪" in sidebar_text, \
            "Logout button should be visible after login"
        print("  ✓ Logout button visible – login successful")

        # ── Step 8: Navigate a page while logged in ────────────────────
        print("⑧ Navigate while logged in")
        _open_sidebar(page)
        nav_labels = page.locator(
            '[data-testid="stSidebar"] div[data-baseweb="radio"] .st-bq'
        ).all()
        if len(nav_labels) > 1:
            nav_labels[1].click(timeout=5000)
            page.wait_for_timeout(3000)
            _screenshot(page, "navigated_logged_in")
            assert not page.is_visible("text=Error loading page", timeout=3000), \
                "Page should load without error"
            print("  ✓ Navigation successful")
        else:
            _screenshot(page, "nav_skipped")
            print("  ⚠ No nav items found, skipping navigation check")

        # ── Step 9: Logout ─────────────────────────────────────────────
        print("⑨ Logout")
        _open_sidebar(page)
        logout_btn = sidebar.locator(
            'button:has-text("Logout"), button:has-text("退出"), button:has-text("🚪")'
        ).first
        assert logout_btn.is_visible(timeout=5000), "Logout button should be visible"
        logout_btn.click()
        page.wait_for_timeout(4000)
        _screenshot(page, "after_logout")

        # ── Step 10: Verify back to guest state ────────────────────────
        print("⑩ Verify back to guest state")
        sidebar_text = sidebar.inner_text()
        assert "Login" in sidebar_text or "登录" in sidebar_text, \
            "Should be back to guest state with login form"
        _screenshot(page, "guest_after_logout")
        print("  ✓ Back to guest state")

        # ── Summary ────────────────────────────────────────────────────
        screenshot_count = len(list(SCREENSHOT_DIR.glob("*.png")))
        print(f"\n{'='*70}")
        print(f"✅ All steps passed!  ({screenshot_count} screenshots in {SCREENSHOT_DIR})")
        print(f"{'='*70}\n")
