"""
Property-based tests for Moderation System

Feature: platform-core, Property 16: Moderation Queue Integrity
Validates: Requirements 10.1, 10.2

This module contains property-based tests using Hypothesis to verify
moderation queue integrity and content moderation workflows.
"""

import os
import shutil
import tempfile
from typing import List, Tuple
from datetime import datetime

import pytest
import pandas as pd
from hypothesis import given, strategies as st, settings, assume

from modules.database import DatabaseManager
from modules.auth import AuthManager
from modules.comments import CommentSystem, CommentModerationSystem, get_comment_moderation_system
from modules.articles import ArticleManager
from modules.moderation import UnifiedModerationDashboard


class TestModerationProperties:
    """
    Property-based tests for moderation system.
    
    Feature: platform-core, Property 16: Moderation Queue Integrity
    """
    
    def setup_method(self):
        """Set up test environment for each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_counter = 0
    
    def _get_fresh_system(self):
        """Create a fresh database and moderation system for each test example."""
        self.test_counter += 1
        test_db_path = os.path.join(self.temp_dir, f"test_moderation_{self.test_counter}.db")
        
        # Create test database manager
        db_manager = DatabaseManager(test_db_path)
        db_manager.init_database()
        
        # Create comment system
        comment_system = CommentSystem(db_manager)
        
        # Create comment moderation system
        comment_mod_system = get_comment_moderation_system(comment_system)
        
        return db_manager, comment_system, comment_mod_system
    
    def teardown_method(self):
        """Clean up test environment after each test method."""
        import glob
        for db_file in glob.glob(os.path.join(self.temp_dir, "test_moderation_*.db")):
            if os.path.exists(db_file):
                os.remove(db_file)
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @given(
        st.text(min_size=1, max_size=20),  # username
        st.text(min_size=1, max_size=20),  # reporter_username
        st.sampled_from(['timeline', 'figures', 'campaigns', 'article']),  # target_type
        st.text(min_size=1, max_size=20),  # target_id
        st.text(min_size=1, max_size=200),  # content
        st.text(min_size=1, max_size=100)   # report_reason
    )
    @settings(max_examples=10, deadline=None)
    def test_reported_comment_appears_in_moderation_queue(
        self,
        username: str,
        reporter_username: str,
        target_type: str,
        target_id: str,
        content: str,
        report_reason: str
    ):
        """
        Property 16: For any content requiring moderation (reported comment),
        the system should add it to the appropriate moderation queue with 
        proper categorization.
        
        Feature: platform-core, Property 16: Moderation Queue Integrity
        Validates: Requirements 10.1, 10.2
        """
        # Ensure reporter is different from commenter
        assume(username != reporter_username)
        
        # Get fresh system
        db_manager, comment_system, comment_mod_system = self._get_fresh_system()
        
        # Add a comment
        success = comment_system.add_comment(
            username=username,
            target_type=target_type,
            target_id=target_id,
            content=content,
            parent_id=None
        )
        assert success is True, "Comment should be added successfully"
        
        # Get the comment ID
        comments = comment_system.get_comments(target_type, target_id, approved_only=False)
        assert len(comments) == 1, "Should have exactly one comment"
        comment_id = comments.iloc[0]['id']
        
        # Report the comment
        report_success = comment_system.report_comment(
            comment_id=comment_id,
            reporter_username=reporter_username,
            reason=report_reason
        )
        assert report_success is True, "Comment report should succeed"
        
        # Verify comment appears in moderation queue
        reported_comments = comment_mod_system.get_reported_comments()
        
        # Should have at least one reported comment
        assert len(reported_comments) > 0, "Moderation queue should contain reported comment"
        
        # Find our reported comment - convert comment_id column to int for comparison
        if not reported_comments.empty:
            reported_comments['comment_id'] = reported_comments['comment_id'].astype(int)
        our_report = reported_comments[reported_comments['comment_id'] == comment_id]
        assert len(our_report) > 0, f"Comment {comment_id} should be in moderation queue"
        
        # Verify proper categorization
        report = our_report.iloc[0]
        assert report['reporter_username'] == reporter_username, \
            f"Reporter should be {reporter_username}, got {report['reporter_username']}"
        assert report['comment_username'] == username, \
            f"Comment author should be {username}, got {report['comment_username']}"
        assert report_reason in report['reason'], \
            f"Report reason should be in details"
        assert report['target_type'] == target_type, \
            f"Target type should be {target_type}"
        assert report['target_id'] == target_id, \
            f"Target ID should be {target_id}"
    
    @given(
        st.lists(
            st.tuples(
                st.text(min_size=1, max_size=15),  # username
                st.text(min_size=1, max_size=15),  # reporter
                st.text(min_size=1, max_size=100)  # content
            ),
            min_size=1,
            max_size=5
        ),
        st.sampled_from(['timeline', 'figures', 'campaigns', 'article']),
        st.text(min_size=1, max_size=15)
    )
    @settings(max_examples=10, deadline=None)
    def test_multiple_reported_comments_in_queue(
        self,
        comment_data: List[Tuple[str, str, str]],
        target_type: str,
        target_id: str
    ):
        """
        Property 16: For any set of reported comments, all should appear in 
        the moderation queue with correct categorization.
        
        Feature: platform-core, Property 16: Moderation Queue Integrity
        Validates: Requirements 10.1, 10.2
        """
        # Ensure all reporters are different from commenters
        filtered_data = [(u, r, c) for u, r, c in comment_data if u != r]
        assume(len(filtered_data) > 0)
        
        # Get fresh system
        db_manager, comment_system, comment_mod_system = self._get_fresh_system()
        
        comment_ids = []
        
        # Add and report all comments
        for username, reporter, content in filtered_data:
            # Add comment
            success = comment_system.add_comment(
                username=username,
                target_type=target_type,
                target_id=target_id,
                content=content,
                parent_id=None
            )
            assert success is True, f"Comment from {username} should be added"
            
            # Get comment ID
            comments = comment_system.get_comments(target_type, target_id, approved_only=False)
            comment_id = comments[comments['content'] == content].iloc[0]['id']
            comment_ids.append(comment_id)
            
            # Report comment
            report_success = comment_system.report_comment(
                comment_id=comment_id,
                reporter_username=reporter,
                reason=f"Reported by {reporter}"
            )
            assert report_success is True, f"Report from {reporter} should succeed"
        
        # Get moderation queue
        reported_comments = comment_mod_system.get_reported_comments()
        
        # Verify all reported comments are in queue
        assert len(reported_comments) >= len(filtered_data), \
            f"Queue should contain at least {len(filtered_data)} reported comments"
        
        # Convert comment_id column to int for comparison
        if not reported_comments.empty:
            reported_comments['comment_id'] = reported_comments['comment_id'].astype(int)
        
        # Verify each comment is in the queue
        for comment_id in comment_ids:
            matching = reported_comments[reported_comments['comment_id'] == comment_id]
            assert len(matching) > 0, f"Comment {comment_id} should be in moderation queue"
    
    @given(
        st.text(min_size=1, max_size=20),  # username
        st.text(min_size=1, max_size=20),  # admin_username
        st.sampled_from(['timeline', 'figures', 'campaigns', 'article']),
        st.text(min_size=1, max_size=20),
        st.text(min_size=1, max_size=200)
    )
    @settings(max_examples=10, deadline=None)
    def test_comment_approval_removes_from_unapproved_queue(
        self,
        username: str,
        admin_username: str,
        target_type: str,
        target_id: str,
        content: str
    ):
        """
        Property 16: For any unapproved comment that is approved, it should 
        be removed from the unapproved moderation queue.
        
        Feature: platform-core, Property 16: Moderation Queue Integrity
        Validates: Requirements 10.1, 10.2
        """
        # Get fresh system
        db_manager, comment_system, comment_mod_system = self._get_fresh_system()
        
        # Manually add an unapproved comment
        query = """
            INSERT INTO comments 
            (username, target_type, target_id, content, is_approved)
            VALUES (?, ?, ?, ?, 0)
        """
        db_manager.execute_update(query, (username, target_type, target_id, content))
        
        # Get the comment ID
        all_comments_query = "SELECT * FROM comments WHERE is_approved = 0"
        unapproved = db_manager.execute_query(all_comments_query)
        assert len(unapproved) == 1, "Should have one unapproved comment"
        comment_id = unapproved.iloc[0]['id']
        
        # Verify comment is in unapproved queue
        unapproved_queue = comment_mod_system.get_unapproved_comments()
        assert len(unapproved_queue) == 1, "Unapproved queue should have one comment"
        assert unapproved_queue.iloc[0]['id'] == comment_id, \
            "Comment should be in unapproved queue"
        
        # Approve the comment
        approval_success = comment_mod_system.approve_comment(comment_id, admin_username)
        assert approval_success is True, "Comment approval should succeed"
        
        # Verify comment is removed from unapproved queue
        unapproved_queue_after = comment_mod_system.get_unapproved_comments()
        assert len(unapproved_queue_after) == 0, \
            "Unapproved queue should be empty after approval"
        
        # Verify comment is now approved
        approved_comments = comment_system.get_comments(
            target_type, target_id, approved_only=True
        )
        assert len(approved_comments) == 1, "Should have one approved comment"
        assert approved_comments.iloc[0]['id'] == comment_id, \
            "Approved comment should be the one we approved"
    
    @given(
        st.text(min_size=1, max_size=20),  # username
        st.text(min_size=1, max_size=20),  # admin_username
        st.sampled_from(['timeline', 'figures', 'campaigns', 'article']),
        st.text(min_size=1, max_size=20),
        st.text(min_size=1, max_size=200)
    )
    @settings(max_examples=10, deadline=None)
    def test_comment_rejection_removes_from_system(
        self,
        username: str,
        admin_username: str,
        target_type: str,
        target_id: str,
        content: str
    ):
        """
        Property 16: For any comment that is rejected, it should be completely 
        removed from the system and all moderation queues.
        
        Feature: platform-core, Property 16: Moderation Queue Integrity
        Validates: Requirements 10.1, 10.2
        """
        # Get fresh system
        db_manager, comment_system, comment_mod_system = self._get_fresh_system()
        
        # Add an unapproved comment
        query = """
            INSERT INTO comments 
            (username, target_type, target_id, content, is_approved)
            VALUES (?, ?, ?, ?, 0)
        """
        db_manager.execute_update(query, (username, target_type, target_id, content))
        
        # Get comment ID
        unapproved = comment_mod_system.get_unapproved_comments()
        assert len(unapproved) == 1, "Should have one unapproved comment"
        comment_id = unapproved.iloc[0]['id']
        
        # Reject the comment
        rejection_success = comment_mod_system.reject_comment(comment_id, admin_username)
        assert rejection_success is True, "Comment rejection should succeed"
        
        # Verify comment is removed from unapproved queue
        unapproved_after = comment_mod_system.get_unapproved_comments()
        assert len(unapproved_after) == 0, \
            "Unapproved queue should be empty after rejection"
        
        # Verify comment is not in approved comments
        approved_comments = comment_system.get_comments(
            target_type, target_id, approved_only=True
        )
        assert len(approved_comments) == 0, \
            "Should have no approved comments after rejection"
        
        # Verify comment is completely removed from database
        all_comments_query = "SELECT * FROM comments WHERE id = ?"
        result = db_manager.execute_query(all_comments_query, (comment_id,))
        assert len(result) == 0, \
            "Comment should be completely removed from database"
    
    @given(
        st.lists(
            st.tuples(
                st.text(min_size=1, max_size=15),  # username
                st.text(min_size=1, max_size=100)  # content
            ),
            min_size=2,
            max_size=5
        ),
        st.text(min_size=1, max_size=15),  # admin_username
        st.sampled_from(['timeline', 'figures', 'campaigns', 'article']),
        st.text(min_size=1, max_size=15)
    )
    @settings(max_examples=10, deadline=None)
    def test_bulk_comment_approval_integrity(
        self,
        comment_data: List[Tuple[str, str]],
        admin_username: str,
        target_type: str,
        target_id: str
    ):
        """
        Property 16: For any set of comments approved in bulk, all should be 
        properly approved and removed from moderation queue.
        
        Feature: platform-core, Property 16: Moderation Queue Integrity
        Validates: Requirements 10.1, 10.2
        """
        # Get fresh system
        db_manager, comment_system, comment_mod_system = self._get_fresh_system()
        
        comment_ids = []
        
        # Add unapproved comments
        for username, content in comment_data:
            query = """
                INSERT INTO comments 
                (username, target_type, target_id, content, is_approved)
                VALUES (?, ?, ?, ?, 0)
            """
            db_manager.execute_update(query, (username, target_type, target_id, content))
            
            # Get the comment ID
            result = db_manager.execute_query(
                "SELECT id FROM comments WHERE content = ? AND username = ? ORDER BY id DESC LIMIT 1",
                (content, username)
            )
            comment_ids.append(result.iloc[0]['id'])
        
        # Verify all comments are in unapproved queue
        unapproved_before = comment_mod_system.get_unapproved_comments()
        assert len(unapproved_before) == len(comment_data), \
            f"Should have {len(comment_data)} unapproved comments"
        
        # Bulk approve all comments
        for comment_id in comment_ids:
            success = comment_mod_system.approve_comment(comment_id, admin_username)
            assert success is True, f"Approval of comment {comment_id} should succeed"
        
        # Verify all comments are removed from unapproved queue
        unapproved_after = comment_mod_system.get_unapproved_comments()
        assert len(unapproved_after) == 0, \
            "Unapproved queue should be empty after bulk approval"
        
        # Verify all comments are now approved
        approved_comments = comment_system.get_comments(
            target_type, target_id, approved_only=True
        )
        assert len(approved_comments) == len(comment_data), \
            f"Should have {len(comment_data)} approved comments"
        
        # Verify all comment IDs are in approved list
        approved_ids = set(approved_comments['id'].tolist())
        for comment_id in comment_ids:
            assert comment_id in approved_ids, \
                f"Comment {comment_id} should be in approved list"
    
    @given(
        st.text(min_size=1, max_size=20),  # username
        st.text(min_size=1, max_size=20),  # admin_username
        st.sampled_from(['timeline', 'figures', 'campaigns', 'article']),
        st.text(min_size=1, max_size=20),
        st.text(min_size=1, max_size=200),
        st.text(min_size=1, max_size=200)  # new_content
    )
    @settings(max_examples=10, deadline=None)
    def test_comment_edit_preserves_moderation_state(
        self,
        username: str,
        admin_username: str,
        target_type: str,
        target_id: str,
        original_content: str,
        new_content: str
    ):
        """
        Property 16: For any comment that is edited by a moderator, the edit 
        should preserve the comment's moderation state and update content.
        
        Feature: platform-core, Property 16: Moderation Queue Integrity
        Validates: Requirements 10.1, 10.2
        """
        # Ensure contents are different
        assume(original_content != new_content)
        
        # Get fresh system
        db_manager, comment_system, comment_mod_system = self._get_fresh_system()
        
        # Add an approved comment
        success = comment_system.add_comment(
            username=username,
            target_type=target_type,
            target_id=target_id,
            content=original_content,
            parent_id=None
        )
        assert success is True, "Comment should be added"
        
        # Get comment ID
        comments = comment_system.get_comments(target_type, target_id, approved_only=False)
        assert len(comments) == 1, "Should have one comment"
        comment_id = comments.iloc[0]['id']
        original_is_approved = comments.iloc[0]['is_approved']
        
        # Edit the comment
        edit_success = comment_mod_system.edit_comment(
            comment_id=comment_id,
            new_content=new_content,
            admin_username=admin_username
        )
        assert edit_success is True, "Comment edit should succeed"
        
        # Verify content was updated
        comments_after = comment_system.get_comments(target_type, target_id, approved_only=False)
        edited_comment = comments_after[comments_after['id'] == comment_id]
        assert len(edited_comment) == 1, "Edited comment should exist"
        assert edited_comment.iloc[0]['content'] == new_content, \
            f"Content should be updated to '{new_content}'"
        
        # Verify moderation state was preserved
        assert edited_comment.iloc[0]['is_approved'] == original_is_approved, \
            "Moderation state should be preserved after edit"
        
        # Verify comment ID remained the same
        assert edited_comment.iloc[0]['id'] == comment_id, \
            "Comment ID should remain unchanged after edit"
    
    @given(
        st.text(min_size=1, max_size=20),  # username
        st.text(min_size=1, max_size=20),  # reporter_username
        st.text(min_size=1, max_size=20),  # admin_username
        st.sampled_from(['timeline', 'figures', 'campaigns', 'article']),
        st.text(min_size=1, max_size=20),
        st.text(min_size=1, max_size=200)
    )
    @settings(max_examples=10, deadline=None)
    def test_moderation_action_logging(
        self,
        username: str,
        reporter_username: str,
        admin_username: str,
        target_type: str,
        target_id: str,
        content: str
    ):
        """
        Property 16: For any moderation action, the system should log the 
        action with proper attribution and details.
        
        Feature: platform-core, Property 16: Moderation Queue Integrity
        Validates: Requirements 10.1, 10.2
        """
        # Ensure all usernames are different
        assume(username != reporter_username and username != admin_username)
        
        # Get fresh system
        db_manager, comment_system, comment_mod_system = self._get_fresh_system()
        
        # Add a comment
        success = comment_system.add_comment(
            username=username,
            target_type=target_type,
            target_id=target_id,
            content=content,
            parent_id=None
        )
        assert success is True, "Comment should be added"
        
        # Get comment ID
        comments = comment_system.get_comments(target_type, target_id, approved_only=False)
        comment_id = comments.iloc[0]['id']
        
        # Report the comment
        comment_system.report_comment(comment_id, reporter_username, "Test report")
        
        # Approve the comment (moderation action)
        comment_mod_system.approve_comment(comment_id, admin_username)
        
        # Verify moderation action was logged
        activity_query = """
            SELECT * FROM user_activity 
            WHERE action = 'comment_approved' 
            AND username = ?
            AND target_id = ?
        """
        activity_log = db_manager.execute_query(
            activity_query,
            (admin_username, str(comment_id))
        )
        
        assert len(activity_log) > 0, \
            "Moderation action should be logged in user_activity"
        
        # Verify log details
        log_entry = activity_log.iloc[0]
        assert log_entry['username'] == admin_username, \
            f"Log should attribute action to {admin_username}"
        assert log_entry['action'] == 'comment_approved', \
            "Log should record correct action type"
        assert log_entry['target_type'] == 'comment', \
            "Log should record correct target type"
        assert str(comment_id) in str(log_entry['target_id']), \
            "Log should reference correct comment ID"
