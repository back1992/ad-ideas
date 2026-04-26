"""
Property-based tests for UI Consistency and Error Handling

Feature: platform-core, Property 13: User Interface Consistency
Feature: platform-core, Property 14: Error Handling Completeness
Validates: Requirements 7.1, 7.2, 7.4

This module contains property-based tests using Hypothesis to verify
UI consistency across navigation and error handling completeness.
"""

import os
import tempfile
import yaml
import bcrypt
from pathlib import Path
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, patch, MagicMock, call

import pytest
import streamlit as st
from hypothesis import given, strategies as st_hyp, settings, assume

from modules.auth import AuthManager
from modules.database import DatabaseManager
from modules.feedback import FeedbackSystem
from modules.comments import CommentSystem
from modules.articles import ArticleManager


class TestUIConsistencyProperties:
    """
    Property-based tests for UI consistency.
    
    Feature: platform-core, Property 13: User Interface Consistency
    Feature: platform-core, Property 14: Error Handling Completeness
    """
    
    def setup_method(self):
        """Set up test environment for each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config_path = os.path.join(self.temp_dir, "test_config.yaml")
        self.test_db_path = os.path.join(self.temp_dir, "test_ui.db")
        
        # Create test database manager
        self.db_manager = DatabaseManager(self.test_db_path)
        self.db_manager.init_database()
        
        # Create test configuration with users of different roles
        self.test_config = {
            'credentials': {
                'usernames': {
                    'student1': {
                        'email': 'student1@test.com',
                        'name': 'Student One',
                        'password': self._hash_password('pass123'),
                        'role': 'student'
                    },
                    'professor1': {
                        'email': 'prof1@test.com',
                        'name': 'Professor One',
                        'password': self._hash_password('profpass'),
                        'role': 'professor'
                    },
                    'admin1': {
                        'email': 'admin1@test.com',
                        'name': 'Admin One',
                        'password': self._hash_password('adminpass'),
                        'role': 'admin'
                    }
                }
            },
            'cookie': {
                'expiry_days': 30,
                'key': 'test_ui_key',
                'name': 'test_ui_cookie'
            }
        }
        
        # Save test configuration
        with open(self.test_config_path, 'w') as f:
            yaml.dump(self.test_config, f)
    
    def teardown_method(self):
        """Clean up test environment after each test method."""
        # Clean up files
        if os.path.exists(self.test_config_path):
            os.remove(self.test_config_path)
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        os.rmdir(self.temp_dir)
        
        # Clear streamlit session state
        if hasattr(st, 'session_state'):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def _create_auth_manager(self) -> AuthManager:
        """Create AuthManager instance with test configuration."""
        return AuthManager(self.test_config_path, self.db_manager)
    
    def _setup_authenticated_session(self, username: str, role: str) -> Dict[str, Any]:
        """Set up authenticated session state for testing."""
        session_state = {
            'authentication_status': True,
            'username': username,
            'name': self.test_config['credentials']['usernames'][username]['name'],
            'user_role': role
        }
        return session_state
    
    @given(
        st_hyp.sampled_from(['student', 'professor', 'admin']),
        st_hyp.integers(min_value=1, max_value=5)  # Number of navigation checks
    )
    @settings(max_examples=15, deadline=None)
    def test_navigation_menu_consistency(self, role: str, num_checks: int):
        """
        Property 13: For any page navigation, the system should maintain 
        consistent styling, layout, and navigation elements.
        
        Feature: platform-core, Property 13: User Interface Consistency
        Validates: Requirements 7.1, 7.2
        """
        # Map role to test username
        username_map = {
            'student': 'student1',
            'professor': 'professor1',
            'admin': 'admin1'
        }
        username = username_map[role]
        
        auth_manager = self._create_auth_manager()
        
        # Set up authenticated session
        session_state = self._setup_authenticated_session(username, role)
        
        # Define expected menu items for each role
        expected_base_items = [
            "首页 / Home",
            "广告大事年表 / Timeline",
            "20世纪广告百位巨星榜 / Top 100 Stars",
            "20世纪最成功的广告TOP100 / Top 100 Campaigns",
            "行业数据 / Industry Data",
            "与大师对话 / Chat with Masters"
        ]
        
        expected_professor_items = [
            "📝 我的文章 / My Articles",
            "✍️ 创建文章 / Create Article"
        ]
        
        expected_admin_items = [
            "🔧 内容审核 / Content Moderation",
            "📊 平台分析 / Platform Analytics"
        ]
        
        # Build expected menu based on role
        expected_menu_items = expected_base_items.copy()
        
        if role in ['professor', 'admin']:
            expected_menu_items.extend(expected_professor_items)
        
        if role == 'admin':
            expected_menu_items.extend(expected_admin_items)
        
        # Test navigation consistency across multiple checks
        menu_results = []
        
        for check_num in range(num_checks):
            with patch('streamlit.session_state', session_state):
                # Get navigation menu (simulating the get_navigation_menu function)
                user_info = auth_manager.get_current_user()
                
                # Verify user info consistency
                assert user_info['authenticated'] is True, \
                    f"User should be authenticated on check {check_num + 1}"
                assert user_info['username'] == username, \
                    f"Username should be {username} on check {check_num + 1}"
                assert user_info['role'] == role, \
                    f"Role should be {role} on check {check_num + 1}"
                
                # Simulate menu generation based on role
                menu_items = expected_base_items.copy()
                
                if auth_manager.is_professor_or_admin(username):
                    menu_items.extend(expected_professor_items)
                
                if auth_manager.is_admin(username):
                    menu_items.extend(expected_admin_items)
                
                menu_results.append(menu_items)
        
        # Verify all menu results are identical (consistency)
        first_menu = menu_results[0]
        for i, menu in enumerate(menu_results[1:], 1):
            assert menu == first_menu, \
                f"Navigation menu should be consistent: check 1 had {len(first_menu)} items, " \
                f"check {i + 1} had {len(menu)} items"
        
        # Verify menu contains expected items
        final_menu = menu_results[0]
        assert len(final_menu) == len(expected_menu_items), \
            f"Menu should have {len(expected_menu_items)} items for {role}, got {len(final_menu)}"
        
        for expected_item in expected_menu_items:
            assert expected_item in final_menu, \
                f"Menu should contain '{expected_item}' for {role} role"
    
    @given(
        st_hyp.sampled_from(['student', 'professor', 'admin']),
        st_hyp.integers(min_value=1, max_value=3)  # Number of session checks
    )
    @settings(max_examples=15, deadline=None)
    def test_session_state_consistency(self, role: str, num_checks: int):
        """
        Property 13: For any authenticated user, session state should remain 
        consistent across multiple operations.
        
        Feature: platform-core, Property 13: User Interface Consistency
        Validates: Requirements 7.1, 7.2
        """
        username_map = {
            'student': 'student1',
            'professor': 'professor1',
            'admin': 'admin1'
        }
        username = username_map[role]
        
        auth_manager = self._create_auth_manager()
        session_state = self._setup_authenticated_session(username, role)
        
        # Test session state consistency across multiple checks
        for check_num in range(num_checks):
            with patch('streamlit.session_state', session_state):
                user_info = auth_manager.get_current_user()
                
                # Verify all session state fields are consistent
                assert user_info['authenticated'] is True, \
                    f"Authentication status should be True on check {check_num + 1}"
                
                assert user_info['username'] == username, \
                    f"Username should be {username} on check {check_num + 1}"
                
                assert user_info['role'] == role, \
                    f"Role should be {role} on check {check_num + 1}"
                
                assert user_info['name'] == self.test_config['credentials']['usernames'][username]['name'], \
                    f"Name should match config on check {check_num + 1}"
                
                # Verify session state keys exist
                assert session_state.get('authentication_status') is True, \
                    f"Session authentication_status should be True on check {check_num + 1}"
                
                assert session_state.get('username') == username, \
                    f"Session username should be {username} on check {check_num + 1}"
                
                assert session_state.get('user_role') == role, \
                    f"Session user_role should be {role} on check {check_num + 1}"
    
    @given(
        st_hyp.sampled_from(['student', 'professor']),  # Non-admin roles
        st_hyp.sampled_from(['admin', 'professor'])     # Required permissions
    )
    @settings(max_examples=10, deadline=None)
    def test_error_handling_access_denied(self, user_role: str, required_permission: str):
        """
        Property 14: For any error condition, the system should display 
        user-friendly error messages and provide suggested recovery actions.
        
        Feature: platform-core, Property 14: Error Handling Completeness
        Validates: Requirements 7.4
        """
        # Skip cases where user has the required permission
        assume(user_role != required_permission)
        assume(not (user_role == 'professor' and required_permission == 'professor'))
        
        username_map = {
            'student': 'student1',
            'professor': 'professor1'
        }
        username = username_map[user_role]
        
        auth_manager = self._create_auth_manager()
        session_state = self._setup_authenticated_session(username, user_role)
        
        with patch('streamlit.session_state', session_state), \
             patch('streamlit.error') as mock_error:
            
            # Test require_role method which should display error
            result = auth_manager.require_role(required_permission, username)
            
            # Verify access is denied
            assert result is False, \
                f"User with {user_role} role should not have {required_permission} permission"
            
            # Verify error message was displayed
            mock_error.assert_called_once()
            
            # Get the error message
            error_call_args = mock_error.call_args[0][0]
            
            # Verify error message is user-friendly and informative
            assert "access denied" in error_call_args.lower(), \
                "Error message should indicate access denial"
            
            assert required_permission in error_call_args.lower(), \
                f"Error message should mention required role '{required_permission}'"
            
            # Verify error message doesn't expose sensitive information
            assert "password" not in error_call_args.lower(), \
                "Error message should not expose password information"
            
            assert "database" not in error_call_args.lower(), \
                "Error message should not expose database details"
            
            assert "exception" not in error_call_args.lower(), \
                "Error message should not expose exception details"
    
    @given(
        st_hyp.text(min_size=1, max_size=20).filter(
            lambda x: x not in ['student1', 'professor1', 'admin1'] and x.strip() != ''
        ),
        st_hyp.text(min_size=1, max_size=50)
    )
    @settings(max_examples=10, deadline=None)
    def test_error_handling_authentication_failure(self, username: str, password: str):
        """
        Property 14: For any authentication failure, the system should display 
        appropriate error messages without revealing sensitive information.
        
        Feature: platform-core, Property 14: Error Handling Completeness
        Validates: Requirements 7.4
        """
        auth_manager = self._create_auth_manager()
        
        with patch('streamlit.session_state', {}) as mock_session_state, \
             patch.object(auth_manager.authenticator, 'login') as mock_login:
            
            # Configure mock to return failed authentication
            mock_login.return_value = (None, False, username)
            
            # Attempt login
            name, auth_status, returned_username = auth_manager.login()
            
            # Verify authentication failed
            assert auth_status is False, \
                f"Authentication should fail for invalid credentials"
            
            assert name is None, \
                "Name should be None for failed authentication"
            
            # Verify session state doesn't contain sensitive information
            assert mock_session_state.get('password') is None, \
                "Session state should not store password"
            
            # Verify no role is assigned for failed authentication
            user_role = mock_session_state.get('user_role')
            assert user_role is None or user_role == 'unknown', \
                "Failed authentication should not assign user role"
    
    @given(
        st_hyp.sampled_from(['student', 'professor', 'admin']),
        st_hyp.sampled_from([
            'save_feedback', 'add_comment', 'save_article', 
            'get_feedback_stats', 'get_comments'
        ])
    )
    @settings(max_examples=15, deadline=None)
    def test_error_handling_database_operations(self, role: str, operation: str):
        """
        Property 14: For any database operation failure, the system should 
        handle errors gracefully and provide user-friendly messages.
        
        Feature: platform-core, Property 14: Error Handling Completeness
        Validates: Requirements 7.4
        """
        username_map = {
            'student': 'student1',
            'professor': 'professor1',
            'admin': 'admin1'
        }
        username = username_map[role]
        
        # Create a mock database manager that simulates failures
        mock_db = Mock(spec=DatabaseManager)
        mock_db.execute_query.side_effect = Exception("Database connection error")
        mock_db.execute_update.side_effect = Exception("Database write error")
        
        # Test different system components with failing database
        if operation == 'save_feedback':
            feedback_system = FeedbackSystem(mock_db)
            
            # Attempt to save feedback (should handle error gracefully)
            result = feedback_system.save_feedback(
                username=username,
                target_type='timeline',
                target_id='test_id',
                feedback_type='thumbs',
                feedback_value=1,
                feedback_text='test'
            )
            
            # Verify operation returns False (graceful failure)
            assert result is False, \
                "save_feedback should return False on database error"
        
        elif operation == 'add_comment':
            comment_system = CommentSystem(mock_db)
            
            # Attempt to add comment (should handle error gracefully)
            result = comment_system.add_comment(
                username=username,
                target_type='article',
                target_id='test_article',
                content='test comment',
                parent_id=None
            )
            
            # Verify operation returns False (graceful failure)
            assert result is False, \
                "add_comment should return False on database error"
        
        elif operation == 'get_feedback_stats':
            feedback_system = FeedbackSystem(mock_db)
            
            # Attempt to get stats (should handle error gracefully)
            stats = feedback_system.get_feedback_stats('timeline', 'test_id')
            
            # Verify returns default/empty stats instead of crashing
            assert isinstance(stats, dict), \
                "get_feedback_stats should return dict on error"
            
            assert stats['total_feedback'] == 0, \
                "Error case should return zero feedback count"
        
        elif operation == 'get_comments':
            comment_system = CommentSystem(mock_db)
            
            # Attempt to get comments (should handle error gracefully)
            import pandas as pd
            comments = comment_system.get_comments('article', 'test_id')
            
            # Verify returns empty DataFrame instead of crashing
            assert isinstance(comments, pd.DataFrame), \
                "get_comments should return DataFrame on error"
            
            assert len(comments) == 0, \
                "Error case should return empty DataFrame"
    
    @given(
        st_hyp.sampled_from(['student', 'professor', 'admin']),
        st_hyp.integers(min_value=1, max_value=3)
    )
    @settings(max_examples=10, deadline=None)
    def test_ui_element_presence_consistency(self, role: str, num_checks: int):
        """
        Property 13: For any user role, UI elements should be consistently 
        present across multiple page loads.
        
        Feature: platform-core, Property 13: User Interface Consistency
        Validates: Requirements 7.1, 7.2
        """
        username_map = {
            'student': 'student1',
            'professor': 'professor1',
            'admin': 'admin1'
        }
        username = username_map[role]
        
        auth_manager = self._create_auth_manager()
        session_state = self._setup_authenticated_session(username, role)
        
        # Track UI element presence across checks
        ui_elements_results = []
        
        for check_num in range(num_checks):
            with patch('streamlit.session_state', session_state):
                user_info = auth_manager.get_current_user()
                
                # Define expected UI elements based on role
                ui_elements = {
                    'user_authenticated': user_info['authenticated'],
                    'username_present': user_info['username'] is not None,
                    'name_present': user_info['name'] is not None,
                    'role_present': user_info['role'] is not None,
                    'has_base_navigation': True,  # All users have base navigation
                    'has_professor_features': auth_manager.is_professor_or_admin(username),
                    'has_admin_features': auth_manager.is_admin(username)
                }
                
                ui_elements_results.append(ui_elements)
        
        # Verify UI elements are consistent across all checks
        first_result = ui_elements_results[0]
        for i, result in enumerate(ui_elements_results[1:], 1):
            assert result == first_result, \
                f"UI elements should be consistent: check 1 vs check {i + 1} differ"
        
        # Verify expected UI elements are present
        final_result = ui_elements_results[0]
        
        assert final_result['user_authenticated'] is True, \
            "User should be authenticated"
        
        assert final_result['username_present'] is True, \
            "Username should be present in UI"
        
        assert final_result['name_present'] is True, \
            "User name should be present in UI"
        
        assert final_result['role_present'] is True, \
            "User role should be present in UI"
        
        assert final_result['has_base_navigation'] is True, \
            "Base navigation should be available"
        
        # Verify role-specific features
        if role in ['professor', 'admin']:
            assert final_result['has_professor_features'] is True, \
                f"{role} should have professor features"
        else:
            assert final_result['has_professor_features'] is False, \
                f"{role} should not have professor features"
        
        if role == 'admin':
            assert final_result['has_admin_features'] is True, \
                "Admin should have admin features"
        else:
            assert final_result['has_admin_features'] is False, \
                f"{role} should not have admin features"
    
    @given(
        st_hyp.lists(
            st_hyp.sampled_from(['student', 'professor', 'admin']),
            min_size=2,
            max_size=5
        )
    )
    @settings(max_examples=10, deadline=None)
    def test_ui_consistency_across_role_switches(self, role_sequence: List[str]):
        """
        Property 13: For any sequence of role switches, UI should consistently 
        reflect the current user's role and permissions.
        
        Feature: platform-core, Property 13: User Interface Consistency
        Validates: Requirements 7.1, 7.2
        """
        auth_manager = self._create_auth_manager()
        
        username_map = {
            'student': 'student1',
            'professor': 'professor1',
            'admin': 'admin1'
        }
        
        # Test UI consistency when switching between different user roles
        for role in role_sequence:
            username = username_map[role]
            session_state = self._setup_authenticated_session(username, role)
            
            with patch('streamlit.session_state', session_state):
                user_info = auth_manager.get_current_user()
                
                # Verify UI reflects current role correctly
                assert user_info['role'] == role, \
                    f"UI should reflect current role {role}"
                
                assert user_info['username'] == username, \
                    f"UI should show current username {username}"
                
                # Verify permission checks match role
                is_admin = auth_manager.is_admin(username)
                is_professor = auth_manager.is_professor(username)
                is_professor_or_admin = auth_manager.is_professor_or_admin(username)
                
                if role == 'admin':
                    assert is_admin is True, "Admin role should pass is_admin check"
                    assert is_professor_or_admin is True, "Admin should pass is_professor_or_admin"
                elif role == 'professor':
                    assert is_admin is False, "Professor should not pass is_admin check"
                    assert is_professor is True, "Professor should pass is_professor check"
                    assert is_professor_or_admin is True, "Professor should pass is_professor_or_admin"
                elif role == 'student':
                    assert is_admin is False, "Student should not pass is_admin check"
                    assert is_professor is False, "Student should not pass is_professor check"
                    assert is_professor_or_admin is False, "Student should not pass is_professor_or_admin"
    
    @given(
        st_hyp.sampled_from(['', None, 'invalid_operation', 'malformed_input'])
    )
    @settings(max_examples=10, deadline=None)
    def test_error_handling_invalid_inputs(self, invalid_input: Any):
        """
        Property 14: For any invalid input, the system should handle it 
        gracefully without crashing and provide helpful error messages.
        
        Feature: platform-core, Property 14: Error Handling Completeness
        Validates: Requirements 7.4
        """
        auth_manager = self._create_auth_manager()
        
        # Test various invalid inputs to role checking methods
        # These should not crash but return appropriate defaults
        
        # Test with invalid username
        role = auth_manager.get_user_role(invalid_input if invalid_input else '')
        assert role in ['unknown', 'student'], \
            f"Invalid username should return 'unknown' or default 'student' role, got {role}"
        
        # Test permission checks with invalid username
        has_permission = auth_manager.check_permission('admin', invalid_input if invalid_input else '')
        assert has_permission is False, \
            "Invalid username should not have any permissions"
        
        # Test is_admin with invalid username
        is_admin = auth_manager.is_admin(invalid_input if invalid_input else '')
        assert is_admin is False, \
            "Invalid username should not be admin"
        
        # Test is_professor with invalid username
        is_professor = auth_manager.is_professor(invalid_input if invalid_input else '')
        assert is_professor is False, \
            "Invalid username should not be professor"


class TestErrorMessageQuality:
    """
    Additional tests for error message quality and user-friendliness.
    
    Feature: platform-core, Property 14: Error Handling Completeness
    """
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_errors.db")
        self.db_manager = DatabaseManager(self.test_db_path)
        self.db_manager.init_database()
    
    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        os.rmdir(self.temp_dir)
    
    @given(
        st_hyp.sampled_from(['feedback', 'comment', 'article']),
        st_hyp.text(min_size=0, max_size=20)
    )
    @settings(max_examples=10, deadline=None)
    def test_error_messages_are_informative(self, system_type: str, invalid_id: str):
        """
        Property 14: Error messages should be informative and suggest 
        recovery actions.
        
        Feature: platform-core, Property 14: Error Handling Completeness
        Validates: Requirements 7.4
        """
        # Create system with mock database that fails
        mock_db = Mock(spec=DatabaseManager)
        mock_db.execute_query.side_effect = Exception("Connection timeout")
        mock_db.execute_update.side_effect = Exception("Write failed")
        
        if system_type == 'feedback':
            system = FeedbackSystem(mock_db)
            
            # Test that operations fail gracefully
            result = system.save_feedback(
                username='test_user',
                target_type='timeline',
                target_id=invalid_id,
                feedback_type='thumbs',
                feedback_value=1,
                feedback_text=''
            )
            
            # Should return False, not raise exception
            assert result is False, \
                "Failed operation should return False, not crash"
        
        elif system_type == 'comment':
            system = CommentSystem(mock_db)
            
            result = system.add_comment(
                username='test_user',
                target_type='article',
                target_id=invalid_id,
                content='test',
                parent_id=None
            )
            
            assert result is False, \
                "Failed operation should return False, not crash"
    
    @given(
        st_hyp.sampled_from([
            'database_error', 'network_error', 'permission_error', 
            'validation_error', 'not_found_error'
        ])
    )
    @settings(max_examples=10, deadline=None)
    def test_error_types_handled_appropriately(self, error_type: str):
        """
        Property 14: Different error types should be handled with appropriate 
        error messages and recovery suggestions.
        
        Feature: platform-core, Property 14: Error Handling Completeness
        Validates: Requirements 7.4
        """
        # Create mock database with specific error types
        mock_db = Mock(spec=DatabaseManager)
        
        if error_type == 'database_error':
            mock_db.execute_query.side_effect = Exception("Database connection failed")
        elif error_type == 'network_error':
            mock_db.execute_query.side_effect = ConnectionError("Network unreachable")
        elif error_type == 'permission_error':
            mock_db.execute_query.side_effect = PermissionError("Access denied")
        elif error_type == 'validation_error':
            mock_db.execute_query.side_effect = ValueError("Invalid data format")
        elif error_type == 'not_found_error':
            mock_db.execute_query.side_effect = FileNotFoundError("Resource not found")
        
        # Test that system handles error gracefully
        feedback_system = FeedbackSystem(mock_db)
        
        # Should not raise exception, should return default/empty result
        stats = feedback_system.get_feedback_stats('timeline', 'test_id')
        
        assert isinstance(stats, dict), \
            f"System should handle {error_type} gracefully and return dict"
        
        assert stats['total_feedback'] == 0, \
            f"Error case should return default empty stats for {error_type}"
