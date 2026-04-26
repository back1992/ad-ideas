"""
Property-based tests for ActivityLogger

Feature: platform-core, Property 15: Activity Logging Completeness
Validates: Requirements 9.1

This module contains property-based tests using Hypothesis to verify
activity logging completeness, ensuring all user actions are properly
logged with attribution, timestamp, and action details.
"""

import os
import tempfile
import re
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

import pytest
import pandas as pd
from hypothesis import given, strategies as st, settings, assume
from hypothesis.stateful import RuleBasedStateMachine, rule, initialize

from modules.database import DatabaseManager
from modules.activity import ActivityLogger


class TestActivityLoggingCompleteness:
    """
    Property-based tests for activity logging completeness.
    
    Feature: platform-core, Property 15: Activity Logging Completeness
    """
    
    def setup_method(self):
        """Set up test environment for each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_activity.db")
        
        # Create test database manager with isolated test database
        self.db_manager = DatabaseManager(self.test_db_path)
        self.db_manager.init_database()
        
        # Verify we're using a fresh database
        count_query = "SELECT COUNT(*) as count FROM user_activity"
        result = self.db_manager.execute_query(count_query)
        assert result.iloc[0]['count'] == 0, "Test database should start empty"
        
        # Create activity logger
        self.activity_logger = ActivityLogger(self.db_manager)
    
    def teardown_method(self):
        """Clean up test environment after each test method."""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        os.rmdir(self.temp_dir)
    
    @given(
        username=st.text(min_size=1, max_size=50).filter(lambda x: x.strip() != ''),
        action=st.sampled_from([
            'login', 'logout', 'feedback_submitted', 'comment_posted', 
            'comment_reply', 'article_create', 'article_edit', 'article_publish',
            'article_delete', 'article_view', 'content_viewed', 
            'moderation_approve', 'moderation_reject'
        ]),
        target_type=st.one_of(st.none(), st.sampled_from(['article', 'timeline', 'figures', 'campaigns'])),
        target_id=st.one_of(st.none(), st.text(min_size=1, max_size=20)),
        details=st.one_of(st.none(), st.text(min_size=0, max_size=200))
    )
    @settings(max_examples=5, deadline=None)
    def test_activity_logging_completeness(
        self, 
        username: str, 
        action: str,
        target_type: Optional[str],
        target_id: Optional[str],
        details: Optional[str]
    ):
        """
        Property 15: For any user action, the system should log the activity 
        with proper attribution, timestamp, and action details.
        
        Feature: platform-core, Property 15: Activity Logging Completeness
        Validates: Requirements 9.1
        """
        # Get initial count
        initial_count_query = "SELECT COUNT(*) as count FROM user_activity"
        initial_result = self.db_manager.execute_query(initial_count_query)
        initial_count = initial_result.iloc[0]['count']
        
        # Log the activity
        success = self.activity_logger.log_activity(
            username=username,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details
        )
        
        # Verify logging succeeded
        assert success is True, f"Activity logging should succeed for valid inputs"
        
        # Verify activity was stored
        final_result = self.db_manager.execute_query(initial_count_query)
        final_count = final_result.iloc[0]['count']
        assert final_count == initial_count + 1, \
            f"Activity count should increase by 1, was {initial_count}, now {final_count}"
        
        # Retrieve the logged activity (get the most recent one after our log call)
        query = """
            SELECT * FROM user_activity 
            WHERE username = ? AND action = ?
            AND id = (SELECT MAX(id) FROM user_activity WHERE username = ? AND action = ?)
        """
        result = self.db_manager.execute_query(query, (username, action, username, action))
        
        assert not result.empty, "Should retrieve the logged activity"
        
        logged_activity = result.iloc[0]
        
        # Verify proper attribution
        assert logged_activity['username'] == username, \
            f"Username should be {username}, got {logged_activity['username']}"
        
        # Verify action is logged correctly
        assert logged_activity['action'] == action, \
            f"Action should be {action}, got {logged_activity['action']}"
        
        # Verify target_type is logged correctly
        if target_type is not None:
            assert logged_activity['target_type'] == target_type, \
                f"Target type should be {target_type}, got {logged_activity['target_type']}"
        else:
            assert pd.isna(logged_activity['target_type']) or logged_activity['target_type'] is None, \
                f"Target type should be None/NULL, got {logged_activity['target_type']}"
        
        # Verify target_id is logged correctly
        if target_id is not None and target_id.strip() != '':
            assert logged_activity['target_id'] == target_id, \
                f"Target ID should be {target_id}, got {logged_activity['target_id']}"
        else:
            assert pd.isna(logged_activity['target_id']) or logged_activity['target_id'] is None, \
                f"Target ID should be None/NULL, got {logged_activity['target_id']}"
        
        # Verify timestamp exists and is recent
        assert 'timestamp' in logged_activity.index, "Timestamp should be present"
        assert logged_activity['timestamp'] is not None, "Timestamp should not be None"
        
        # Parse timestamp and verify it's recent (within last minute)
        # Note: SQLite CURRENT_TIMESTAMP uses UTC, so we need to compare with UTC time
        timestamp_str = logged_activity['timestamp']
        try:
            # SQLite returns timestamps as strings in format 'YYYY-MM-DD HH:MM:SS'
            from datetime import timezone
            logged_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
            current_time = datetime.now(timezone.utc)
            time_diff = abs((current_time - logged_time).total_seconds())
            
            # Should be logged within the last 60 seconds
            assert time_diff < 60, \
                f"Timestamp should be recent, but was {time_diff} seconds ago"
        except (ValueError, TypeError) as e:
            pytest.fail(f"Timestamp format invalid: {timestamp_str}, error: {e}")
        
        # Verify details are logged (may be sanitized)
        if details is not None and details.strip() != '':
            # Details should be present (possibly sanitized)
            assert 'details' in logged_activity.index, "Details field should be present"
            # Details may be None if sanitization removed everything, or may be sanitized
            logged_details = logged_activity['details']
            if logged_details is not None and not pd.isna(logged_details):
                # Verify details don't exceed max length (500 chars + "...")
                assert len(logged_details) <= 503, \
                    f"Details should be truncated to max 503 chars, got {len(logged_details)}"
    
    @given(
        username=st.text(min_size=1, max_size=50).filter(lambda x: x.strip() != ''),
        success=st.booleans()
    )
    @settings(max_examples=5, deadline=None)
    def test_login_activity_logging(self, username: str, success: bool):
        """
        Property: For any login attempt, the system should log the activity
        with success/failure indication.
        
        Feature: platform-core, Property 15: Activity Logging Completeness
        Validates: Requirements 9.1
        """
        # Log login activity
        result = self.activity_logger.log_login(username, success)
        
        assert result is True, "Login logging should succeed"
        
        # Verify activity was logged
        expected_action = 'login' if success else 'login_failed'
        query = """
            SELECT * FROM user_activity 
            WHERE username = ? AND action = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """
        logged = self.db_manager.execute_query(query, (username, expected_action))
        
        assert not logged.empty, f"Login activity should be logged for {username}"
        assert logged.iloc[0]['username'] == username
        assert logged.iloc[0]['action'] == expected_action
        assert logged.iloc[0]['details'] is not None
    
    @given(
        username=st.text(min_size=1, max_size=50).filter(lambda x: x.strip() != ''),
        target_type=st.sampled_from(['article', 'timeline', 'figures', 'campaigns']),
        target_id=st.text(min_size=1, max_size=20),
        feedback_type=st.sampled_from(['thumbs', 'stars', 'faces'])
    )
    @settings(max_examples=5, deadline=None)
    def test_feedback_activity_logging(
        self, 
        username: str, 
        target_type: str,
        target_id: str,
        feedback_type: str
    ):
        """
        Property: For any feedback submission, the system should log the activity
        with target information and feedback type.
        
        Feature: platform-core, Property 15: Activity Logging Completeness
        Validates: Requirements 9.1
        """
        # Log feedback activity
        result = self.activity_logger.log_feedback(username, target_type, target_id, feedback_type)
        
        assert result is True, "Feedback logging should succeed"
        
        # Verify activity was logged
        query = """
            SELECT * FROM user_activity 
            WHERE username = ? AND action = 'feedback_submitted'
            AND target_type = ? AND target_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """
        logged = self.db_manager.execute_query(query, (username, target_type, target_id))
        
        assert not logged.empty, f"Feedback activity should be logged"
        assert logged.iloc[0]['username'] == username
        assert logged.iloc[0]['action'] == 'feedback_submitted'
        assert logged.iloc[0]['target_type'] == target_type
        assert logged.iloc[0]['target_id'] == target_id
        assert feedback_type in logged.iloc[0]['details']
    
    @given(
        username=st.text(min_size=1, max_size=50).filter(lambda x: x.strip() != ''),
        target_type=st.sampled_from(['article', 'timeline', 'figures', 'campaigns']),
        target_id=st.text(min_size=1, max_size=20),
        is_reply=st.booleans()
    )
    @settings(max_examples=5, deadline=None)
    def test_comment_activity_logging(
        self, 
        username: str, 
        target_type: str,
        target_id: str,
        is_reply: bool
    ):
        """
        Property: For any comment posting, the system should log the activity
        with target information and reply status.
        
        Feature: platform-core, Property 15: Activity Logging Completeness
        Validates: Requirements 9.1
        """
        # Log comment activity
        result = self.activity_logger.log_comment(username, target_type, target_id, is_reply)
        
        assert result is True, "Comment logging should succeed"
        
        # Verify activity was logged
        expected_action = 'comment_reply' if is_reply else 'comment_posted'
        query = """
            SELECT * FROM user_activity 
            WHERE username = ? AND action = ?
            AND target_type = ? AND target_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """
        logged = self.db_manager.execute_query(query, (username, expected_action, target_type, target_id))
        
        assert not logged.empty, f"Comment activity should be logged"
        assert logged.iloc[0]['username'] == username
        assert logged.iloc[0]['action'] == expected_action
        assert logged.iloc[0]['target_type'] == target_type
        assert logged.iloc[0]['target_id'] == target_id
    
    @given(
        username=st.text(min_size=1, max_size=50).filter(lambda x: x.strip() != ''),
        action=st.sampled_from(['create', 'edit', 'publish', 'delete', 'view']),
        article_id=st.one_of(st.none(), st.integers(min_value=1, max_value=10000)),
        article_title=st.one_of(st.none(), st.text(min_size=1, max_size=100))
    )
    @settings(max_examples=5, deadline=None)
    def test_article_activity_logging(
        self, 
        username: str, 
        action: str,
        article_id: Optional[int],
        article_title: Optional[str]
    ):
        """
        Property: For any article action, the system should log the activity
        with article information.
        
        Feature: platform-core, Property 15: Activity Logging Completeness
        Validates: Requirements 9.1
        """
        # Log article activity
        result = self.activity_logger.log_article_action(username, action, article_id, article_title)
        
        assert result is True, "Article activity logging should succeed"
        
        # Verify activity was logged
        expected_action = f'article_{action}'
        query = """
            SELECT * FROM user_activity 
            WHERE username = ? AND action = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """
        logged = self.db_manager.execute_query(query, (username, expected_action))
        
        assert not logged.empty, f"Article activity should be logged"
        assert logged.iloc[0]['username'] == username
        assert logged.iloc[0]['action'] == expected_action
        
        if article_id is not None:
            assert logged.iloc[0]['target_id'] == str(article_id)
            assert logged.iloc[0]['target_type'] == 'article'
    
    @given(
        details=st.text(min_size=1, max_size=1000)
    )
    @settings(max_examples=5, deadline=None)
    def test_details_sanitization(self, details: str):
        """
        Property: For any activity details, sensitive information should be
        sanitized before storage.
        
        Feature: platform-core, Property 15: Activity Logging Completeness
        Validates: Requirements 9.1 (privacy compliance)
        """
        # Add some potentially sensitive data to details
        test_details = f"{details} test@email.com 555-123-4567"
        
        # Log activity with potentially sensitive details
        username = "test_user"
        action = "test_action"
        
        result = self.activity_logger.log_activity(
            username=username,
            action=action,
            details=test_details
        )
        
        assert result is True, "Activity logging should succeed"
        
        # Retrieve logged activity
        query = """
            SELECT details FROM user_activity 
            WHERE username = ? AND action = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """
        logged = self.db_manager.execute_query(query, (username, action))
        
        assert not logged.empty, "Activity should be logged"
        
        logged_details = logged.iloc[0]['details']
        
        if logged_details is not None and not pd.isna(logged_details):
            # Verify email addresses are sanitized
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails_found = re.findall(email_pattern, logged_details)
            assert len(emails_found) == 0, \
                f"Email addresses should be sanitized, found: {emails_found}"
            
            # Verify phone numbers are sanitized
            phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
            phones_found = re.findall(phone_pattern, logged_details)
            assert len(phones_found) == 0, \
                f"Phone numbers should be sanitized, found: {phones_found}"
            
            # Verify length limit is enforced (500 chars + "...")
            assert len(logged_details) <= 503, \
                f"Details should be truncated to max 503 chars, got {len(logged_details)}"
    
    @given(
        username=st.text(min_size=1, max_size=50).filter(lambda x: x.strip() != ''),
        num_actions=st.integers(min_value=1, max_value=20)
    )
    @settings(max_examples=5, deadline=None)
    def test_multiple_activities_logging(self, username: str, num_actions: int):
        """
        Property: For any sequence of user actions, all activities should be
        logged in order with correct timestamps.
        
        Feature: platform-core, Property 15: Activity Logging Completeness
        Validates: Requirements 9.1
        """
        actions = ['login', 'content_viewed', 'feedback_submitted', 'comment_posted', 'logout']
        
        # Log multiple activities
        for i in range(num_actions):
            action = actions[i % len(actions)]
            result = self.activity_logger.log_activity(
                username=username,
                action=action,
                details=f"Action {i+1}"
            )
            assert result is True, f"Activity {i+1} should be logged successfully"
        
        # Retrieve all logged activities for this user
        query = """
            SELECT * FROM user_activity 
            WHERE username = ?
            ORDER BY timestamp ASC
        """
        logged = self.db_manager.execute_query(query, (username,))
        
        # Verify all activities were logged
        assert len(logged) >= num_actions, \
            f"Should have at least {num_actions} activities logged, got {len(logged)}"
        
        # Verify timestamps are in order
        timestamps = logged['timestamp'].tolist()
        for i in range(len(timestamps) - 1):
            t1 = datetime.strptime(timestamps[i], '%Y-%m-%d %H:%M:%S')
            t2 = datetime.strptime(timestamps[i+1], '%Y-%m-%d %H:%M:%S')
            assert t1 <= t2, \
                f"Timestamps should be in chronological order: {timestamps[i]} should be <= {timestamps[i+1]}"
    
    @given(
        username=st.text(min_size=1, max_size=50).filter(lambda x: x.strip() != ''),
        action_filter=st.one_of(st.none(), st.sampled_from(['login', 'logout', 'feedback_submitted']))
    )
    @settings(max_examples=5, deadline=None)
    def test_activity_retrieval_completeness(self, username: str, action_filter: Optional[str]):
        """
        Property: For any user, all logged activities should be retrievable
        with optional filtering by action type.
        
        Feature: platform-core, Property 15: Activity Logging Completeness
        Validates: Requirements 9.1
        """
        # Log some activities
        test_actions = ['login', 'feedback_submitted', 'comment_posted', 'logout']
        for action in test_actions:
            self.activity_logger.log_activity(username, action)
        
        # Retrieve activities
        result = self.activity_logger.get_user_activity(username, limit=100, action_filter=action_filter)
        
        # Verify retrieval
        assert isinstance(result, pd.DataFrame), "Should return DataFrame"
        
        if action_filter:
            # Should only contain filtered action
            if not result.empty:
                assert all(result['action'] == action_filter), \
                    f"All actions should be {action_filter}"
        else:
            # Should contain all actions
            assert len(result) >= len(test_actions), \
                f"Should retrieve at least {len(test_actions)} activities"
        
        # Verify all retrieved activities have required fields
        if not result.empty:
            required_fields = ['username', 'action', 'timestamp']
            for field in required_fields:
                assert field in result.columns, f"Field {field} should be present"
                assert all(result[field].notna()), f"Field {field} should not have null values"


class ActivityLoggingStateMachine(RuleBasedStateMachine):
    """
    Stateful property-based testing for activity logging operations.
    
    Feature: platform-core, Property 15: Activity Logging Completeness
    """
    
    def __init__(self):
        super().__init__()
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "stateful_activity.db")
        self.db_manager = None
        self.activity_logger = None
        self.logged_activities = []
    
    @initialize()
    def setup_activity_logger(self):
        """Initialize activity logger."""
        self.db_manager = DatabaseManager(self.db_path)
        self.db_manager.init_database()
        self.activity_logger = ActivityLogger(self.db_manager)
    
    @rule(
        username=st.text(min_size=1, max_size=30).filter(lambda x: x.strip() != ''),
        action=st.sampled_from(['login', 'logout', 'feedback_submitted', 'comment_posted'])
    )
    def log_activity(self, username: str, action: str):
        """Rule: Log an activity."""
        result = self.activity_logger.log_activity(username, action)
        assert result is True, "Activity logging should succeed"
        
        # Track logged activity
        self.logged_activities.append((username, action))
        
        # Verify activity count matches
        query = "SELECT COUNT(*) as count FROM user_activity"
        count_result = self.db_manager.execute_query(query)
        actual_count = count_result.iloc[0]['count']
        
        assert actual_count == len(self.logged_activities), \
            f"Activity count should be {len(self.logged_activities)}, got {actual_count}"
    
    @rule(username=st.text(min_size=1, max_size=30).filter(lambda x: x.strip() != ''))
    def retrieve_user_activities(self, username: str):
        """Rule: Retrieve activities for a user."""
        result = self.activity_logger.get_user_activity(username)
        
        # Should return DataFrame
        assert isinstance(result, pd.DataFrame), "Should return DataFrame"
        
        # Count expected activities for this user
        expected_count = sum(1 for u, a in self.logged_activities if u == username)
        
        # Verify count matches
        assert len(result) == expected_count, \
            f"Should retrieve {expected_count} activities for {username}, got {len(result)}"
    
    def teardown(self):
        """Clean up test database."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)


# Stateful test class
TestActivityLoggingStateMachine = ActivityLoggingStateMachine.TestCase
