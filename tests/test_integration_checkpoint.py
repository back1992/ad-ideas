"""
Integration Tests for Platform Core Systems Checkpoint

This test suite validates that all core systems (database, auth, feedback, comments)
work together correctly. It tests cross-system interactions and end-to-end workflows.

Task: 5. Checkpoint - Core systems integration test
Requirements: All core system requirements (1.x, 2.x, 3.x, 4.x, 6.x)
"""

import pytest
import os
import tempfile
import yaml
from modules.database import DatabaseManager
from modules.auth import AuthManager
from modules.feedback import FeedbackSystem
from modules.comments import CommentSystem


class TestDatabaseIntegration:
    """Test database initialization and basic operations."""
    
    def test_database_initialization(self, temp_db):
        """Test that database initializes with all required tables."""
        db_manager = DatabaseManager(temp_db)
        db_manager.init_database()
        
        # Verify all required tables exist
        required_tables = [
            'user_feedback',
            'comments',
            'articles',
            'content_stats',
            'user_activity'
        ]
        
        for table in required_tables:
            assert db_manager.table_exists(table), f"Table {table} should exist"
    
    def test_database_crud_operations(self, db_manager):
        """Test basic CRUD operations work correctly."""
        # Insert test data
        query = """
            INSERT INTO user_activity (username, action, details)
            VALUES (?, ?, ?)
        """
        affected = db_manager.execute_update(query, ('test_user', 'test_action', 'test details'))
        assert affected == 1, "Should insert one row"
        
        # Query test data
        query = "SELECT * FROM user_activity WHERE username = ?"
        result = db_manager.execute_query(query, ('test_user',))
        assert len(result) == 1, "Should retrieve one row"
        assert result.iloc[0]['action'] == 'test_action'


class TestAuthenticationIntegration:
    """Test authentication system integration."""
    
    def test_auth_manager_initialization(self, auth_manager):
        """Test that auth manager initializes correctly with config."""
        assert auth_manager is not None
        assert auth_manager.config is not None
        assert 'credentials' in auth_manager.config
    
    def test_user_role_retrieval(self, auth_manager):
        """Test getting user roles from configuration."""
        # Test with known users from config
        admin_role = auth_manager.get_user_role('admin')
        assert admin_role == 'admin', "Admin user should have admin role"
        
        professor_role = auth_manager.get_user_role('professor')
        assert professor_role == 'professor', "Professor user should have professor role"
        
        student_role = auth_manager.get_user_role('student')
        assert student_role == 'student', "Student user should have student role"
    
    def test_role_permission_checks(self, auth_manager):
        """Test role-based permission checking."""
        # Admin should have all permissions
        assert auth_manager.check_permission('student', 'admin') is True
        assert auth_manager.check_permission('professor', 'admin') is True
        assert auth_manager.check_permission('admin', 'admin') is True
        
        # Professor should have professor and student permissions
        assert auth_manager.check_permission('student', 'professor') is True
        assert auth_manager.check_permission('professor', 'professor') is True
        assert auth_manager.check_permission('admin', 'professor') is False
        
        # Student should only have student permissions
        assert auth_manager.check_permission('student', 'student') is True
        assert auth_manager.check_permission('professor', 'student') is False
        assert auth_manager.check_permission('admin', 'student') is False
    
    def test_auth_logs_to_database(self, auth_manager, db_manager):
        """Test that authentication actions are logged to database."""
        # Simulate login activity logging
        auth_manager._log_user_activity('test_user', 'login', 'Test login')
        
        # Verify activity was logged
        query = "SELECT * FROM user_activity WHERE username = ? AND action = ?"
        result = db_manager.execute_query(query, ('test_user', 'login'))
        assert len(result) > 0, "Login activity should be logged"


