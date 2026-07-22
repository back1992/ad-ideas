"""
Unit tests for new comment system features

Tests for:
- Per-user like tracking
- Report deduplication
- Content sanitization
- Pagination
- Rate limiting
- User self-edit
- Reply notifications
- Comment search
- Soft delete
"""

import os
import shutil
import tempfile
import time
from datetime import datetime, timezone, timedelta

import pytest
import pandas as pd

from modules.database import DatabaseManager
from modules.comments import CommentSystem


class TestCommentLikes:
    """Tests for per-user like tracking"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_likes.db")
        self.db_manager = DatabaseManager(self.db_path)
        self.db_manager.init_database()
        self.comment_system = CommentSystem(self.db_manager)
    
    def approve_all_comments(self):
        """Helper to approve all pending comments (for testing)"""
        # Get ALL comments regardless of target
        query = "SELECT * FROM comments WHERE is_approved = 0 AND deleted_at IS NULL"
        comments = self.comment_system.db_manager.execute_query(query, ())
        for _, comment in comments.iterrows():
            self.comment_system.db_manager.execute_update(
                "UPDATE comments SET is_approved = 1 WHERE id = ?",
                (int(comment['id']),)
            )
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_like_comment_increments_count(self):
        """Test that liking a comment increments the like count"""
        # Create a comment
        self.comment_system.add_comment(
            username="user1",
            target_type="article",
            target_id="1",
            content="Test comment"
        )
        
        # Get comment ID
        comments = self.comment_system.get_comments("article", "1", approved_only=False)
        comment_id = int(comments.iloc[0]['id'])
        
        # Like the comment
        result = self.comment_system.like_comment(comment_id, "user2")
        assert result is True
        
        # Check like count
        comments = self.comment_system.get_comments("article", "1", approved_only=False)
        assert int(comments.iloc[0]['likes']) == 1
    
    def test_unlike_comment_decrements_count(self):
        """Test that unliking a comment decrements the like count"""
        # Create and like a comment
        self.comment_system.add_comment(
            username="user1",
            target_type="article",
            target_id="1",
            content="Test comment"
        )
        comments = self.comment_system.get_comments("article", "1", approved_only=False)
        comment_id = int(comments.iloc[0]['id'])
        
        self.comment_system.like_comment(comment_id, "user2")
        
        # Unlike the comment
        result = self.comment_system.unlike_comment(comment_id, "user2")
        assert result is True
        
        # Check like count
        comments = self.comment_system.get_comments("article", "1", approved_only=False)
        assert int(comments.iloc[0]['likes']) == 0
    
    def test_has_user_liked(self):
        """Test checking if user has liked a comment"""
        # Create a comment
        self.comment_system.add_comment(
            username="user1",
            target_type="article",
            target_id="1",
            content="Test comment"
        )
        comments = self.comment_system.get_comments("article", "1", approved_only=False)
        comment_id = int(comments.iloc[0]['id'])
        
        # User hasn't liked yet
        assert self.comment_system.has_user_liked(comment_id, "user2") is False
        
        # Like the comment
        self.comment_system.like_comment(comment_id, "user2")
        
        # Now user has liked
        assert self.comment_system.has_user_liked(comment_id, "user2") is True
    
    def test_cannot_like_same_comment_twice(self):
        """Test that user cannot like the same comment twice"""
        # Create a comment
        self.comment_system.add_comment(
            username="user1",
            target_type="article",
            target_id="1",
            content="Test comment"
        )
        comments = self.comment_system.get_comments("article", "1", approved_only=False)
        comment_id = int(comments.iloc[0]['id'])
        
        # Like once
        result1 = self.comment_system.like_comment(comment_id, "user2")
        assert result1 is True
        
        # Try to like again
        result2 = self.comment_system.like_comment(comment_id, "user2")
        assert result2 is False
        
        # Count should still be 1
        comments = self.comment_system.get_comments("article", "1", approved_only=False)
        assert int(comments.iloc[0]['likes']) == 1
    
    def test_multiple_users_can_like(self):
        """Test that multiple users can like the same comment"""
        # Create a comment
        self.comment_system.add_comment(
            username="user1",
            target_type="article",
            target_id="1",
            content="Test comment"
        )
        comments = self.comment_system.get_comments("article", "1", approved_only=False)
        comment_id = int(comments.iloc[0]['id'])
        
        # Multiple users like
        self.comment_system.like_comment(comment_id, "user2")
        self.comment_system.like_comment(comment_id, "user3")
        self.comment_system.like_comment(comment_id, "user4")
        
        # Count should be 3
        comments = self.comment_system.get_comments("article", "1", approved_only=False)
        assert int(comments.iloc[0]['likes']) == 3


class TestCommentReports:
    """Tests for report deduplication"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_reports.db")
        self.db_manager = DatabaseManager(self.db_path)
        self.db_manager.init_database()
        self.comment_system = CommentSystem(self.db_manager)
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_report_comment_creates_entry(self):
        """Test that reporting a comment creates a report entry"""
        # Create a comment
        self.comment_system.add_comment(
            username="user1",
            target_type="article",
            target_id="1",
            content="Test comment"
        )
        comments = self.comment_system.get_comments("article", "1", approved_only=False)
        comment_id = int(comments.iloc[0]['id'])
        
        # Report the comment
        result = self.comment_system.report_comment(comment_id, "user2", "Spam")
        assert result is True
        
        # Check report exists
        query = "SELECT * FROM comment_reports WHERE comment_id = ?"
        reports = self.db_manager.execute_query(query, (comment_id,))
        assert len(reports) == 1
        assert reports.iloc[0]['reporter_username'] == "user2"
        assert reports.iloc[0]['reason'] == "Spam"
    
    def test_cannot_report_same_comment_twice(self):
        """Test that user cannot report the same comment twice"""
        # Create a comment
        self.comment_system.add_comment(
            username="user1",
            target_type="article",
            target_id="1",
            content="Test comment"
        )
        comments = self.comment_system.get_comments("article", "1", approved_only=False)
        comment_id = int(comments.iloc[0]['id'])
        
        # Report once
        result1 = self.comment_system.report_comment(comment_id, "user2", "Spam")
        assert result1 is True
        
        # Try to report again
        result2 = self.comment_system.report_comment(comment_id, "user2", "Spam")
        assert result2 is False
        
        # Should still have only 1 report
        query = "SELECT * FROM comment_reports WHERE comment_id = ?"
        reports = self.db_manager.execute_query(query, (comment_id,))
        assert len(reports) == 1
    
    def test_different_users_can_report(self):
        """Test that different users can report the same comment"""
        # Create a comment
        self.comment_system.add_comment(
            username="user1",
            target_type="article",
            target_id="1",
            content="Test comment"
        )
        comments = self.comment_system.get_comments("article", "1", approved_only=False)
        comment_id = int(comments.iloc[0]['id'])
        
        # Different users report
        self.comment_system.report_comment(comment_id, "user2", "Spam")
        self.comment_system.report_comment(comment_id, "user3", "Inappropriate")
        self.comment_system.report_comment(comment_id, "user4", "Offensive")
        
        # Should have 3 reports
        query = "SELECT * FROM comment_reports WHERE comment_id = ?"
        reports = self.db_manager.execute_query(query, (comment_id,))
        assert len(reports) == 3


