"""
Authentication Manager for 广告思想简史 Platform

Centralized user authentication and role-based access control
using streamlit-authenticator.
"""

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from typing import Optional, Tuple, Dict, Any
from utils.logger import create_logger
from modules.database import DatabaseManager

VALID_ROLES = frozenset({"student", "professor", "admin"})

ROLE_HIERARCHY = {
    "student": 1,
    "professor": 2,
    "admin": 3,
}

_SESSION_KEYS = ("name", "username", "authentication_status", "user_role")


class AuthManager:
    """Handles login, logout, role checks, and session management."""

    def __init__(self, config_path: str = "config.yaml", db_manager: Optional[DatabaseManager] = None):
        self.config_path = config_path
        self.db_manager = db_manager
        self.logger = create_logger("AuthManager")
        self.config = self._load_config()
        self.authenticator = self._create_authenticator()

    # ------------------------------------------------------------------
    # Config helpers
    # ------------------------------------------------------------------

    def _load_config(self) -> Dict[str, Any]:
        with open(self.config_path, "r", encoding="utf-8") as file:
            return yaml.load(file, Loader=SafeLoader)

    def _save_config(self) -> None:
        with open(self.config_path, "w", encoding="utf-8") as file:
            yaml.dump(self.config, file, default_flow_style=False, allow_unicode=True)

    def _create_authenticator(self) -> stauth.Authenticate:
        try:
            return stauth.Authenticate(
                credentials=self.config["credentials"],
                cookie_name=self.config["cookie"]["name"],
                cookie_key=self.config["cookie"]["key"],
                cookie_expiry_days=self.config["cookie"]["expiry_days"],
            )
        except TypeError:
            return stauth.Authenticate(
                self.config["credentials"],
                self.config["cookie"]["name"],
                self.config["cookie"]["key"],
                self.config["cookie"]["expiry_days"],
            )

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    @staticmethod
    def _init_session_state() -> None:
        for key in _SESSION_KEYS:
            if key not in st.session_state:
                st.session_state[key] = None
        if "logout" not in st.session_state:
            st.session_state["logout"] = None

    @staticmethod
    def _clear_session_state() -> None:
        for key in _SESSION_KEYS:
            st.session_state.pop(key, None)

    # ------------------------------------------------------------------
    # Login / logout
    # ------------------------------------------------------------------

    def login(self, location: str = "main", key: str = "Login") -> Tuple[Optional[str], Optional[bool], Optional[str]]:
        self._init_session_state()

        # Try different API versions
        login_result = None
        for api_call in [
            lambda: self.authenticator.login(fields={"Form name": "Login"}, location=location, key=key),
            lambda: self.authenticator.login(location, key),
            lambda: self.authenticator.login(),
        ]:
            try:
                login_result = api_call()
                break
            except TypeError:
                continue

        if login_result is None:
            name = st.session_state.get("name")
            authentication_status = st.session_state.get("authentication_status")
            username = st.session_state.get("username")
        else:
            name, authentication_status, username = login_result

        if authentication_status:
            if not self.is_user_active(username):
                st.error("Your account has been suspended. Please contact an administrator.")
                self.force_logout()
                return None, False, None

            self._log_user_activity(username, "login", "User logged in")
            st.session_state["name"] = name
            st.session_state["username"] = username
            st.session_state["authentication_status"] = True
            st.session_state["user_role"] = self.get_user_role(username)

        elif authentication_status is False:
            self._log_user_activity(username or "unknown", "login_failed", "Failed login attempt")

        return name, authentication_status, username

    def logout(self, location: str = "main", key: str = "Logout") -> None:
        username = st.session_state.get("username")

        for api_call in [
            lambda: self.authenticator.logout(location, key),
            lambda: self.authenticator.logout(),
        ]:
            try:
                api_call()
                break
            except (TypeError, Exception):
                continue

        if username:
            self._log_user_activity(username, "logout", "User logged out")

        self._clear_session_state()

    def force_logout(self) -> None:
        username = st.session_state.get("username")

        if username:
            self._log_user_activity(username, "logout", "User logged out")

        self._clear_session_state()

        # Clear streamlit-authenticator internal state
        for attr in ("authentication_status", "name", "username"):
            if hasattr(self.authenticator, attr):
                setattr(self.authenticator, attr, None)

        try:
            self.authenticator.logout("sidebar", "Logout")
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_user(self, location: str = "main", key: str = "Register", captcha: bool = True) -> bool:
        if not hasattr(self.authenticator, "register_user"):
            return False

        result = self.authenticator.register_user(location, key, captcha=captcha)
        if result is None:
            return False

        email, username, name = result
        if not email:
            return False

        # Set default role for new users
        users = self.config.get("credentials", {}).get("usernames", {})
        if username in users and "role" not in users[username]:
            users[username]["role"] = "student"
            users[username]["is_active"] = True

        self._log_user_activity(username, "register", f"New user registered: {name}")
        self._save_config()
        return True

    # ------------------------------------------------------------------
    # User info
    # ------------------------------------------------------------------

    def get_user_role(self, username: str) -> str:
        users = self.config.get("credentials", {}).get("usernames", {})
        return users.get(username, {}).get("role", "student")

    def is_user_active(self, username: str) -> bool:
        users = self.config.get("credentials", {}).get("usernames", {})
        return users.get(username, {}).get("is_active", True)

    def _resolve_username(self, username: Optional[str]) -> Optional[str]:
        return username if username else st.session_state.get("username")

    # ------------------------------------------------------------------
    # Role & permission checks
    # ------------------------------------------------------------------

    def has_role(self, role: str, username: Optional[str] = None) -> bool:
        """Check if user has exactly the given role."""
        resolved = self._resolve_username(username)
        return resolved is not None and self.get_user_role(resolved) == role

    def has_min_role(self, role: str, username: Optional[str] = None) -> bool:
        """Check if user's role is at least the given level."""
        resolved = self._resolve_username(username)
        if resolved is None:
            return False
        user_level = ROLE_HIERARCHY.get(self.get_user_role(resolved), 0)
        required_level = ROLE_HIERARCHY.get(role, 0)
        return user_level >= required_level

    def is_admin(self, username: Optional[str] = None) -> bool:
        return self.has_role("admin", username)

    def is_professor(self, username: Optional[str] = None) -> bool:
        return self.has_role("professor", username)

    def is_professor_or_admin(self, username: Optional[str] = None) -> bool:
        return self.has_min_role("professor", username)

    def is_student(self, username: Optional[str] = None) -> bool:
        return self.has_role("student", username)

    # ------------------------------------------------------------------
    # Deprecated / UI helpers — kept for backwards compatibility
    # ------------------------------------------------------------------

    def check_permission(self, required_role: str, username: Optional[str] = None) -> bool:
        return self.has_min_role(required_role, username)

    def require_authentication(self) -> bool:
        status = st.session_state.get("authentication_status")
        if status is True:
            return True
        if status is False:
            st.error("Username/password is incorrect")
        else:
            st.warning("Please enter your username and password")
        return False

    def require_role(self, required_role: str, username: Optional[str] = None) -> bool:
        if not self.has_min_role(required_role, username):
            st.error(f"Access denied. This feature requires {required_role} role or higher.")
            return False
        return True

    def get_current_user(self) -> Dict[str, Any]:
        username = st.session_state.get("username")
        role = st.session_state.get("user_role")

        if username and not role:
            role = self.get_user_role(username)
            st.session_state["user_role"] = role

        return {
            "name": st.session_state.get("name"),
            "username": username,
            "role": role,
            "authenticated": st.session_state.get("authentication_status", False),
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _log_user_activity(self, username: str, action: str, details: str) -> None:
        if self.db_manager:
            try:
                self.db_manager.execute_update(
                    "INSERT INTO user_activity (username, action, details) VALUES (?, ?, ?)",
                    (username, action, details),
                )
            except Exception:
                self.logger.error(f"Failed to log user activity: {action} for {username}")


def get_auth_manager(config_path: str = "config.yaml", db_manager: Optional[DatabaseManager] = None) -> AuthManager:
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager(config_path, db_manager)
    return _auth_manager


_auth_manager: Optional[AuthManager] = None