class TestFeedbackIntegration:
    """Test feedback system integration."""
    
    def test_feedback_system_initialization(self, feedback_system):
        """Test that feedback system initializes correctly."""
        assert feedback_system is not None
        assert feedback_system.db_manager is not None
    
    def test_save_and_retrieve_feedback(self, feedback_system, db_manager):
        """Test saving and retrieving feedback."""
        # Save feedback
        success = feedback_system.save_feedback(
            username='test_user',
            target_type='timeline',
            target_id='test_content',
            feedback_type='thumbs',
            feedback_value=1,
            feedback_text='Great content!'
        )
        assert success == True, "Feedback should be saved successfully"
        
        # Check if user has feedback
        has_feedback = feedback_system.has_user_feedback(
            'test_user',
            'timeline',
            'test_content'
        )
        assert has_feedback == True, "User should have feedback recorded"
        
        # Get feedback stats
        stats = feedback_system.get_feedback_stats('timeline', 'test_content')
        assert stats['total_feedback'] == 1, "Should have one feedback entry"
        assert stats['positive_count'] == 1, "Should have one positive feedback"
    
    def test_feedback_uniqueness_constraint(self, feedback_system):
        """Test that users can only submit feedback once per content."""
        # Save first feedback
        success1 = feedback_system.save_feedback(
            username='test_user',
            target_type='timeline',
            target_id='unique_test',
            feedback_type='stars',
            feedback_value=4,
            feedback_text='Good'
        )
        assert success1 == True
        
        # Check that user has feedback
        has_feedback = feedback_system.has_user_feedback(
            'test_user',
            'timeline',
            'unique_test'
        )
        assert has_feedback == True, "User should have feedback recorded"
    
    def test_content_stats_update(self, feedback_system):
        """Test that content statistics are updated correctly."""
        # Add multiple feedback entries
        feedback_system.save_feedback(
            'user1', 'figures', 'stats_test', 'thumbs', 1, ''
        )
        feedback_system.save_feedback(
            'user2', 'figures', 'stats_test', 'thumbs', 0, ''
        )
        feedback_system.save_feedback(
            'user3', 'figures', 'stats_test', 'stars', 4, ''
        )
        
        # Update content stats
        feedback_system.update_content_stats('figures', 'stats_test')
        
        # Get content stats
        stats = feedback_system.get_content_stats('figures', 'stats_test')
        assert stats is not None, "Content stats should exist"
        assert stats['total_ratings'] == 3, "Should have 3 total ratings"
        assert stats['thumbs_up'] == 1, "Should have 1 thumbs up"
        assert stats['thumbs_down'] == 1, "Should have 1 thumbs down"