class TestContentSanitization:
    """Tests for content sanitization"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_sanitization.db")
        self.db_manager = DatabaseManager(self.db_path)
        self.db_manager.init_database()
        self.comment_system = CommentSystem(self.db_manager)
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_sanitize_html_tags(self):
        """Test that script tags are removed entirely"""
        content = "<script>alert('xss')</script>"
        sanitized = self.comment_system.sanitize_content(content)
        assert "<script>" not in sanitized
        assert "alert" not in sanitized  # Script content is removed, not just escaped
    
    def test_sanitize_event_handlers(self):
        """Test that event handlers are removed"""
        content = '<img src="x" onerror="alert(1)">'
        sanitized = self.comment_system.sanitize_content(content)
        assert "onerror" not in sanitized
    
    def test_preserve_safe_content(self):
        """Test that safe content is preserved"""
        content = "This is a normal comment with **markdown**"
        sanitized = self.comment_system.sanitize_content(content)
        assert sanitized == content
    
    def test_escape_quotes(self):
        """Test that quotes are escaped"""
        content = 'He said "hello"'
        sanitized = self.comment_system.sanitize_content(content)
        assert "&quot;" in sanitized


class TestPagination:
    """Tests for comment pagination"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_pagination.db")
        self.db_manager = DatabaseManager(self.db_path)
        self.db_manager.init_database()
        self.comment_system = CommentSystem(self.db_manager)
    
    def approve_all_comments(self):
        """Helper to approve all pending comments (for testing)"""
        # Get ALL comments regardless of target
        query = "SELECT * FROM comments WHERE is_approved = 0 AND deleted_at IS NULL"
        comments = self.comment_system.db_manager.execute_query(query, ())
        for _, comment in comments.iterrows():
            self.comment_system.db_manager.execute_update(
                "UPDATE comments SET is_approved = 1 WHERE id = ?",
                (int(comment['id']),)
            )
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_get_comments_paginated(self):
        """Test paginated comment retrieval"""
        # Create 25 comments
        for i in range(25):
            self.comment_system.add_comment(
                username=f"user{i}",
                target_type="article",
                target_id="1",
                content=f"Comment {i}"
            )
        
        # Get first page (20 comments)
        page1 = self.comment_system.get_comments_paginated("article", "1", page=0, per_page=20, approved_only=False)
        assert len(page1) == 20
        
        # Get second page (5 comments)
        page2 = self.comment_system.get_comments_paginated("article", "1", page=1, per_page=20, approved_only=False)
        assert len(page2) == 5
    
    def test_get_comment_count(self):
        """Test getting total comment count"""
        # Create 15 comments
        for i in range(15):
            self.comment_system.add_comment(
                username=f"user{i}",
                target_type="article",
                target_id="1",
                content=f"Comment {i}"
            )
        
        self.approve_all_comments()
        count = self.comment_system.get_comment_count("article", "1")
        assert count == 15
    
    def test_pagination_sorting(self):
        """Test that pagination respects sorting"""
        # Create comments
        for i in range(5):
            self.comment_system.add_comment(
                username=f"user{i}",
                target_type="article",
                target_id="1",
                content=f"Comment {i}"
            )
        
        self.approve_all_comments()
        # Get newest first
        self.approve_all_comments()
        newest = self.comment_system.get_comments_paginated("article", "1", sort_by="newest")
        assert newest.iloc[0]['content'] == "Comment 4"
        
        # Get oldest first
        oldest = self.comment_system.get_comments_paginated("article", "1", sort_by="oldest")
        assert oldest.iloc[0]['content'] == "Comment 0"


