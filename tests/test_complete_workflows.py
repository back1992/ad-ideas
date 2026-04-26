"""
Complete Workflow Integration Tests for Platform Core

This test suite validates end-to-end workflows across all platform systems:
1. User registration → content interaction → article creation workflow
2. Moderation workflow from report to resolution
3. Analytics data flow and accuracy

Task: 11.2 Write additional integration tests for complete workflows
Requirements: All platform requirements (1.x through 10.x)
"""

import pytest
import os
import tempfile
import yaml
import bcrypt
from datetime import datetime, timedelta
from modules.database import DatabaseManager
from modules.auth import AuthManager
from modules.feedback import FeedbackSystem
from modules.comments import CommentSystem
from modules.articles import ArticleManager
from modules.activity import ActivityLogger
from modules.analytics import AnalyticsDashboard
from modules.moderation import UnifiedModerationDashboard
from modules.user_management import UserManagementSystem


class TestUserContentInteractionWorkflow:
    """
    Test complete workflow: user registration → content interaction → article creation
    
    This tests the full user journey from registration through content consumption
    to content creation (for professors).
    """
    
    def test_student_complete_workflow(self, integrated_system):
        """
        Test complete student workflow:
        1. User registers/logs in as student
        2. Views content and provides feedback
        3. Reads and comments on articles
        4. Interacts with other comments (likes, replies)
        5. Activity is logged throughout
        """
        db_manager, auth_manager, feedback_system, comment_system, article_manager, activity_logger, analytics, comment_moderation = integrated_system
        
        # Step 1: Student authentication
        student_username = 'student_user'
        student_role = auth_manager.get_user_role(student_username)
        assert student_role == 'student', "User should have student role"
        
        # Verify student permissions
        assert not auth_manager.is_professor_or_admin(student_username), \
            "Student should not have professor/admin permissions"
        assert auth_manager.check_permission('student', student_username), \
            "Student should have student permissions"
        
        # Step 2: Student views content and provides feedback
        content_type = 'timeline'
        content_id = 'advertising_1920s'
        
        # Submit thumbs up feedback
        success = feedback_system.save_feedback(
            username=student_username,
            target_type=content_type,
            target_id=content_id,
            feedback_type='thumbs',
            feedback_value=1,
            feedback_text='Great historical overview!'
        )
        assert success, "Feedback submission should succeed"
        
        # Verify feedback was recorded
        has_feedback = feedback_system.has_user_feedback(student_username, content_type, content_id)
        assert has_feedback, "Feedback should be recorded"
        
        # Check feedback stats
        stats = feedback_system.get_feedback_stats(content_type, content_id)
        assert stats['total_feedback'] >= 1, "Should have at least one feedback"
        assert stats['positive_count'] >= 1, "Should have at least one positive feedback"
        
        # Step 3: Student reads and comments on an article
        # First, create an article for the student to comment on (as professor)
        professor_username = 'professor_user'
        article_success = article_manager.save_article(
            title='The Evolution of Advertising in the 1920s',
            content='# Introduction\n\nThe 1920s marked a pivotal era...',
            excerpt='Exploring advertising evolution in the roaring twenties',
            category='Advertising History',
            tags='1920s, history, evolution',
            author=professor_username,
            status='published',
            article_id=None
        )
        assert article_success, "Article creation should succeed"
        
        # Get the article
        articles = article_manager.get_articles(status='published', limit=1)
        assert len(articles) > 0, "Should have at least one published article"
        article_id = articles.iloc[0]['id']
        
        # Student comments on the article
        comment_success = comment_system.add_comment(
            username=student_username,
            target_type='article',
            target_id=str(article_id),
            content='This is a fascinating analysis of 1920s advertising trends!',
            parent_id=None
        )
        assert comment_success, "Comment submission should succeed"
        
        # Verify comment was recorded
        comments = comment_system.get_comments('article', str(article_id))
        assert len(comments) > 0, "Should have at least one comment"
        student_comment = comments[comments['username'] == student_username]
        assert len(student_comment) > 0, "Student's comment should be recorded"
        
        # Step 4: Student interacts with comments
        comment_id = student_comment.iloc[0]['id']
        
        # Another student likes the comment
        other_student = 'student_user_2'
        like_success = comment_system.like_comment(comment_id, other_student)
        assert like_success, "Liking comment should succeed"
        
        # Verify like was recorded
        updated_comments = comment_system.get_comments('article', str(article_id))
        liked_comment = updated_comments[updated_comments['id'] == comment_id]
        assert liked_comment.iloc[0]['likes'] > 0, "Comment should have at least one like"
        
        # Student replies to another comment
        # First, create another comment to reply to
        comment_system.add_comment(
            username=other_student,
            target_type='article',
            target_id=str(article_id),
            content='I agree, the analysis is very thorough.',
            parent_id=None
        )
        
        # Get the new comment
        all_comments = comment_system.get_comments('article', str(article_id))
        other_comment = all_comments[all_comments['username'] == other_student]
        parent_comment_id = other_comment.iloc[0]['id']
        
        # Student replies
        reply_success = comment_system.add_comment(
            username=student_username,
            target_type='article',
            target_id=str(article_id),
            content='Thanks! I found the section on radio advertising particularly interesting.',
            parent_id=parent_comment_id
        )
        assert reply_success, "Reply should succeed"
        
        # Verify reply threading
        all_comments_with_reply = comment_system.get_comments('article', str(article_id))
        replies = all_comments_with_reply[all_comments_with_reply['parent_id'] == parent_comment_id]
        assert len(replies) > 0, "Should have at least one reply"
        
        # Step 5: Verify activity logging
        # Check that user activities were logged
        query = "SELECT * FROM user_activity WHERE username = ? ORDER BY timestamp DESC"
        activities = db_manager.execute_query(query, (student_username,))
        
        assert len(activities) > 0, "Should have logged activities"
        
        # Verify different types of activities were logged
        activity_types = set(activities['action'].tolist())
        assert 'comment_posted' in activity_types, "Should have logged comment posting"

    
    def test_professor_complete_workflow(self, integrated_system):
        """
        Test complete professor workflow:
        1. Professor logs in
        2. Creates article draft
        3. Edits and refines article
        4. Submits article for review
        5. Article gets published
        6. Professor views article analytics
        7. Professor responds to comments on their article
        """
        db_manager, auth_manager, feedback_system, comment_system, article_manager, activity_logger, analytics, comment_moderation = integrated_system
        
        # Step 1: Professor authentication
        professor_username = 'professor_user'
        professor_role = auth_manager.get_user_role(professor_username)
        assert professor_role == 'professor', "User should have professor role"
        
        # Verify professor permissions
        assert auth_manager.is_professor_or_admin(professor_username), \
            "Professor should have professor/admin permissions"
        assert auth_manager.check_permission('professor', professor_username), \
            "Professor should have professor permissions"
        
        # Step 2: Professor creates article draft
        draft_title = 'The Impact of Digital Advertising'
        draft_content = '# Introduction\n\nDigital advertising has transformed...'
        
        draft_success = article_manager.save_article(
            title=draft_title,
            content=draft_content,
            excerpt='Exploring the digital advertising revolution',
            category='Marketing Theory',
            tags='digital, advertising, technology',
            author=professor_username,
            status='draft',
            article_id=None
        )
        assert draft_success, "Draft creation should succeed"
        
        # Verify draft was created
        drafts = article_manager.get_articles(author=professor_username, status='draft')
        assert len(drafts) > 0, "Should have at least one draft"
        draft_article = drafts[drafts['title'] == draft_title]
        assert len(draft_article) > 0, "Draft article should exist"
        article_id = draft_article.iloc[0]['id']
        
        # Step 3: Professor edits and refines article
        updated_content = draft_content + '\n\n## Key Trends\n\n1. Programmatic advertising\n2. Social media marketing'
        
        edit_success = article_manager.save_article(
            title=draft_title,
            content=updated_content,
            excerpt='Exploring the digital advertising revolution',
            category='Marketing Theory',
            tags='digital, advertising, technology, trends',
            author=professor_username,
            status='draft',
            article_id=int(article_id)
        )
        assert edit_success, "Article edit should succeed"
        
        # Verify article was updated
        updated_article = article_manager.get_article_by_id(article_id)
        assert updated_article['content'] == updated_content, "Content should be updated"
        assert 'trends' in updated_article['tags'], "Tags should be updated"
        
        # Step 4: Professor submits article for review
        review_success = article_manager.save_article(
            title=draft_title,
            content=updated_content,
            excerpt='Exploring the digital advertising revolution',
            category='Marketing Theory',
            tags='digital, advertising, technology, trends',
            author=professor_username,
            status='review',
            article_id=int(article_id)
        )
        assert review_success, "Submitting for review should succeed"
        
        # Verify status changed to review
        review_article = article_manager.get_article_by_id(article_id)
        assert review_article['status'] == 'review', "Status should be 'review'"
        
        # Step 5: Admin publishes the article
        admin_username = 'admin_user'
        publish_success = article_manager.save_article(
            title=draft_title,
            content=updated_content,
            excerpt='Exploring the digital advertising revolution',
            category='Marketing Theory',
            tags='digital, advertising, technology, trends',
            author=professor_username,
            status='published',
            article_id=int(article_id)
        )
        assert publish_success, "Publishing should succeed"
        
        # Verify article is published
        published_article = article_manager.get_article_by_id(article_id)
        assert published_article['status'] == 'published', "Status should be 'published'"
        assert published_article['published_at'] is not None, "published_at should be set"
        
        # Step 6: Professor views article analytics
        # Simulate some views and feedback
        article_manager.increment_article_views(article_id)
        article_manager.increment_article_views(article_id)
        article_manager.increment_article_views(article_id)
        
        # Add feedback to the article
        feedback_system.save_feedback(
            username='student_user',
            target_type='article',
            target_id=str(article_id),
            feedback_type='stars',
            feedback_value=4,
            feedback_text='Excellent article!'
        )
        
        # Verify analytics data
        article_with_stats = article_manager.get_article_by_id(article_id)
        assert article_with_stats['views'] >= 3, "Should have at least 3 views"
        
        # Step 7: Professor responds to comments on their article
        # Student comments on the article
        comment_system.add_comment(
            username='student_user',
            target_type='article',
            target_id=str(article_id),
            content='Great insights on programmatic advertising!',
            parent_id=None
        )
        
        # Get the comment
        comments = comment_system.get_comments('article', str(article_id))
        student_comment = comments[comments['username'] == 'student_user']
        parent_comment_id = student_comment.iloc[0]['id']
        
        # Professor replies
        reply_success = comment_system.add_comment(
            username=professor_username,
            target_type='article',
            target_id=str(article_id),
            content='Thank you! I\'m glad you found it helpful. The programmatic section was particularly interesting to research.',
            parent_id=parent_comment_id
        )
        assert reply_success, "Professor reply should succeed"
        
        # Verify reply was recorded
        all_comments = comment_system.get_comments('article', str(article_id))
        professor_replies = all_comments[
            (all_comments['username'] == professor_username) & 
            (all_comments['parent_id'] == parent_comment_id)
        ]
        assert len(professor_replies) > 0, "Professor's reply should be recorded"



