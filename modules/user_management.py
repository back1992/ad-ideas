"""
User Management System for 广告思想简史 Platform

Admin tools for role management, activity monitoring, and account control.
"""

import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any
from modules.database import DatabaseManager
from modules.auth import AuthManager


class UserManagementSystem:
    """Admin-facing user management dashboard."""

    def __init__(self, db_manager: DatabaseManager, auth_manager: AuthManager):
        self.db_manager = db_manager
        self.auth_manager = auth_manager

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def show_user_management_dashboard(self, admin_username: str) -> None:
        if not self.auth_manager.is_admin(admin_username):
            st.error("Access denied. Only administrators can access user management.")
            return

        st.markdown("# User Management Dashboard")
        st.markdown("Manage user accounts, roles, and monitor activity")

        stats = self.get_user_statistics()
        self._display_user_statistics(stats)

        st.markdown("---")

        tab1, tab2, tab3 = st.tabs([
            "User Accounts",
            "Activity Monitoring",
            "Role Management",
        ])

        with tab1:
            self._display_user_accounts(admin_username)
        with tab2:
            self._display_activity_monitoring(admin_username)
        with tab3:
            self._display_role_management()

    # ------------------------------------------------------------------
    # Config mutation (atomic load → modify → save → reload)
    # ------------------------------------------------------------------

    def _update_user_config(self, username: str, updates: Dict[str, Any]) -> bool:
        """Apply updates to a user's config entry and persist."""
        users = self.auth_manager.config.get("credentials", {}).get("usernames", {})
        if username not in users:
            return False

        users[username].update(updates)
        self.auth_manager._save_config()
        self.auth_manager.config = self.auth_manager._load_config()
        return True

    def suspend_user(self, username: str, admin_username: str) -> bool:
        if self._update_user_config(username, {"is_active": False}):
            self._log_action(admin_username, "user_suspended", username, f"Suspended user account: {username}")
            return True
        return False

    def activate_user(self, username: str, admin_username: str) -> bool:
        if self._update_user_config(username, {"is_active": True}):
            self._log_action(admin_username, "user_activated", username, f"Activated user account: {username}")
            return True
        return False

    def change_user_role(self, username: str, new_role: str, admin_username: str) -> bool:
        users = self.auth_manager.config.get("credentials", {}).get("usernames", {})
        old_role = users.get(username, {}).get("role", "student")
        if self._update_user_config(username, {"role": new_role}):
            self._log_action(admin_username, "user_role_changed", username,
                             f"Changed role from {old_role} to {new_role} for user: {username}")
            return True
        return False

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_user_statistics(self) -> Dict[str, Any]:
        try:
            users = self.get_all_users()
            stats = {"total_users": len(users), "admins": 0, "professors": 0, "students": 0,
                     "active_today": 0, "suspended": 0}

            for data in users.values():
                role = data.get("role", "student")
                if role == "admin":
                    stats["admins"] += 1
                elif role == "professor":
                    stats["professors"] += 1
                else:
                    stats["students"] += 1
                if not data.get("is_active", True):
                    stats["suspended"] += 1

            result = self.db_manager.execute_query(
                "SELECT COUNT(DISTINCT username) as active FROM user_activity WHERE DATE(timestamp) = DATE('now')"
            )
            if not result.empty:
                stats["active_today"] = int(result.iloc[0]["active"])
            return stats
        except Exception:
            return {"total_users": 0, "admins": 0, "professors": 0, "students": 0, "active_today": 0, "suspended": 0}

    def get_all_users(self) -> Dict[str, Dict[str, Any]]:
        try:
            return self.auth_manager.config.get("credentials", {}).get("usernames", {})
        except Exception:
            return {}

    def get_user_activity_stats(self, username: str) -> Dict[str, Any]:
        try:
            total = self.db_manager.execute_query(
                "SELECT COUNT(*) as total FROM user_activity WHERE username = ?", (username,)
            )
            last = self.db_manager.execute_query(
                "SELECT MAX(timestamp) as last_active FROM user_activity WHERE username = ?", (username,)
            )
            return {
                "total_actions": int(total.iloc[0]["total"]) if not total.empty else 0,
                "last_active": last.iloc[0]["last_active"] if not last.empty and last.iloc[0]["last_active"] else "Never",
            }
        except Exception:
            return {"total_actions": 0, "last_active": "Unknown"}

    def get_user_recent_activity(self, username: str, limit: int = 10) -> pd.DataFrame:
        try:
            return self.db_manager.execute_query(
                "SELECT * FROM user_activity WHERE username = ? ORDER BY timestamp DESC LIMIT ?",
                (username, limit),
            )
        except Exception:
            return pd.DataFrame()

    def get_activity_log(self, username: Optional[str] = None,
                         action: Optional[str] = None,
                         days_back: int = 7) -> pd.DataFrame:
        try:
            query = "SELECT * FROM user_activity WHERE datetime(timestamp) >= datetime('now', '-' || ? || ' days')"
            params: list = [days_back]
            if username:
                query += " AND username = ?"
                params.append(username)
            if action:
                query += " AND action = ?"
                params.append(action)
            query += " ORDER BY timestamp DESC LIMIT 1000"
            return self.db_manager.execute_query(query, tuple(params))
        except Exception:
            return pd.DataFrame()

    # ------------------------------------------------------------------
    # UI sections
    # ------------------------------------------------------------------

    def _display_user_statistics(self, stats: Dict[str, Any]) -> None:
        col1, col2, col3, col4, col5 = st.columns(5)
        metrics = [
            ("Total Users", stats["total_users"]),
            ("Admins", stats["admins"]),
            ("Professors", stats["professors"]),
            ("Students", stats["students"]),
            ("Active Today", stats["active_today"]),
        ]
        for col, (label, value) in zip([col1, col2, col3, col4, col5], metrics):
            col.metric(label, value)

    def _display_user_accounts(self, admin_username: str) -> None:
        st.markdown("### User Accounts")
        users = self.get_all_users()
        if not users:
            st.info("No users found.")
            return

        col1, col2 = st.columns(2)
        role_filter = col1.selectbox("Filter by Role", ["All", "admin", "professor", "student"], key="user_role_filter")
        status_filter = col2.selectbox("Filter by Status", ["All", "Active", "Suspended"], key="user_status_filter")

        filtered = {k: v for k, v in users.items()
                    if (role_filter == "All" or v.get("role", "student") == role_filter)
                    and (status_filter == "All"
                         or (status_filter == "Active" and v.get("is_active", True))
                         or (status_filter == "Suspended" and not v.get("is_active", True)))}

        st.markdown(f"**{len(filtered)} user(s) found**")

        for username, user_data in filtered.items():
            is_active = user_data.get("is_active", True)
            with st.expander(
                f"{'🔴' if not is_active else '🟢'} "
                f"{user_data.get('name', username)} (@{username}) - "
                f"{user_data.get('role', 'student').upper()}"
            ):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Username:** {username}")
                    st.markdown(f"**Name:** {user_data.get('name', 'N/A')}")
                    st.markdown(f"**Email:** {user_data.get('email', 'N/A')}")
                    st.markdown(f"**Role:** {user_data.get('role', 'student')}")
                with col2:
                    st.markdown(f"**Status:** {'Active' if is_active else 'Suspended'}")
                    activity = self.get_user_activity_stats(username)
                    st.markdown(f"**Total Actions:** {activity['total_actions']}")
                    st.markdown(f"**Last Active:** {activity['last_active']}")

                st.markdown("---")
                col1, col2, col3 = st.columns(3)

                if username != admin_username:
                    with col1:
                        label = "Suspend Account" if is_active else "Activate Account"
                        if st.button(label, key=f"toggle_{username}"):
                            ok = self.activate_user(username, admin_username) if not is_active else self.suspend_user(username, admin_username)
                            if ok:
                                st.success(f"User {username} {'activated' if not is_active else 'suspended'}")
                                st.rerun()

                    with col2:
                        if st.button("Change Role", key=f"role_{username}"):
                            st.session_state[f"changing_role_{username}"] = True
                            st.rerun()

                with col3:
                    if st.button("View Activity", key=f"activity_{username}"):
                        st.session_state[f"viewing_activity_{username}"] = True
                        st.rerun()

                # Role change form
                if st.session_state.pop(f"changing_role_{username}", False):
                    with st.form(f"role_form_{username}"):
                        st.markdown("**Change User Role:**")
                        new_role = st.selectbox(
                            "Select new role:",
                            ["student", "professor", "admin"],
                            index=["student", "professor", "admin"].index(user_data.get("role", "student")),
                            key=f"new_role_{username}",
                        )
                        c1, c2 = st.columns(2)
                        if c1.form_submit_button("Save Changes"):
                            if self.change_user_role(username, new_role, admin_username):
                                st.success(f"Role changed to {new_role}")
                                st.rerun()
                        if c2.form_submit_button("Cancel"):
                            st.rerun()

                # Activity view
                if st.session_state.pop(f"viewing_activity_{username}", False):
                    st.markdown("**Recent Activity:**")
                    recent = self.get_user_recent_activity(username, limit=10)
                    if recent.empty:
                        st.info("No recent activity")
                    else:
                        for _, row in recent.iterrows():
                            st.caption(
                                f"{row['timestamp'][:16]} - {row['action']}: "
                                f"{row['details'][:50] if row['details'] else 'N/A'}"
                            )
                    if st.button("Close", key=f"close_activity_{username}"):
                        st.rerun()

    def _display_activity_monitoring(self, admin_username: str) -> None:
        st.markdown("### User Activity Monitoring")

        col1, col2, col3 = st.columns(3)
        username_filter = col1.text_input("Filter by Username", placeholder="Enter username", key="activity_username_filter")
        action_filter = col2.selectbox(
            "Filter by Action Type",
            ["All", "login", "comment_posted", "feedback_submitted", "article_created", "article_viewed"],
            key="activity_action_filter",
        )
        days_back = col3.selectbox(
            "Time Period",
            [1, 7, 30, 90],
            format_func=lambda x: f"Last {x} day{'s' if x > 1 else ''}",
            index=1,
            key="activity_days_filter",
        )

        activity_log = self.get_activity_log(
            username=username_filter or None,
            action=action_filter if action_filter != "All" else None,
            days_back=days_back,
        )

        if activity_log.empty:
            st.info("No activity found for the selected filters.")
            return

        st.markdown(f"**Found {len(activity_log)} activity record(s)**")

        col1, col2 = st.columns(2)
        action_counts = activity_log["action"].value_counts()
        col1.markdown("**Actions by Type:**")
        for action, count in action_counts.items():
            col1.write(f"- {action}: {count}")

        user_counts = activity_log["username"].value_counts().head(10)
        col2.markdown("**Most Active Users:**")
        for user, count in user_counts.items():
            col2.write(f"- {user}: {count} actions")

        st.markdown("---")
        st.markdown("#### Detailed Activity Log")

        for _, activity in activity_log.head(50).iterrows():
            with st.expander(f"{activity['username']} - {activity['action']} - {activity['timestamp'][:16]}"):
                c1, c2 = st.columns(2)
                c1.markdown(f"**User:** {activity['username']}")
                c1.markdown(f"**Action:** {activity['action']}")
                c1.markdown(f"**Timestamp:** {activity['timestamp']}")
                if activity["target_type"]:
                    c2.markdown(f"**Target Type:** {activity['target_type']}")
                if activity["target_id"]:
                    c2.markdown(f"**Target ID:** {activity['target_id']}")
                if activity["details"]:
                    st.markdown(f"> {activity['details']}")

        if len(activity_log) > 50:
            st.info(f"Showing first 50 of {len(activity_log)} records")

    def _display_role_management(self) -> None:
        st.markdown("### Role Management")
        users = self.get_all_users()

        by_role: Dict[str, dict] = {"admin": {}, "professor": {}, "student": {}}
        for uname, data in users.items():
            role = data.get("role", "student")
            by_role.setdefault(role, {})[uname] = data

        col1, col2, col3 = st.columns(3)
        for col, (role, label) in zip([col1, col2, col3], [("admin", "Administrators"), ("professor", "Professors"), ("student", "Students")]):
            col.markdown(f"#### {label}")
            group = by_role.get(role, {})
            col.markdown(f"**{len(group)} user(s)**")
            for uname, data in list(group.items())[:10]:
                col.write(f"- {data.get('name', uname)} (@{uname})")
            if len(group) > 10:
                col.caption(f"... and {len(group) - 10} more")

        st.markdown("---")
        st.markdown("#### Role Permissions Reference")

        permissions_data = {
            "Permission": ["View Content", "Submit Feedback", "Post Comments", "Create Articles",
                           "Manage Own Articles", "Review Articles", "Moderate Comments", "Manage Users", "View Analytics"],
            "Student": ["Yes", "Yes", "Yes", "No", "No", "No", "No", "No", "No"],
            "Professor": ["Yes", "Yes", "Yes", "Yes", "Yes", "No", "No", "No", "Yes"],
            "Admin": ["Yes", "Yes", "Yes", "Yes", "Yes", "Yes", "Yes", "Yes", "Yes"],
        }
        st.dataframe(pd.DataFrame(permissions_data), use_container_width=True, hide_index=True)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _log_action(self, admin_username: str, action: str, target_username: str, details: str) -> None:
        try:
            self.db_manager.execute_update(
                "INSERT INTO user_activity (username, action, target_type, target_id, details) VALUES (?, ?, 'user', ?, ?)",
                (admin_username, action, target_username, details),
            )
        except Exception:
            pass


def get_user_management_system(db_manager: DatabaseManager, auth_manager: AuthManager) -> UserManagementSystem:
    return UserManagementSystem(db_manager, auth_manager)