class TestRateLimiting:
    """Tests for rate limiting"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_ratelimit.db")
        self.db_manager = DatabaseManager(self.db_path)
        self.db_manager.init_database()
        self.comment_system = CommentSystem(self.db_manager)
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_rate_limit_allows_normal_usage(self):
        """Test that rate limit allows normal usage"""
        # User should be able to post 10 comments
        for i in range(10):
            result = self.comment_system.add_comment(
                username="user1",
                target_type="article",
                target_id="1",
                content=f"Comment {i}"
            )
            assert result is True
    
    def test_rate_limit_blocks_excessive_usage(self):
        """Test that rate limit blocks excessive usage"""
        # Post 10 comments (limit)
        for i in range(10):
            self.comment_system.add_comment(
                username="user1",
                target_type="article",
                target_id="1",
                content=f"Comment {i}"
            )
        
        # 11th comment should fail
        result = self.comment_system.add_comment(
            username="user1",
            target_type="article",
            target_id="1",
            content="Comment 11"
        )
        assert result is False
    
    def test_check_rate_limit(self):
        """Test rate limit check function"""
        # Initially within limit
        assert self.comment_system.check_rate_limit("user1") is True
        
        # Post 10 comments
        for i in range(10):
            self.comment_system.add_comment(
                username="user1",
                target_type="article",
                target_id="1",
                content=f"Comment {i}"
            )
        
        # Now at limit
        assert self.comment_system.check_rate_limit("user1") is False


class TestUserSelfEdit:
    """Tests for user self-edit feature"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_selfedit.db")
        self.db_manager = DatabaseManager(self.db_path)
        self.db_manager.init_database()
        self.comment_system = CommentSystem(self.db_manager)
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_user_can_edit_own_comment(self):
        """Test that user can edit their own comment"""
        # Create a comment
        self.comment_system.add_comment(
            username="user1",
            target_type="article",
            target_id="1",
            content="Original content"
        )
        comments = self.comment_system.get_comments("article", "1", approved_only=False)
        comment_id = int(comments.iloc[0]['id'])
        
        # Edit the comment
        result = self.comment_system.edit_comment_by_user(
            comment_id,
            "Updated content",
            "user1"
        )
        assert result is True
        
        # Check content was updated
        comments = self.comment_system.get_comments("article", "1", approved_only=False)
        assert comments.iloc[0]['content'] == "Updated content"
    
    def test_user_cannot_edit_others_comment(self):
        """Test that user cannot edit someone else's comment"""
        # Create a comment
        self.comment_system.add_comment(
            username="user1",
            target_type="article",
            target_id="1",
            content="Original content"
        )
        comments = self.comment_system.get_comments("article", "1", approved_only=False)
        comment_id = int(comments.iloc[0]['id'])
        
        # Try to edit as different user
        result = self.comment_system.edit_comment_by_user(
            comment_id,
            "Updated content",
            "user2"
        )
        assert result is False
    
    def test_can_edit_within_time_limit(self):
        """Test that edit is allowed within 24 hours"""
        # Create a comment
        self.comment_system.add_comment(
            username="user1",
            target_type="article",
            target_id="1",
            content="Original content"
        )
        comments = self.comment_system.get_comments("article", "1", approved_only=False)
        comment_id = int(comments.iloc[0]['id'])
        
        # Should be able to edit
        assert self.comment_system.can_edit_comment(comments.iloc[0]['timestamp']) is True
    
    def test_cannot_edit_after_time_limit(self):
        """Test that edit is blocked after 24 hours"""
        # Create a comment with old timestamp
        self.comment_system.add_comment(
            username="user1",
            target_type="article",
            target_id="1",
            content="Original content"
        )
        
        # Manually update timestamp to 25 hours ago
        comments = self.comment_system.get_comments("article", "1", approved_only=False)
        comment_id = int(comments.iloc[0]['id'])
        old_time = (datetime.now(timezone.utc) - timedelta(hours=25)).isoformat()
        query = "UPDATE comments SET timestamp = ? WHERE id = ?"
        self.db_manager.execute_update(query, (old_time, comment_id))
        
        # Check if can edit
        comments = self.comment_system.get_comments("article", "1", approved_only=False)
        assert self.comment_system.can_edit_comment(comments.iloc[0]['timestamp']) is False
    
    def test_edit_records_metadata(self):
        """Test that editing records edited_at and edited_by"""
        # Create a comment
        self.comment_system.add_comment(
            username="user1",
            target_type="article",
            target_id="1",
            content="Original content"
        )
        comments = self.comment_system.get_comments("article", "1", approved_only=False)
        comment_id = int(comments.iloc[0]['id'])
        
        # Edit the comment
        self.comment_system.edit_comment_by_user(comment_id, "Updated", "user1")
        
        # Check metadata
        comments = self.comment_system.get_comments("article", "1", approved_only=False)
        assert comments.iloc[0]['edited_at'] is not None
        assert comments.iloc[0]['edited_by'] == "user1"