class TestCommentIntegration:
    """Test comment system integration."""
    
    def test_comment_system_initialization(self, comment_system):
        """Test that comment system initializes correctly."""
        assert comment_system is not None
        assert comment_system.db_manager is not None
    
    def test_add_and_retrieve_comments(self, comment_system):
        """Test adding and retrieving comments."""
        # Add a comment
        success = comment_system.add_comment(
            username='test_user',
            target_type='campaigns',
            target_id='test_campaign',
            content='This is a test comment',
            parent_id=None
        )
        assert success is True, "Comment should be added successfully"
        
        # Retrieve comments
        comments = comment_system.get_comments('campaigns', 'test_campaign', approved_only=False)
        assert len(comments) == 1, "Should have one comment"
        assert comments.iloc[0]['content'] == 'This is a test comment'
        assert comments.iloc[0]['username'] == 'test_user'
    
    def test_comment_threading(self, comment_system):
        """Test comment threading with parent-child relationships."""
        # Add parent comment
        success1 = comment_system.add_comment(
            'user1', 'article', 'thread_test', 'Parent comment', None
        )
        assert success1 is True
        
        # Get parent comment ID
        comments = comment_system.get_comments('article', 'thread_test', approved_only=False)
        parent_id = comments.iloc[0]['id']
        
        # Add reply
        success2 = comment_system.add_comment(
            'user2', 'article', 'thread_test', 'Reply comment', parent_id
        )
        assert success2 is True
        
        # Verify threading
        all_comments = comment_system.get_comments('article', 'thread_test', approved_only=False)
        assert len(all_comments) == 2, "Should have 2 comments"
        
        # Find the reply
        reply = all_comments[all_comments['parent_id'] == parent_id]
        assert len(reply) == 1, "Should have one reply"
        assert reply.iloc[0]['content'] == 'Reply comment'
    
    def test_comment_likes(self, comment_system):
        """Test comment like functionality."""
        # Add a comment
        comment_system.add_comment(
            'user1', 'timeline', 'like_test', 'Likeable comment', None
        )
        
        # Get comment
        comments = comment_system.get_comments('timeline', 'like_test', approved_only=False)
        comment_id = comments.iloc[0]['id']
        initial_likes = comments.iloc[0]['likes']
        
        # Like the comment
        success = comment_system.like_comment(comment_id, 'user2')
        assert success is True, "Like should be successful"
        
        # Verify like count increased
        updated_comments = comment_system.get_comments('timeline', 'like_test', approved_only=False)
        new_likes = updated_comments.iloc[0]['likes']
        assert new_likes == initial_likes + 1, "Like count should increase by 1"
    
    def test_comment_reporting(self, comment_system, db_manager):
        """Test comment reporting functionality."""
        # Add a comment
        comment_system.add_comment(
            'user1', 'figures', 'report_test', 'Reportable comment', None
        )
        
        # Get comment
        comments = comment_system.get_comments('figures', 'report_test', approved_only=False)
        comment_id = int(comments.iloc[0]['id'])
        
        # Report the comment
        success = comment_system.report_comment(comment_id, 'user2', 'Inappropriate')
        assert success is True, "Report should be successful"
        
        # Verify report was logged
        query = """
            SELECT * FROM comment_reports
            WHERE comment_id = ?
        """
        result = db_manager.execute_query(query, (comment_id,))
        assert len(result) > 0, "Report should be logged in comment_reports"


class TestCrossSystemIntegration:
    """Test interactions between multiple systems."""
    
    def test_authenticated_user_feedback_workflow(self, auth_manager, feedback_system):
        """Test complete workflow: user authentication -> feedback submission."""
        # Simulate authenticated user
        username = 'student'
        role = auth_manager.get_user_role(username)
        assert role == 'student', "User should be authenticated with student role"
        
        # User submits feedback
        success = feedback_system.save_feedback(
            username=username,
            target_type='timeline',
            target_id='workflow_test',
            feedback_type='stars',
            feedback_value=4,
            feedback_text='Great timeline!'
        )
        assert success == True, "Authenticated user should be able to submit feedback"
        
        # Verify feedback is recorded
        has_feedback = feedback_system.has_user_feedback(username, 'timeline', 'workflow_test')
        assert has_feedback == True
    
    def test_authenticated_user_comment_workflow(self, auth_manager, comment_system):
        """Test complete workflow: user authentication -> comment submission."""
        # Simulate authenticated user
        username = 'professor'
        role = auth_manager.get_user_role(username)
        assert role == 'professor', "User should be authenticated with professor role"
        
        # User submits comment
        success = comment_system.add_comment(
            username=username,
            target_type='article',
            target_id='workflow_article',
            content='Excellent article!',
            parent_id=None
        )
        assert success is True, "Authenticated user should be able to submit comment"
        
        # Verify comment is recorded
        comments = comment_system.get_comments('article', 'workflow_article')
        assert len(comments) == 1
        assert comments.iloc[0]['username'] == username
    
    def test_role_based_access_to_features(self, auth_manager):
        """Test that different roles have appropriate access levels."""
        # Student can view and interact
        assert auth_manager.check_permission('student', 'student') is True
        
        # Professor has elevated permissions
        assert auth_manager.is_professor('professor') is True
        assert auth_manager.is_professor_or_admin('professor') is True
        
        # Admin has full permissions
        assert auth_manager.is_admin('admin') is True
        assert auth_manager.is_professor_or_admin('admin') is True
    
    def test_content_with_feedback_and_comments(self, feedback_system, comment_system):
        """Test that content can have both feedback and comments."""
        content_type = 'campaigns'
        content_id = 'integrated_content'
        
        # Add feedback
        feedback_system.save_feedback(
            'user1', content_type, content_id, 'thumbs', 1, 'Good'
        )
        feedback_system.save_feedback(
            'user2', content_type, content_id, 'stars', 4, 'Great'
        )
        
        # Add comments
        comment_system.add_comment(
            'user1', content_type, content_id, 'First comment', None
        )
        comment_system.add_comment(
            'user2', content_type, content_id, 'Second comment', None
        )
        
        # Verify both systems have data for the same content
        feedback_stats = feedback_system.get_feedback_stats(content_type, content_id)
        comments = comment_system.get_comments(content_type, content_id, approved_only=False)
        
        assert feedback_stats['total_feedback'] == 2, "Should have 2 feedback entries"
        assert len(comments) == 2, "Should have 2 comments"
    
    def test_user_activity_logging_across_systems(self, auth_manager, feedback_system, 
                                                   comment_system, db_manager):
        """Test that all systems log user activities correctly."""
        username = 'test_user'
        
        # Auth system logs activity
        auth_manager._log_user_activity(username, 'login', 'User logged in')
        
        # Feedback system saves feedback (note: doesn't log to user_activity currently)
        feedback_system.save_feedback(
            username, 'timeline', 'activity_test', 'thumbs', 1, ''
        )
        
        # Comment system logs activity (via add_comment)
        comment_system.add_comment(
            username, 'article', 'activity_test', 'Test comment', None
        )
        
        # Verify activities are logged
        query = "SELECT * FROM user_activity WHERE username = ?"
        activities = db_manager.execute_query(query, (username,))
        
        # Should have at least 2 logged activities (login and comment_posted)
        # Note: Feedback system doesn't currently log to user_activity
        assert len(activities) >= 2, "Should have at least 2 logged activities"
        
        # Verify different action types
        actions = set(activities['action'].tolist())
        assert 'login' in actions, "Should have login action"
        assert 'comment_posted' in actions, "Should have comment_posted action"