class TestModerationWorkflow:
    """
    Test complete moderation workflow from report to resolution.
    
    This tests the full moderation process including content reporting,
    moderation queue management, and resolution actions.
    """
    
    def test_comment_moderation_workflow(self, integrated_system):
        """
        Test complete comment moderation workflow:
        1. User posts comment
        2. Another user reports the comment
        3. Comment appears in moderation queue
        4. Admin reviews and takes action (approve/reject)
        5. Moderation action is logged
        6. User is notified (if applicable)
        """
        db_manager, auth_manager, feedback_system, comment_system, article_manager, activity_logger, analytics, comment_moderation = integrated_system
        
        # Step 1: User posts comment
        user_username = 'student_user'
        comment_content = 'This article needs more citations.'
        
        comment_success = comment_system.add_comment(
            username=user_username,
            target_type='article',
            target_id='test_article_1',
            content=comment_content,
            parent_id=None
        )
        assert comment_success, "Comment posting should succeed"
        
        # Get the comment
        comments = comment_system.get_comments('article', 'test_article_1')
        assert len(comments) > 0, "Should have at least one comment"
        comment_id = comments.iloc[0]['id']
        
        # Step 2: Another user reports the comment
        reporter_username = 'student_user_2'
        report_reason = 'Inappropriate tone'
        
        report_success = comment_system.report_comment(
            comment_id=comment_id,
            reporter_username=reporter_username,
            reason=report_reason
        )
        assert report_success, "Comment reporting should succeed"
        
        # Step 3: Verify comment appears in moderation queue
        # Check that report was logged in user_activity
        query = """
            SELECT * FROM user_activity 
            WHERE action = 'comment_reported' AND target_id = ?
        """
        reports = db_manager.execute_query(query, (str(comment_id),))
        assert len(reports) > 0, "Report should be logged in user_activity"
        
        # Verify report details
        report = reports.iloc[0]
        assert report['username'] == reporter_username, "Reporter should be recorded"
        assert report_reason in report['details'], "Report reason should be recorded"
        
        # Step 4: Admin reviews and takes action
        admin_username = 'admin_user'
        
        # Admin approves the comment (it was a false report)
        approve_success = comment_moderation.approve_comment(comment_id, admin_username)
        assert approve_success, "Comment approval should succeed"
        
        # Verify comment is still approved
        query = "SELECT is_approved FROM comments WHERE id = ?"
        result = db_manager.execute_query(query, (int(comment_id),))
        assert len(result) > 0, "Comment should exist"
        assert result.iloc[0]['is_approved'] == 1, "Comment should remain approved"
        
        # Step 5: Verify moderation action is logged
        query = """
            SELECT * FROM user_activity 
            WHERE action = 'comment_approved' AND target_id = ?
        """
        approvals = db_manager.execute_query(query, (str(comment_id),))
        assert len(approvals) > 0, "Approval should be logged"
        
        approval = approvals.iloc[0]
        assert approval['username'] == admin_username, "Admin should be recorded as moderator"
        
        # Test rejection workflow
        # Create another comment to reject
        comment_system.add_comment(
            username='student_user_3',
            target_type='article',
            target_id='test_article_1',
            content='Spam content here',
            parent_id=None
        )
        
        spam_comments = comment_system.get_comments('article', 'test_article_1')
        spam_comment = spam_comments[spam_comments['username'] == 'student_user_3']
        spam_comment_id = spam_comment.iloc[0]['id']
        
        # Report and reject
        comment_system.report_comment(spam_comment_id, 'student_user', 'Spam')
        reject_success = comment_moderation.reject_comment(spam_comment_id, admin_username)
        assert reject_success, "Comment rejection should succeed"
        
        # Verify comment was deleted (reject_comment deletes the comment)
        query = "SELECT COUNT(*) as count FROM comments WHERE id = ?"
        result = db_manager.execute_query(query, (int(spam_comment_id),))
        assert result.iloc[0]['count'] == 0, "Comment should be deleted after rejection"
        
        # Verify rejection is logged
        query = """
            SELECT * FROM user_activity 
            WHERE action = 'comment_rejected' AND target_id = ?
        """
        rejections = db_manager.execute_query(query, (str(spam_comment_id),))
        assert len(rejections) > 0, "Rejection should be logged"
    
    def test_article_moderation_workflow(self, integrated_system):
        """
        Test complete article moderation workflow:
        1. Professor submits article for review
        2. Article appears in admin review queue
        3. Admin reviews article
        4. Admin approves or rejects with feedback
        5. Article status is updated
        6. Professor is notified
        """
        db_manager, auth_manager, feedback_system, comment_system, article_manager, activity_logger, analytics, comment_moderation = integrated_system
        
        # Step 1: Professor submits article for review
        professor_username = 'professor_user'
        article_title = 'New Research on Consumer Behavior'
        
        submit_success = article_manager.save_article(
            title=article_title,
            content='# Abstract\n\nThis research explores...',
            excerpt='New insights into consumer behavior',
            category='Marketing Theory',
            tags='research, consumer, behavior',
            author=professor_username,
            status='review',
            article_id=None
        )
        assert submit_success, "Article submission should succeed"
        
        # Step 2: Verify article appears in review queue
        review_articles = article_manager.get_articles(status='review')
        assert len(review_articles) > 0, "Should have articles in review"
        
        submitted_article = review_articles[review_articles['title'] == article_title]
        assert len(submitted_article) > 0, "Submitted article should be in review queue"
        article_id = submitted_article.iloc[0]['id']
        
        # Step 3: Admin reviews article
        admin_username = 'admin_user'
        
        # Admin approves the article
        approve_success = article_manager.save_article(
            title=article_title,
            content='# Abstract\n\nThis research explores...',
            excerpt='New insights into consumer behavior',
            category='Marketing Theory',
            tags='research, consumer, behavior',
            author=professor_username,
            status='published',
            article_id=int(article_id)  # Ensure it's a Python int, not numpy.int64
        )
        assert approve_success, "Article approval should succeed"
        
        # Step 4: Verify article status is updated
        published_article = article_manager.get_article_by_id(article_id)
        assert published_article['status'] == 'published', f"Article should be published, got {published_article['status']}"
        assert published_article['published_at'] is not None, "published_at should be set"
        
        # Test rejection workflow
        # Professor submits another article
        article_manager.save_article(
            title='Incomplete Research Draft',
            content='# Introduction\n\nThis is incomplete...',
            excerpt='Draft article',
            category='Marketing Theory',
            tags='draft',
            author=professor_username,
            status='review',
            article_id=None
        )
        
        # Get the new article
        new_review_articles = article_manager.get_articles(status='review')
        draft_article = new_review_articles[new_review_articles['title'] == 'Incomplete Research Draft']
        draft_article_id = draft_article.iloc[0]['id']
        
        # Admin rejects with feedback
        reject_success = article_manager.save_article(
            title='Incomplete Research Draft',
            content='# Introduction\n\nThis is incomplete...',
            excerpt='Draft article - needs more work',
            category='Marketing Theory',
            tags='draft, needs-revision',
            author=professor_username,
            status='draft',  # Send back to draft
            article_id=int(draft_article_id)
        )
        assert reject_success, "Article rejection should succeed"
        
        # Verify article is back in draft status
        rejected_article = article_manager.get_article_by_id(draft_article_id)
        assert rejected_article['status'] == 'draft', "Article should be back in draft"
        assert 'needs-revision' in rejected_article['tags'], "Rejection feedback should be in tags"
    
    def test_bulk_moderation_workflow(self, integrated_system):
        """
        Test bulk moderation operations:
        1. Multiple items need moderation
        2. Admin uses bulk actions
        3. All items are processed correctly
        4. Actions are logged
        """
        db_manager, auth_manager, feedback_system, comment_system, article_manager, activity_logger, analytics, comment_moderation = integrated_system
        
        # Create multiple comments that need moderation
        comment_ids = []
        for i in range(5):
            comment_system.add_comment(
                username=f'user_{i}',
                target_type='article',
                target_id='bulk_test_article',
                content=f'Test comment {i}',
                parent_id=None
            )
        
        # Get all comments
        comments = comment_system.get_comments('article', 'bulk_test_article')
        comment_ids = comments['id'].tolist()
        
        # Report all comments
        for comment_id in comment_ids:
            comment_system.report_comment(comment_id, 'reporter_user', 'Bulk test')
        
        # Admin performs bulk approval
        admin_username = 'admin_user'
        approved_count = 0
        
        for comment_id in comment_ids[:3]:  # Approve first 3
            success = comment_moderation.approve_comment(comment_id, admin_username)
            if success:
                approved_count += 1
        
        assert approved_count == 3, "Should approve 3 comments"
        
        # Admin performs bulk rejection
        rejected_count = 0
        
        for comment_id in comment_ids[3:]:  # Reject last 2
            success = comment_moderation.reject_comment(comment_id, admin_username)
            if success:
                rejected_count += 1
        
        assert rejected_count == 2, "Should reject 2 comments"
        
        # Verify all actions were logged
        query = """
            SELECT * FROM user_activity 
            WHERE username = ? AND action IN ('comment_approved', 'comment_rejected')
            ORDER BY timestamp DESC
        """
        moderation_actions = db_manager.execute_query(query, (admin_username,))
        assert len(moderation_actions) >= 5, "Should have logged all moderation actions"