class TestNotifications:
    """Tests for reply notifications"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_notifications.db")
        self.db_manager = DatabaseManager(self.db_path)
        self.db_manager.init_database()
        self.comment_system = CommentSystem(self.db_manager)
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_reply_creates_notification(self):
        """Test that replying to a comment creates a notification"""
        # Create parent comment
        self.comment_system.add_comment(
            username="user1",
            target_type="article",
            target_id="1",
            content="Parent comment"
        )
        comments = self.comment_system.get_comments("article", "1", approved_only=False)
        parent_id = int(comments.iloc[0]['id'])
        
        # Reply to it
        self.comment_system.add_comment(
            username="user2",
            target_type="article",
            target_id="1",
            content="Reply comment",
            parent_id=parent_id
        )
        
        # Check notification was created
        notifications = self.comment_system.get_user_notifications("user1")
        assert len(notifications) == 1
        assert notifications.iloc[0]['notification_type'] == "reply"
    
    def test_no_notification_for_self_reply(self):
        """Test that replying to own comment doesn't create notification"""
        # Create parent comment
        self.comment_system.add_comment(
            username="user1",
            target_type="article",
            target_id="1",
            content="Parent comment"
        )
        comments = self.comment_system.get_comments("article", "1", approved_only=False)
        parent_id = int(comments.iloc[0]['id'])
        
        # Reply to own comment
        self.comment_system.add_comment(
            username="user1",
            target_type="article",
            target_id="1",
            content="Reply to self",
            parent_id=parent_id
        )
        
        # Should have no notifications
        notifications = self.comment_system.get_user_notifications("user1")
        assert len(notifications) == 0
    
    def test_mark_notification_read(self):
        """Test marking notification as read"""
        # Create and reply
        self.comment_system.add_comment(
            username="user1",
            target_type="article",
            target_id="1",
            content="Parent comment"
        )
        comments = self.comment_system.get_comments("article", "1", approved_only=False)
        parent_id = int(comments.iloc[0]['id'])
        
        self.comment_system.add_comment(
            username="user2",
            target_type="article",
            target_id="1",
            content="Reply",
            parent_id=parent_id
        )
        
        # Get notification
        notifications = self.comment_system.get_user_notifications("user1")
        notification_id = int(notifications.iloc[0]['id'])
        
        # Mark as read
        result = self.comment_system.mark_notification_read(notification_id)
        assert result is True
        
        # Should not appear in unread notifications
        unread = self.comment_system.get_user_notifications("user1", unread_only=True)
        assert len(unread) == 0