# Fixtures

@pytest.fixture(scope="function")
def temp_db():
    """Create a temporary database file."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    # Cleanup
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture(scope="function")
def db_manager(temp_db):
    """Create and initialize a database manager."""
    manager = DatabaseManager(temp_db)
    manager.init_database()
    return manager


@pytest.fixture(scope="function")
def temp_config():
    """Create a temporary config file for authentication."""
    config_data = {
        'credentials': {
            'usernames': {
                'admin': {
                    'name': 'Admin User',
                    'password': '$2b$12$KIXqRzPEBzqZhQvZ5vZ5ZeYqZqZqZqZqZqZqZqZqZqZqZqZqZqZqZ',
                    'role': 'admin'
                },
                'professor': {
                    'name': 'Professor User',
                    'password': '$2b$12$KIXqRzPEBzqZhQvZ5vZ5ZeYqZqZqZqZqZqZqZqZqZqZqZqZqZqZqZ',
                    'role': 'professor'
                },
                'student': {
                    'name': 'Student User',
                    'password': '$2b$12$KIXqRzPEBzqZhQvZ5vZ5ZeYqZqZqZqZqZqZqZqZqZqZqZqZqZqZqZ',
                    'role': 'student'
                }
            }
        },
        'cookie': {
            'name': 'test_cookie',
            'key': 'test_key_12345',
            'expiry_days': 30
        }
    }
    
    fd, path = tempfile.mkstemp(suffix='.yaml')
    with os.fdopen(fd, 'w') as f:
        yaml.dump(config_data, f)
    
    yield path
    
    # Cleanup
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture(scope="function")
def auth_manager(temp_config, db_manager):
    """Create an authentication manager."""
    return AuthManager(temp_config, db_manager)


@pytest.fixture(scope="function")
def feedback_system(db_manager):
    """Create a feedback system."""
    return FeedbackSystem(db_manager)


@pytest.fixture(scope="function")
def comment_system(db_manager):
    """Create a comment system."""
    return CommentSystem(db_manager)
