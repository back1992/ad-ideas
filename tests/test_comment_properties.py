"""
Property-based tests for CommentSystem

Feature: platform-core, Property 9: Comment Data Persistence
Feature: platform-core, Property 10: Comment Threading Integrity
Validates: Requirements 4.2, 4.4

This module contains property-based tests using Hypothesis to verify
comment data persistence and threading integrity.
"""

import os
import shutil
import tempfile
from typing import Tuple, List, Optional
from datetime import datetime, timezone

import pytest
import pandas as pd
from hypothesis import given, strategies as st, settings, assume

from modules.database import DatabaseManager
from modules.comments import CommentSystem


class TestCommentProperties:
    """
    Property-based tests for comment system.
    
    Feature: platform-core, Property 9: Comment Data Persistence
    Feature: platform-core, Property 10: Comment Threading Integrity
    """
    
    def setup_method(self):
        """Set up test environment for each test method."""
        self.temp_dir = tempfile.mkdtemp()
        # Use a counter to ensure unique database for each test
        self.test_counter = 0
    
    def _get_fresh_system(self):
        """Create a fresh database and comment system for each test example."""
        self.test_counter += 1
        test_db_path = os.path.join(self.temp_dir, f"test_comments_{self.test_counter}.db")
        
        # Create test database manager
        db_manager = DatabaseManager(test_db_path)
        db_manager.init_database()
        
        # Create comment system
        return CommentSystem(db_manager)
    
    def teardown_method(self):
        """Clean up test environment after each test method."""
        # Clean up all test database files
        import glob
        for db_file in glob.glob(os.path.join(self.temp_dir, "test_comments_*.db")):
            if os.path.exists(db_file):
                os.remove(db_file)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @given(
        st.text(min_size=1, max_size=20),  # username
        st.sampled_from(['timeline', 'figures', 'campaigns', 'article']),  # target_type
        st.text(min_size=1, max_size=20),  # target_id
        st.text(min_size=1, max_size=500)  # content
    )
    @settings(max_examples=20, deadline=None)
    def test_comment_data_persistence(
        self,
        username: str,
        target_type: str,
        target_id: str,
        content: str
    ):
        """
        Property 9: For any valid comment submission, the system should store 
        the comment with correct timestamp, user attribution, and content.
        
        Feature: platform-core, Property 9: Comment Data Persistence
        Validates: Requirements 4.2
        """
        # Get fresh system for this test
        comment_system = self._get_fresh_system()
        
        # Record time before submission (timezone-naive to match SQLite)
        time_before = datetime.now(timezone.utc).replace(tzinfo=None).replace(microsecond=0)
        
        # Submit comment
        success = comment_system.add_comment(
            username=username,
            target_type=target_type,
            target_id=target_id,
            content=content,
            parent_id=None
        )
        
        # Record time after submission
        time_after = datetime.now(timezone.utc).replace(tzinfo=None).replace(microsecond=0) + pd.Timedelta(seconds=1)
        
        # Verify submission succeeded
        assert success is True, "Comment submission should succeed"
        
        # Retrieve comments for this content
        comments = comment_system.get_comments(
            target_type=target_type,
            target_id=target_id,
            approved_only=False
        )
        
        # Verify exactly one comment exists
        assert len(comments) == 1, f"Expected 1 comment, found {len(comments)}"
        
        # Get the comment
        comment = comments.iloc[0]
        
        # Verify user attribution
        assert comment['username'] == username, \
            f"Username should be {username}, got {comment['username']}"
        
        # Verify content
        assert comment['content'] == content, \
            f"Content should match submitted content"
        
        # Verify target information
        assert comment['target_type'] == target_type, \
            f"Target type should be {target_type}, got {comment['target_type']}"
        assert comment['target_id'] == target_id, \
            f"Target ID should be {target_id}, got {comment['target_id']}"
        
        # Verify timestamp is within reasonable range (SQLite stores timezone-naive)
        comment_timestamp = datetime.fromisoformat(comment['timestamp']).replace(microsecond=0)
        assert time_before <= comment_timestamp <= time_after, \
            f"Timestamp should be between {time_before} and {time_after}, got {comment_timestamp}"
        
        # Verify comment approval status (student comments require approval)
        # Note: Comments from non-professor/admin users are pending approval by default
        assert comment['is_approved'] in [0, 1], "Comment should have valid approval status"
        
        # Verify parent_id is None for top-level comment
        assert pd.isna(comment['parent_id']), "Top-level comment should have no parent"
        
        # Verify likes initialized to 0
        assert comment['likes'] == 0, "New comment should have 0 likes"
        
        # Verify comment has an ID
        assert comment['id'] > 0, "Comment should have a valid ID"
    
    @given(
        st.lists(
            st.tuples(
                st.text(min_size=1, max_size=15),  # username
                st.text(min_size=1, max_size=200)  # content
            ),
            min_size=1,
            max_size=10
        ),
        st.sampled_from(['timeline', 'figures', 'campaigns', 'article']),  # target_type
        st.text(min_size=1, max_size=15)  # target_id
    )
    @settings(max_examples=20, deadline=None)
    def test_multiple_comments_persistence(
        self,
        user_content_pairs: List[Tuple[str, str]],
        target_type: str,
        target_id: str
    ):
        """
        Property: For any set of comment submissions, all comments should be 
        persisted with correct data.
        
        Feature: platform-core, Property 9: Comment Data Persistence
        Validates: Requirements 4.2
        """
        # Get fresh system for this test
        comment_system = self._get_fresh_system()
        
        # Submit all comments
        for username, content in user_content_pairs:
            success = comment_system.add_comment(
                username=username,
                target_type=target_type,
                target_id=target_id,
                content=content,
                parent_id=None
            )
            assert success is True, f"Comment from {username} should be saved"
        
        # Retrieve all comments
        comments = comment_system.get_comments(
            target_type=target_type,
            target_id=target_id,
            approved_only=False
        )
        
        # Verify count matches
        expected_count = len(user_content_pairs)
        assert len(comments) == expected_count, \
            f"Expected {expected_count} comments, found {len(comments)}"
        
        # Verify each comment's data by matching username AND content
        for i, (username, content) in enumerate(user_content_pairs):
            # Find the comment by both username and content
            matching_comments = comments[
                (comments['username'] == username) & 
                (comments['content'] == content)
            ]
            assert len(matching_comments) > 0, \
                f"Comment from {username} with content '{content[:50]}...' should exist"
            
            comment = matching_comments.iloc[0]
            assert comment['target_type'] == target_type, \
                f"Target type should be {target_type} for comment {i}"
            assert comment['target_id'] == target_id, \
                f"Target ID should be {target_id} for comment {i}"
    
    @given(
        st.text(min_size=1, max_size=20),  # parent_username
        st.text(min_size=1, max_size=20),  # reply_username
        st.sampled_from(['timeline', 'figures', 'campaigns', 'article']),  # target_type
        st.text(min_size=1, max_size=20),  # target_id
        st.text(min_size=1, max_size=200),  # parent_content
        st.text(min_size=1, max_size=200)   # reply_content
    )
    @settings(max_examples=20, deadline=None)
    def test_comment_threading_integrity(
        self,
        parent_username: str,
        reply_username: str,
        target_type: str,
        target_id: str,
        parent_content: str,
        reply_content: str
    ):
        """
        Property 10: For any reply to a comment, the system should maintain 
        proper parent-child relationships in the comment thread structure.
        
        Feature: platform-core, Property 10: Comment Threading Integrity
        Validates: Requirements 4.4
        """
        # Get fresh system for this test
        comment_system = self._get_fresh_system()
        
        # Submit parent comment
        parent_success = comment_system.add_comment(
            username=parent_username,
            target_type=target_type,
            target_id=target_id,
            content=parent_content,
            parent_id=None
        )
        assert parent_success is True, "Parent comment submission should succeed"
        
        # Get parent comment to retrieve its ID
        comments = comment_system.get_comments(
            target_type=target_type,
            target_id=target_id,
            approved_only=False
        )
        assert len(comments) == 1, "Should have exactly one parent comment"
        parent_comment = comments.iloc[0]
        parent_id = parent_comment['id']
        
        # Verify parent has no parent_id
        assert pd.isna(parent_comment['parent_id']), \
            "Parent comment should have no parent_id"
        
        # Submit reply comment
        reply_success = comment_system.add_comment(
            username=reply_username,
            target_type=target_type,
            target_id=target_id,
            content=reply_content,
            parent_id=parent_id
        )
        assert reply_success is True, "Reply comment submission should succeed"
        
        # Get all comments
        all_comments = comment_system.get_comments(
            target_type=target_type,
            target_id=target_id,
            approved_only=False
        )
        
        # Verify we have 2 comments
        assert len(all_comments) == 2, f"Expected 2 comments, found {len(all_comments)}"
        
        # Find the reply comment by matching username and content
        reply_comments = all_comments[
            (all_comments['username'] == reply_username) & 
            (all_comments['content'] == reply_content) &
            (all_comments['id'] != parent_id)
        ]
        assert len(reply_comments) == 1, "Should have exactly one reply comment"
        reply_comment = reply_comments.iloc[0]
        
        # Verify threading integrity
        assert reply_comment['parent_id'] == parent_id, \
            f"Reply should have parent_id {parent_id}, got {reply_comment['parent_id']}"
        
        # Verify reply has correct attribution
        assert reply_comment['username'] == reply_username, \
            f"Reply username should be {reply_username}, got {reply_comment['username']}"
        
        # Verify reply has correct content
        assert reply_comment['content'] == reply_content, \
            "Reply content should match submitted content"
        
        # Verify reply targets same content as parent
        assert reply_comment['target_type'] == target_type, \
            "Reply should target same type as parent"
        assert reply_comment['target_id'] == target_id, \
            "Reply should target same ID as parent"
        
        # Verify reply has different ID from parent
        assert reply_comment['id'] != parent_id, \
            "Reply should have different ID from parent"
    
    @given(
        st.text(min_size=1, max_size=15),  # username
        st.sampled_from(['timeline', 'figures', 'campaigns', 'article']),  # target_type
        st.text(min_size=1, max_size=15),  # target_id
        st.text(min_size=1, max_size=100),  # parent_content
        st.lists(
            st.text(min_size=1, max_size=100),  # reply_contents
            min_size=1,
            max_size=5
        )
    )
    @settings(max_examples=20, deadline=None)
    def test_multiple_replies_threading_integrity(
        self,
        username: str,
        target_type: str,
        target_id: str,
        parent_content: str,
        reply_contents: List[str]
    ):
        """
        Property: For any parent comment with multiple replies, all replies 
        should correctly reference the parent comment.
        
        Feature: platform-core, Property 10: Comment Threading Integrity
        Validates: Requirements 4.4
        """
        # Get fresh system for this test
        comment_system = self._get_fresh_system()
        
        # Submit parent comment
        parent_success = comment_system.add_comment(
            username=username,
            target_type=target_type,
            target_id=target_id,
            content=parent_content,
            parent_id=None
        )
        assert parent_success is True, "Parent comment should be saved"
        
        # Get parent comment ID
        comments = comment_system.get_comments(
            target_type=target_type,
            target_id=target_id,
            approved_only=False
        )
        parent_id = comments.iloc[0]['id']
        
        # Submit all replies
        for reply_content in reply_contents:
            reply_success = comment_system.add_comment(
                username=username,
                target_type=target_type,
                target_id=target_id,
                content=reply_content,
                parent_id=parent_id
            )
            assert reply_success is True, f"Reply should be saved"
        
        # Get all comments
        all_comments = comment_system.get_comments(
            target_type=target_type,
            target_id=target_id,
            approved_only=False
        )
        
        # Verify total count (1 parent + N replies)
        expected_count = 1 + len(reply_contents)
        assert len(all_comments) == expected_count, \
            f"Expected {expected_count} comments, found {len(all_comments)}"
        
        # Verify parent comment has no parent_id
        parent_comments = all_comments[all_comments['parent_id'].isna()]
        assert len(parent_comments) == 1, "Should have exactly one parent"
        assert parent_comments.iloc[0]['content'] == parent_content, \
            "Parent should have the expected content"
        
        # Verify all replies reference the parent
        reply_comments = all_comments[all_comments['parent_id'] == parent_id]
        assert len(reply_comments) == len(reply_contents), \
            f"Expected {len(reply_contents)} replies, found {len(reply_comments)}"
        
        # Verify each reply has correct parent_id
        for _, reply in reply_comments.iterrows():
            assert reply['parent_id'] == parent_id, \
                f"Reply should have parent_id {parent_id}, got {reply['parent_id']}"
            assert reply['id'] != parent_id, \
                "Reply should have different ID from parent"
    
    @given(
        st.lists(
            st.text(min_size=1, max_size=15),  # usernames
            min_size=2,
            max_size=4
        ),
        st.sampled_from(['timeline', 'figures', 'campaigns', 'article']),  # target_type
        st.text(min_size=1, max_size=15),  # target_id
        st.lists(
            st.text(min_size=1, max_size=100),  # contents
            min_size=2,
            max_size=4
        )
    )
    @settings(max_examples=20, deadline=None)
    def test_nested_threading_integrity(
        self,
        usernames: List[str],
        target_type: str,
        target_id: str,
        contents: List[str]
    ):
        """
        Property: For any nested comment thread, parent-child relationships 
        should be maintained correctly at all levels.
        
        Feature: platform-core, Property 10: Comment Threading Integrity
        Validates: Requirements 4.4
        """
        # Ensure we have enough data
        assume(len(usernames) >= 2 and len(contents) >= 2)
        
        # Get fresh system for this test
        comment_system = self._get_fresh_system()
        
        # Create a chain: comment1 -> comment2 -> comment3 -> ...
        parent_id = None
        comment_ids = []
        
        for i, (username, content) in enumerate(zip(usernames, contents)):
            success = comment_system.add_comment(
                username=username,
                target_type=target_type,
                target_id=target_id,
                content=content,
                parent_id=parent_id
            )
            assert success is True, f"Comment {i} should be saved"
            
            # Get the comment we just added
            comments = comment_system.get_comments(
                target_type=target_type,
                target_id=target_id,
                approved_only=False
            )
            
            # Find the comment by content and username (to handle duplicates)
            matching = comments[
                (comments['content'] == content) & 
                (comments['username'] == username)
            ]
            
            # If there are multiple matches, get the most recent one
            if len(matching) > 1:
                matching = matching.sort_values('id', ascending=False).head(1)
            
            assert len(matching) >= 1, f"Should find at least one comment with content '{content[:30]}...'"
            
            current_comment = matching.iloc[0]
            current_id = current_comment['id']
            comment_ids.append(current_id)
            
            # Verify parent relationship
            if parent_id is None:
                assert pd.isna(current_comment['parent_id']), \
                    f"First comment should have no parent"
            else:
                assert current_comment['parent_id'] == parent_id, \
                    f"Comment {i} should have parent_id {parent_id}, got {current_comment['parent_id']}"
            
            # Set parent for next iteration
            parent_id = current_id
        
        # Verify all comments exist
        all_comments = comment_system.get_comments(
            target_type=target_type,
            target_id=target_id,
            approved_only=False
        )
        
        expected_count = min(len(usernames), len(contents))
        assert len(all_comments) == expected_count, \
            f"Expected {expected_count} comments, found {len(all_comments)}"
        
        # Verify the chain structure
        for i in range(1, len(comment_ids)):
            child_id = comment_ids[i]
            expected_parent_id = comment_ids[i - 1]
            
            child_comment = all_comments[all_comments['id'] == child_id].iloc[0]
            assert child_comment['parent_id'] == expected_parent_id, \
                f"Comment {i} should have parent {expected_parent_id}, got {child_comment['parent_id']}"
    
    @given(
        st.text(min_size=1, max_size=20),  # username
        st.sampled_from(['timeline', 'figures', 'campaigns', 'article']),  # target_type
        st.text(min_size=1, max_size=20),  # target_id
        st.text(min_size=1, max_size=200),  # content
        st.integers(min_value=1, max_value=5)  # number of submissions
    )
    @settings(max_examples=20, deadline=None)
    def test_comment_persistence_consistency(
        self,
        username: str,
        target_type: str,
        target_id: str,
        content: str,
        num_submissions: int
    ):
        """
        Property: For any comment, multiple submissions with the same data 
        should result in multiple distinct comment records (no uniqueness constraint).
        
        Feature: platform-core, Property 9: Comment Data Persistence
        Validates: Requirements 4.2
        """
        # Get fresh system for this test
        comment_system = self._get_fresh_system()
        
        # Submit the same comment multiple times
        for i in range(num_submissions):
            success = comment_system.add_comment(
                username=username,
                target_type=target_type,
                target_id=target_id,
                content=content,
                parent_id=None
            )
            assert success is True, f"Submission {i + 1} should succeed"
        
        # Get all comments
        comments = comment_system.get_comments(
            target_type=target_type,
            target_id=target_id,
            approved_only=False
        )
        
        # Verify all submissions were persisted
        assert len(comments) == num_submissions, \
            f"Expected {num_submissions} comments, found {len(comments)}"
        
        # Verify all comments have the same data but different IDs
        comment_ids = set()
        for _, comment in comments.iterrows():
            assert comment['username'] == username, "Username should match"
            assert comment['content'] == content, "Content should match"
            assert comment['target_type'] == target_type, "Target type should match"
            assert comment['target_id'] == target_id, "Target ID should match"
            
            # Collect IDs to verify uniqueness
            comment_ids.add(comment['id'])
        
        # Verify all IDs are unique
        assert len(comment_ids) == num_submissions, \
            f"All {num_submissions} comments should have unique IDs"