class TestCommentSearch:
    """Tests for comment search functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_search.db")
        self.db_manager = DatabaseManager(self.db_path)
        self.db_manager.init_database()
        self.comment_system = CommentSystem(self.db_manager)
    
    def approve_all_comments(self):
        """Helper to approve all pending comments (for testing)"""
        # Get ALL comments regardless of target
        query = "SELECT * FROM comments WHERE is_approved = 0 AND deleted_at IS NULL"
        comments = self.comment_system.db_manager.execute_query(query, ())
        for _, comment in comments.iterrows():
            self.comment_system.db_manager.execute_update(
                "UPDATE comments SET is_approved = 1 WHERE id = ?",
                (int(comment['id']),)
            )
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_search_by_content(self):
        """Test searching comments by content"""
        # Create comments
        self.comment_system.add_comment(
            username="user1",
            target_type="article",
            target_id="1",
            content="This is about Python"
        )
        self.comment_system.add_comment(
            username="user2",
            target_type="article",
            target_id="1",
            content="JavaScript is great"
        )
        self.comment_system.add_comment(
            username="user3",
            target_type="article",
            target_id="1",
            content="Python and JavaScript"
        )
        
        self.approve_all_comments()
        # Search for Python
        results = self.comment_system.search_comments("Python")
        assert len(results) == 2
    
    def test_search_by_target_type(self):
        """Test searching with target type filter"""
        # Create comments on different targets
        self.comment_system.add_comment(
            username="user1",
            target_type="article",
            target_id="1",
            content="Article comment"
        )
        self.comment_system.add_comment(
            username="user2",
            target_type="timeline",
            target_id="1",
            content="Timeline comment"
        )
        
        self.approve_all_comments()
        # Search only articles
        results = self.comment_system.search_comments("Comment", target_type="article")
        assert len(results) == 1
        assert results.iloc[0]['target_type'] == "article"
    
    def test_search_by_username(self):
        """Test searching with username filter"""
        # Create comments from different users
        self.comment_system.add_comment(
            username="alice",
            target_type="article",
            target_id="1",
            content="Comment 1"
        )
        self.comment_system.add_comment(
            username="bob",
            target_type="article",
            target_id="1",
            content="Comment 2"
        )
        self.comment_system.add_comment(
            username="alice",
            target_type="article",
            target_id="1",
            content="Comment 3"
        )
        
        # Search only alice's comments
        self.approve_all_comments()
        results = self.comment_system.search_comments("Comment", username="alice")
        assert len(results) == 2


class TestSoftDelete:
    """Tests for soft delete functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_softdelete.db")
        self.db_manager = DatabaseManager(self.db_path)
        self.db_manager.init_database()
        self.comment_system = CommentSystem(self.db_manager)
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def approve_all_comments(self):
        """Helper to approve all pending comments (for testing)"""
        # Get ALL comments regardless of target
        query = "SELECT * FROM comments WHERE is_approved = 0 AND deleted_at IS NULL"
        comments = self.comment_system.db_manager.execute_query(query, ())
        for _, comment in comments.iterrows():
            self.comment_system.db_manager.execute_update(
                "UPDATE comments SET is_approved = 1 WHERE id = ?",
                (int(comment['id']),)
            )
    
    def test_soft_delete_marks_comment(self):
        """Test that soft delete sets deleted_at"""
        # Create a comment
        self.comment_system.add_comment(
            username="user1",
            target_type="article",
            target_id="1",
            content="Test comment"
        )
        comments = self.comment_system.get_comments("article", "1", approved_only=False)
        comment_id = int(comments.iloc[0]['id'])
        
        # Soft delete
        query = "UPDATE comments SET deleted_at = CURRENT_TIMESTAMP WHERE id = ?"
        self.db_manager.execute_update(query, (comment_id,))
        
        # Check deleted_at is set
        query = "SELECT deleted_at FROM comments WHERE id = ?"
        result = self.db_manager.execute_query(query, (comment_id,))
        assert result.iloc[0]['deleted_at'] is not None
    
    def test_soft_deleted_comments_hidden(self):
        """Test that soft deleted comments are hidden from normal queries"""
        # Create comments
        self.comment_system.add_comment(
            username="user1",
            target_type="article",
            target_id="1",
            content="Visible comment"
        )
        self.comment_system.add_comment(
            username="user2",
            target_type="article",
            target_id="1",
            content="Hidden comment"
        )
        
        comments = self.comment_system.get_comments("article", "1", approved_only=False)
        comment_id = int(comments.iloc[1]['id'])
        
        # Soft delete second comment
        query = "UPDATE comments SET deleted_at = CURRENT_TIMESTAMP WHERE id = ?"
        self.db_manager.execute_update(query, (comment_id,))
        
        # Should only see 1 comment
        comments = self.comment_system.get_comments("article", "1", approved_only=False)
        assert len(comments) == 1
        assert comments.iloc[0]['content'] == "Visible comment"
    
    def test_soft_deleted_comments_count_excluded(self):
        """Test that soft deleted comments are excluded from count"""
        # Create comments
        for i in range(3):
            self.comment_system.add_comment(
                username=f"user{i}",
                target_type="article",
                target_id="1",
                content=f"Comment {i}"
            )
        
        # Approve all first
        self.approve_all_comments()
        
        # Delete one
        comments = self.comment_system.get_comments("article", "1")
        comment_id = int(comments.iloc[0]['id'])
        query = "UPDATE comments SET deleted_at = CURRENT_TIMESTAMP WHERE id = ?"
        self.db_manager.execute_update(query, (comment_id,))
        
        # Count should be 2
        count = self.comment_system.get_comment_count("article", "1")
        assert count == 2
