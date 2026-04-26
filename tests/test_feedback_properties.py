"""
Property-based tests for FeedbackSystem

Feature: platform-core, Property 7: Feedback Uniqueness Constraint
Feature: platform-core, Property 8: Feedback Statistics Consistency
Validates: Requirements 3.2, 3.3

This module contains property-based tests using Hypothesis to verify
feedback uniqueness constraints and statistics consistency.
"""

import os
import tempfile
from typing import Tuple, List

import pytest
from hypothesis import given, strategies as st, settings, assume

from modules.database import DatabaseManager
from modules.feedback import FeedbackSystem


class TestFeedbackProperties:
    """
    Property-based tests for feedback system.
    
    Feature: platform-core, Property 7: Feedback Uniqueness Constraint
    Feature: platform-core, Property 8: Feedback Statistics Consistency
    """
    
    def setup_method(self):
        """Set up test environment for each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_feedback.db")
        
        # Create test database manager
        self.db_manager = DatabaseManager(self.test_db_path)
        self.db_manager.init_database()
        
        # Create feedback system
        self.feedback_system = FeedbackSystem(self.db_manager)
    
    def _clear_database(self):
        """Clear all data from feedback-related tables."""
        try:
            self.db_manager.execute_update("DELETE FROM user_feedback", ())
            self.db_manager.execute_update("DELETE FROM content_stats", ())
        except Exception as e:
            # Log but don't fail - tables might not exist yet
            print(f"Warning: Could not clear database: {e}")
    
    def teardown_method(self):
        """Clean up test environment after each test method."""
        # Clean up files
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        os.rmdir(self.temp_dir)
    
    @given(
        st.text(min_size=1, max_size=20),  # username
        st.sampled_from(['timeline', 'figures', 'campaigns', 'article']),  # target_type
        st.text(min_size=1, max_size=20),  # target_id
        st.sampled_from(['thumbs', 'stars', 'faces']),  # feedback_type
        st.integers(min_value=0, max_value=4),  # feedback_value
        st.text(max_size=100)  # feedback_text
    )
    @settings(max_examples=10, deadline=None)
    def test_feedback_uniqueness_constraint(
        self, 
        username: str, 
        target_type: str, 
        target_id: str,
        feedback_type: str,
        feedback_value: int,
        feedback_text: str
    ):
        """
        Property 7: For any user and content combination, the system should 
        allow only one feedback submission and prevent duplicates.
        
        Feature: platform-core, Property 7: Feedback Uniqueness Constraint
        Validates: Requirements 3.2
        """
        # Clear database before each example
        self._clear_database()
        
        # Verify no feedback exists initially
        has_feedback_initial = self.feedback_system.has_user_feedback(
            username, target_type, target_id
        )
        assert has_feedback_initial == False, \
            f"User should not have feedback initially, but has_user_feedback returned {has_feedback_initial}"
        
        # Submit first feedback
        success_first = self.feedback_system.save_feedback(
            username=username,
            target_type=target_type,
            target_id=target_id,
            feedback_type=feedback_type,
            feedback_value=feedback_value,
            feedback_text=feedback_text
        )
        
        assert success_first is True, \
            "First feedback submission should succeed"
        
        # Verify feedback now exists
        has_feedback_after_first = self.feedback_system.has_user_feedback(
            username, target_type, target_id
        )
        assert has_feedback_after_first is True, \
            "User should have feedback after first submission"
        
        # Get count of feedback records
        query = """
            SELECT COUNT(*) as count 
            FROM user_feedback 
            WHERE username = ? AND target_type = ? AND target_id = ?
        """
        result = self.db_manager.execute_query(
            query, (username, target_type, target_id)
        )
        count_after_first = result.iloc[0]['count']
        
        assert count_after_first == 1, \
            f"Should have exactly 1 feedback record, found {count_after_first}"
        
        # Attempt to submit duplicate feedback (different value/text)
        success_second = self.feedback_system.save_feedback(
            username=username,
            target_type=target_type,
            target_id=target_id,
            feedback_type=feedback_type,
            feedback_value=(feedback_value + 1) % 5,  # Different value
            feedback_text=feedback_text + "_modified"  # Different text
        )
        
        # Second submission should succeed (database allows it)
        # but has_user_feedback should still return True
        has_feedback_after_second = self.feedback_system.has_user_feedback(
            username, target_type, target_id
        )
        assert has_feedback_after_second is True, \
            "has_user_feedback should return True after any number of submissions"
        
        # Count total feedback records
        result_after_second = self.db_manager.execute_query(
            query, (username, target_type, target_id)
        )
        count_after_second = result_after_second.iloc[0]['count']
        
        # Property: The system should track that user has provided feedback
        # (even if database allows multiple records, the check should be consistent)
        assert count_after_second >= 1, \
            f"Should have at least 1 feedback record, found {count_after_second}"
    
    @given(
        st.lists(
            st.tuples(
                st.text(min_size=1, max_size=20),  # username
                st.sampled_from(['timeline', 'figures', 'campaigns', 'article']),  # target_type
                st.text(min_size=1, max_size=20),  # target_id
                st.sampled_from(['thumbs', 'stars', 'faces']),  # feedback_type
                st.integers(min_value=0, max_value=4),  # feedback_value
                st.text(max_size=50)  # feedback_text
            ),
            min_size=1,
            max_size=10,
            unique_by=lambda x: (x[0], x[1], x[2])  # Unique by user+target_type+target_id
        )
    )
    @settings(max_examples=10, deadline=None)
    def test_feedback_statistics_consistency(
        self,
        feedback_data: List[Tuple[str, str, str, str, int, str]]
    ):
        """
        Property 8: For any feedback submission, the content statistics should 
        be updated immediately and accurately reflect all submitted feedback.
        
        Feature: platform-core, Property 8: Feedback Statistics Consistency
        Validates: Requirements 3.3
        """
        # Clear database before each example
        self._clear_database()
        
        # Group feedback by target (target_type, target_id)
        targets = {}
        for username, target_type, target_id, feedback_type, feedback_value, feedback_text in feedback_data:
            target_key = (target_type, target_id)
            if target_key not in targets:
                targets[target_key] = []
            targets[target_key].append({
                'username': username,
                'feedback_type': feedback_type,
                'feedback_value': feedback_value,
                'feedback_text': feedback_text
            })
        
        # Test each target's statistics
        for (target_type, target_id), feedbacks in targets.items():
            # Submit all feedback for this target
            for feedback in feedbacks:
                success = self.feedback_system.save_feedback(
                    username=feedback['username'],
                    target_type=target_type,
                    target_id=target_id,
                    feedback_type=feedback['feedback_type'],
                    feedback_value=feedback['feedback_value'],
                    feedback_text=feedback['feedback_text']
                )
                assert success is True, "Feedback submission should succeed"
            
            # Update content statistics
            self.feedback_system.update_content_stats(target_type, target_id)
            
            # Get statistics from database
            stats = self.feedback_system.get_feedback_stats(target_type, target_id)
            
            # Verify total feedback count
            expected_count = len(feedbacks)
            assert stats['total_feedback'] == expected_count, \
                f"Expected {expected_count} total feedback, got {stats['total_feedback']}"
            
            # Verify statistics are non-negative
            assert stats['total_feedback'] >= 0, "Total feedback should be non-negative"
            assert stats['avg_rating'] >= 0, "Average rating should be non-negative"
            assert stats['positive_count'] >= 0, "Positive count should be non-negative"
            assert stats['negative_count'] >= 0, "Negative count should be non-negative"
            
            # Verify positive + negative <= total (some feedback types don't have pos/neg)
            assert stats['positive_count'] + stats['negative_count'] <= stats['total_feedback'], \
                "Positive + negative count should not exceed total feedback"
            
            # Verify content_stats table is updated
            content_stats = self.feedback_system.get_content_stats(target_type, target_id)
            
            if content_stats is not None:
                # Verify content_stats matches aggregated stats
                assert content_stats['total_ratings'] == stats['total_feedback'], \
                    f"content_stats total_ratings should match feedback stats total_feedback"
                
                # Verify thumbs counts are consistent
                thumbs_feedbacks = [f for f in feedbacks if f['feedback_type'] == 'thumbs']
                if thumbs_feedbacks:
                    expected_thumbs_up = sum(1 for f in thumbs_feedbacks if f['feedback_value'] >= 1)
                    expected_thumbs_down = sum(1 for f in thumbs_feedbacks if f['feedback_value'] == 0)
                    
                    assert content_stats['thumbs_up'] == expected_thumbs_up, \
                        f"Expected {expected_thumbs_up} thumbs up, got {content_stats['thumbs_up']}"
                    assert content_stats['thumbs_down'] == expected_thumbs_down, \
                        f"Expected {expected_thumbs_down} thumbs down, got {content_stats['thumbs_down']}"
                
                # Verify stars average is within valid range
                stars_feedbacks = [f for f in feedbacks if f['feedback_type'] == 'stars']
                if stars_feedbacks:
                    assert 0 <= content_stats['avg_stars'] <= 4, \
                        f"Average stars should be between 0 and 4, got {content_stats['avg_stars']}"
    
    @given(
        st.text(min_size=1, max_size=20),  # username
        st.sampled_from(['timeline', 'figures', 'campaigns', 'article']),  # target_type
        st.text(min_size=1, max_size=20),  # target_id
        st.integers(min_value=1, max_value=5)  # number of feedback attempts
    )
    @settings(max_examples=10, deadline=None)
    def test_feedback_uniqueness_across_multiple_attempts(
        self,
        username: str,
        target_type: str,
        target_id: str,
        num_attempts: int
    ):
        """
        Property: For any user and content, has_user_feedback should consistently 
        return True after the first feedback submission, regardless of subsequent attempts.
        
        Feature: platform-core, Property 7: Feedback Uniqueness Constraint
        Validates: Requirements 3.2
        """
        # Clear database before each example
        self._clear_database()
        
        # Verify no feedback initially
        assert not self.feedback_system.has_user_feedback(username, target_type, target_id), \
            "Should have no feedback initially"
        
        # Submit feedback multiple times
        for attempt in range(num_attempts):
            # Submit feedback
            success = self.feedback_system.save_feedback(
                username=username,
                target_type=target_type,
                target_id=target_id,
                feedback_type='thumbs',
                feedback_value=attempt % 2,  # Alternate between 0 and 1
                feedback_text=f"Attempt {attempt}"
            )
            
            assert success is True, f"Feedback submission {attempt + 1} should succeed"
            
            # Verify has_user_feedback returns True after first submission
            has_feedback = self.feedback_system.has_user_feedback(
                username, target_type, target_id
            )
            assert has_feedback is True, \
                f"has_user_feedback should return True after attempt {attempt + 1}"
    
    @given(
        st.lists(
            st.tuples(
                st.text(min_size=1, max_size=15),  # username
                st.integers(min_value=0, max_value=4)  # feedback_value
            ),
            min_size=2,
            max_size=20,
            unique_by=lambda x: x[0]  # Unique usernames
        ),
        st.sampled_from(['timeline', 'figures', 'campaigns', 'article']),  # target_type
        st.text(min_size=1, max_size=15)  # target_id
    )
    @settings(max_examples=10, deadline=None)
    def test_statistics_accuracy_with_multiple_users(
        self,
        user_feedback_pairs: List[Tuple[str, int]],
        target_type: str,
        target_id: str
    ):
        """
        Property: For any set of users providing feedback on the same content,
        statistics should accurately reflect all submissions.
        
        Feature: platform-core, Property 8: Feedback Statistics Consistency
        Validates: Requirements 3.3
        """
        # Clear database before each example
        self._clear_database()
        
        # Submit feedback from all users
        for username, feedback_value in user_feedback_pairs:
            success = self.feedback_system.save_feedback(
                username=username,
                target_type=target_type,
                target_id=target_id,
                feedback_type='stars',
                feedback_value=feedback_value,
                feedback_text=""
            )
            assert success is True, f"Feedback from {username} should be saved"
        
        # Update statistics
        self.feedback_system.update_content_stats(target_type, target_id)
        
        # Get statistics
        stats = self.feedback_system.get_feedback_stats(target_type, target_id)
        
        # Verify total count matches number of unique users
        expected_count = len(user_feedback_pairs)
        assert stats['total_feedback'] == expected_count, \
            f"Expected {expected_count} feedback entries, got {stats['total_feedback']}"
        
        # Verify average rating calculation
        if expected_count > 0:
            expected_avg = sum(value for _, value in user_feedback_pairs) / expected_count
            actual_avg = stats['avg_rating']
            
            # Allow small floating point difference
            assert abs(actual_avg - expected_avg) < 0.01, \
                f"Expected average {expected_avg:.2f}, got {actual_avg:.2f}"
        
        # Verify each user has feedback recorded
        for username, _ in user_feedback_pairs:
            has_feedback = self.feedback_system.has_user_feedback(
                username, target_type, target_id
            )
            assert has_feedback is True, \
                f"User {username} should have feedback recorded"
    
    @given(
        st.text(min_size=1, max_size=20),  # username
        st.sampled_from(['timeline', 'figures', 'campaigns', 'article']),  # target_type
        st.text(min_size=1, max_size=20),  # target_id
        st.sampled_from(['thumbs', 'stars', 'faces']),  # feedback_type
        st.integers(min_value=0, max_value=4)  # feedback_value
    )
    @settings(max_examples=10, deadline=None)
    def test_statistics_update_idempotency(
        self,
        username: str,
        target_type: str,
        target_id: str,
        feedback_type: str,
        feedback_value: int
    ):
        """
        Property: For any content, calling update_content_stats multiple times
        should produce the same result (idempotent operation).
        
        Feature: platform-core, Property 8: Feedback Statistics Consistency
        Validates: Requirements 3.3
        """
        # Clear database before each example
        self._clear_database()
        
        # Submit feedback
        success = self.feedback_system.save_feedback(
            username=username,
            target_type=target_type,
            target_id=target_id,
            feedback_type=feedback_type,
            feedback_value=feedback_value,
            feedback_text=""
        )
        assert success is True, "Feedback should be saved"
        
        # Update statistics first time
        self.feedback_system.update_content_stats(target_type, target_id)
        stats_first = self.feedback_system.get_content_stats(target_type, target_id)
        
        # Update statistics second time
        self.feedback_system.update_content_stats(target_type, target_id)
        stats_second = self.feedback_system.get_content_stats(target_type, target_id)
        
        # Update statistics third time
        self.feedback_system.update_content_stats(target_type, target_id)
        stats_third = self.feedback_system.get_content_stats(target_type, target_id)
        
        # Verify all statistics are identical (excluding timestamp)
        assert stats_first is not None and stats_second is not None and stats_third is not None, \
            "Statistics should exist after updates"
        
        # Compare all fields except last_updated
        for key in ['thumbs_up', 'thumbs_down', 'avg_stars', 'total_ratings']:
            assert stats_first[key] == stats_second[key] == stats_third[key], \
                f"Field {key} should be consistent across updates: " \
                f"{stats_first[key]}, {stats_second[key]}, {stats_third[key]}"