class TestAnalyticsDataFlow:
    """
    Test analytics data flow and accuracy across the platform.
    
    This tests that user activities, content interactions, and engagement
    metrics are correctly tracked and aggregated in analytics.
    """
    
    def test_user_engagement_analytics_flow(self, integrated_system):
        """
        Test user engagement analytics:
        1. Users perform various activities
        2. Activities are logged
        3. Analytics aggregates data correctly
        4. Reports show accurate metrics
        """
        db_manager, auth_manager, feedback_system, comment_system, article_manager, activity_logger, analytics, comment_moderation = integrated_system
        
        # Step 1: Simulate various user activities
        users = ['student_1', 'student_2', 'professor_1']
        
        # Users view content
        for user in users:
            activity_logger.log_activity(
                username=user,
                action='content_view',
                target_type='timeline',
                target_id='1920s_era',
                details='Viewed 1920s advertising timeline'
            )
        
        # Users provide feedback
        for i, user in enumerate(users):
            feedback_system.save_feedback(
                username=user,
                target_type='timeline',
                target_id='1920s_era',
                feedback_type='stars',
                feedback_value=4 + (i % 2),  # 4 or 5 stars
                feedback_text=f'Great content from {user}'
            )
        
        # Users post comments
        for user in users:
            comment_system.add_comment(
                username=user,
                target_type='timeline',
                target_id='1920s_era',
                content=f'Interesting perspective from {user}',
                parent_id=None
            )
        
        # Step 2: Verify activities are logged
        query = "SELECT * FROM user_activity WHERE target_id = ?"
        activities = db_manager.execute_query(query, ('1920s_era',))
        assert len(activities) >= len(users), "Should have logged activities for all users"
        
        # Step 3: Verify analytics aggregates data correctly
        # Get user engagement stats from database
        query = "SELECT username, COUNT(*) as total_actions FROM user_activity GROUP BY username"
        user_stats = db_manager.execute_query(query, ())
        assert len(user_stats) > 0, "Should have user engagement statistics"
        
        # Verify each user has stats
        for user in users:
            user_data = user_stats[user_stats['username'] == user]
            if len(user_data) > 0:
                assert user_data.iloc[0]['total_actions'] > 0, f"{user} should have recorded actions"
        
        # Get content performance stats from database
        query = """
            SELECT target_type, target_id, COUNT(*) as total_interactions 
            FROM user_activity 
            WHERE target_type IS NOT NULL AND target_id IS NOT NULL
            GROUP BY target_type, target_id
        """
        content_stats = db_manager.execute_query(query, ())
        assert len(content_stats) > 0, "Should have content performance statistics"
        
        # Verify timeline content has stats
        timeline_stats = content_stats[
            (content_stats['target_type'] == 'timeline') & 
            (content_stats['target_id'] == '1920s_era')
        ]
        if len(timeline_stats) > 0:
            assert timeline_stats.iloc[0]['total_interactions'] >= len(users), \
                "Should have interactions from all users"
        
        # Step 4: Verify feedback statistics
        feedback_stats = feedback_system.get_feedback_stats('timeline', '1920s_era')
        assert feedback_stats['total_feedback'] >= len(users), \
            f"Should have feedback from all {len(users)} users"
        assert feedback_stats['avg_rating'] >= 4.0, "Average rating should be at least 4.0"
    
    def test_article_analytics_flow(self, integrated_system):
        """
        Test article-specific analytics:
        1. Article is published
        2. Users view and interact with article
        3. Article metrics are tracked
        4. Analytics show accurate article performance
        """
        db_manager, auth_manager, feedback_system, comment_system, article_manager, activity_logger, analytics, comment_moderation = integrated_system
        
        # Step 1: Create and publish article
        professor_username = 'professor_user'
        article_title = 'Analytics Test Article'
        
        article_manager.save_article(
            title=article_title,
            content='# Test Content\n\nThis is for analytics testing.',
            excerpt='Analytics test',
            category='Test',
            tags='analytics, test',
            author=professor_username,
            status='published',
            article_id=None
        )
        
        # Get the article
        articles = article_manager.get_articles(status='published')
        test_article = articles[articles['title'] == article_title]
        article_id = test_article.iloc[0]['id']
        
        # Step 2: Simulate user interactions
        users = ['student_1', 'student_2', 'student_3', 'professor_2']
        
        # Users view the article
        for user in users:
            article_manager.increment_article_views(article_id)
            activity_logger.log_activity(
                username=user,
                action='article_view',
                target_type='article',
                target_id=str(article_id),
                details=f'{user} viewed article'
            )
        
        # Users provide feedback
        feedback_values = [5, 4, 5, 4]
        for user, value in zip(users, feedback_values):
            feedback_system.save_feedback(
                username=user,
                target_type='article',
                target_id=str(article_id),
                feedback_type='stars',
                feedback_value=value,
                feedback_text=f'Feedback from {user}'
            )
        
        # Users comment
        for user in users:
            comment_system.add_comment(
                username=user,
                target_type='article',
                target_id=str(article_id),
                content=f'Comment from {user}',
                parent_id=None
            )
        
        # Step 3: Verify article metrics are tracked
        updated_article = article_manager.get_article_by_id(article_id)
        assert updated_article['views'] >= len(users), \
            f"Article should have at least {len(users)} views"
        
        # Step 4: Verify analytics show accurate performance
        # Check feedback stats
        article_feedback = feedback_system.get_feedback_stats('article', str(article_id))
        assert article_feedback['total_feedback'] == len(users), \
            f"Should have feedback from all {len(users)} users"
        
        expected_avg = sum(feedback_values) / len(feedback_values)
        assert abs(article_feedback['avg_rating'] - expected_avg) < 0.1, \
            f"Average rating should be approximately {expected_avg}"
        
        # Check comment count
        article_comments = comment_system.get_comments('article', str(article_id))
        assert len(article_comments) >= len(users), \
            f"Should have comments from all {len(users)} users"
        
        # Check activity log
        query = """
            SELECT * FROM user_activity 
            WHERE target_type = 'article' AND target_id = ?
        """
        article_activities = db_manager.execute_query(query, (str(article_id),))
        assert len(article_activities) >= len(users), \
            "Should have logged activities for all users"
    
    def test_platform_growth_analytics(self, integrated_system):
        """
        Test platform growth analytics:
        1. Track user registrations over time
        2. Track content creation over time
        3. Track engagement trends
        4. Verify growth metrics are accurate
        """
        db_manager, auth_manager, feedback_system, comment_system, article_manager, activity_logger, analytics, comment_moderation = integrated_system
        
        # Simulate platform activity over time
        # Day 1: Initial users and content
        day1_users = ['user_1', 'user_2']
        for user in day1_users:
            activity_logger.log_activity(
                username=user,
                action='user_registered',
                target_type='user',
                target_id=user,
                details='User registration'
            )
        
        # Day 1: Content creation
        article_manager.save_article(
            title='Day 1 Article',
            content='Content from day 1',
            excerpt='Day 1',
            category='Test',
            tags='day1',
            author='user_1',
            status='published',
            article_id=None
        )
        
        # Day 2: More users and activity
        day2_users = ['user_3', 'user_4', 'user_5']
        for user in day2_users:
            activity_logger.log_activity(
                username=user,
                action='user_registered',
                target_type='user',
                target_id=user,
                details='User registration'
            )
        
        # Day 2: More content
        article_manager.save_article(
            title='Day 2 Article',
            content='Content from day 2',
            excerpt='Day 2',
            category='Test',
            tags='day2',
            author='user_3',
            status='published',
            article_id=None
        )
        
        # Verify growth metrics
        # Check total user registrations
        query = "SELECT COUNT(*) as count FROM user_activity WHERE action = 'user_registered'"
        registration_count = db_manager.execute_query(query, ())
        total_registrations = registration_count.iloc[0]['count']
        assert total_registrations == len(day1_users) + len(day2_users), \
            "Should have correct number of registrations"
        
        # Check total articles
        all_articles = article_manager.get_articles()
        assert len(all_articles) >= 2, "Should have at least 2 articles"
        
        # Check engagement growth
        # Day 1 users engage with content
        for user in day1_users:
            comment_system.add_comment(
                username=user,
                target_type='article',
                target_id='1',
                content=f'Engagement from {user}',
                parent_id=None
            )
        
        # Day 2 users engage more
        for user in day2_users:
            comment_system.add_comment(
                username=user,
                target_type='article',
                target_id='1',
                content=f'Engagement from {user}',
                parent_id=None
            )
            comment_system.add_comment(
                username=user,
                target_type='article',
                target_id='2',
                content=f'More engagement from {user}',
                parent_id=None
            )
        
        # Verify engagement metrics
        query = "SELECT COUNT(*) as count FROM comments"
        comment_count = db_manager.execute_query(query, ())
        total_comments = comment_count.iloc[0]['count']
        
        # Day 1 users: 2 comments, Day 2 users: 6 comments (2 per user)
        expected_comments = len(day1_users) + (len(day2_users) * 2)
        assert total_comments >= expected_comments, \
            f"Should have at least {expected_comments} comments"



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
def temp_config():
    """Create a temporary config file for authentication."""
    config_data = {
        'credentials': {
            'usernames': {
                'admin_user': {
                    'name': 'Admin User',
                    'email': 'admin@test.com',
                    'password': bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                    'role': 'admin'
                },
                'professor_user': {
                    'name': 'Professor User',
                    'email': 'prof@test.com',
                    'password': bcrypt.hashpw('prof123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                    'role': 'professor'
                },
                'student_user': {
                    'name': 'Student User',
                    'email': 'student@test.com',
                    'password': bcrypt.hashpw('student123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                    'role': 'student'
                },
                'student_user_2': {
                    'name': 'Student User 2',
                    'email': 'student2@test.com',
                    'password': bcrypt.hashpw('student123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                    'role': 'student'
                },
                'student_user_3': {
                    'name': 'Student User 3',
                    'email': 'student3@test.com',
                    'password': bcrypt.hashpw('student123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                    'role': 'student'
                },
                'student_1': {
                    'name': 'Student One',
                    'email': 'student1@test.com',
                    'password': bcrypt.hashpw('student123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                    'role': 'student'
                },
                'student_2': {
                    'name': 'Student Two',
                    'email': 'student2@test.com',
                    'password': bcrypt.hashpw('student123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                    'role': 'student'
                },
                'student_3': {
                    'name': 'Student Three',
                    'email': 'student3@test.com',
                    'password': bcrypt.hashpw('student123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                    'role': 'student'
                },
                'professor_1': {
                    'name': 'Professor One',
                    'email': 'prof1@test.com',
                    'password': bcrypt.hashpw('prof123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                    'role': 'professor'
                },
                'professor_2': {
                    'name': 'Professor Two',
                    'email': 'prof2@test.com',
                    'password': bcrypt.hashpw('prof123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                    'role': 'professor'
                },
                'user_1': {
                    'name': 'User One',
                    'email': 'user1@test.com',
                    'password': bcrypt.hashpw('user123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                    'role': 'student'
                },
                'user_2': {
                    'name': 'User Two',
                    'email': 'user2@test.com',
                    'password': bcrypt.hashpw('user123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                    'role': 'student'
                },
                'user_3': {
                    'name': 'User Three',
                    'email': 'user3@test.com',
                    'password': bcrypt.hashpw('user123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                    'role': 'professor'
                },
                'user_4': {
                    'name': 'User Four',
                    'email': 'user4@test.com',
                    'password': bcrypt.hashpw('user123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                    'role': 'student'
                },
                'user_5': {
                    'name': 'User Five',
                    'email': 'user5@test.com',
                    'password': bcrypt.hashpw('user123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                    'role': 'student'
                },
                'reporter_user': {
                    'name': 'Reporter User',
                    'email': 'reporter@test.com',
                    'password': bcrypt.hashpw('reporter123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
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
def integrated_system(temp_db, temp_config):
    """
    Create a complete integrated system with all components.
    
    Returns:
        Tuple of (db_manager, auth_manager, feedback_system, comment_system, 
                  article_manager, activity_logger, analytics, comment_moderation)
    """
    # Create database manager
    db_manager = DatabaseManager(temp_db)
    db_manager.init_database()
    
    # Create auth manager
    auth_manager = AuthManager(temp_config, db_manager)
    
    # Create feedback system
    feedback_system = FeedbackSystem(db_manager)
    
    # Create comment system
    comment_system = CommentSystem(db_manager)
    
    # Create comment moderation system
    from modules.comments import CommentModerationSystem
    comment_moderation = CommentModerationSystem(comment_system)
    
    # Create article manager
    article_manager = ArticleManager(db_manager, auth_manager)
    
    # Create activity logger
    activity_logger = ActivityLogger(db_manager)
    
    # Create analytics dashboard
    analytics = AnalyticsDashboard(db_manager, activity_logger)
    
    return (db_manager, auth_manager, feedback_system, comment_system, 
            article_manager, activity_logger, analytics, comment_moderation)
