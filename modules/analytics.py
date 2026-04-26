"""
Analytics Dashboard System for 广告思想简史 Platform

This module provides comprehensive analytics and reporting functionality
for administrators to monitor platform usage, user engagement, and content performance.
"""

import streamlit as st
import logging
from utils.logger import create_logger
import pandas as pd
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from modules.database import DatabaseManager
from modules.activity import ActivityLogger


class AnalyticsDashboard:
    """
    Comprehensive analytics dashboard for platform administrators.
    
    Provides user engagement statistics, content performance metrics,
    and platform growth reports with interactive visualizations.
    """
    
    def __init__(self, db_manager: DatabaseManager, activity_logger: ActivityLogger):
        """
        Initialize AnalyticsDashboard with database and activity logger.
        
        Args:
            db_manager: Database manager instance
            activity_logger: Activity logger instance
        """
        self.db_manager = db_manager
        self.activity_logger = activity_logger
        self.logger = create_logger('AnalyticsDashboard')
        
    
    def show_dashboard(self, admin_username: str) -> None:
        """
        Display complete analytics dashboard for administrators.
        
        Args:
            admin_username: Username of administrator viewing dashboard
        """
        try:
            st.markdown("## 📊 Platform Analytics Dashboard")
            st.markdown("Comprehensive platform usage and engagement analytics")
            
            # Time period selector
            col1, col2 = st.columns([3, 1])
            with col1:
                time_period = st.selectbox(
                    "Select Time Period",
                    options=["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"],
                    index=1
                )
            
            with col2:
                if st.button("🔄 Refresh Data"):
                    st.rerun()
            
            # Convert time period to days
            days_map = {
                "Last 7 Days": 7,
                "Last 30 Days": 30,
                "Last 90 Days": 90,
                "All Time": 36500  # ~100 years
            }
            days = days_map[time_period]
            
            # Display dashboard sections
            st.markdown("---")
            self._show_overview_metrics(days)
            
            st.markdown("---")
            self._show_user_engagement_section(days)
            
            st.markdown("---")
            self._show_content_performance_section(days)
            
            st.markdown("---")
            self._show_platform_growth_section(days)
            
            st.markdown("---")
            self._show_activity_breakdown_section(days)
            
        except Exception as e:
            self.logger.error(f"Error displaying analytics dashboard: {e}")
            st.error("Unable to load analytics dashboard. Please try again.")
    
    def _show_overview_metrics(self, days: int) -> None:
        """Display overview metrics section."""
        try:
            st.markdown("### 📈 Platform Overview")
            
            # Get summary statistics
            activity_summary = self.activity_logger.get_activity_summary(days)
            
            # Get additional metrics
            total_users = self._get_total_users()
            published_articles = self._get_published_articles_count()
            total_comments = self._get_total_comments_count()
            total_feedback = self._get_total_feedback_count()
            
            # Display metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Active Users",
                    activity_summary['active_users'],
                    f"{activity_summary['active_users'] / max(total_users, 1) * 100:.1f}% of total"
                )
            
            with col2:
                st.metric(
                    "Total Activities",
                    activity_summary['total_activities'],
                    f"{activity_summary['activities_per_user']:.1f} per user"
                )
            
            with col3:
                st.metric(
                    "Published Articles",
                    published_articles
                )
            
            with col4:
                st.metric(
                    "User Engagement",
                    f"{total_comments + total_feedback}",
                    f"{total_comments} comments, {total_feedback} feedback"
                )
            
        except Exception as e:
            self.logger.error(f"Error showing overview metrics: {e}")
            st.error("Unable to load overview metrics.")
    
    def _show_user_engagement_section(self, days: int) -> None:
        """Display user engagement statistics section."""
        try:
            st.markdown("### 👥 User Engagement Statistics")
            
            # Get activity summary
            activity_summary = self.activity_logger.get_activity_summary(days)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Top active users
                st.markdown("#### Most Active Users")
                if activity_summary['top_users']:
                    top_users_df = pd.DataFrame(activity_summary['top_users'])
                    st.dataframe(
                        top_users_df,
                        column_config={
                            "username": "Username",
                            "activity_count": st.column_config.NumberColumn(
                                "Activities",
                                format="%d"
                            )
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                else:
                    st.info("No user activity data available.")
            
            with col2:
                # Activity by type
                st.markdown("#### Activity Distribution")
                if activity_summary['activity_by_type']:
                    activity_df = pd.DataFrame(activity_summary['activity_by_type'])
                    
                    # Create pie chart
                    fig = px.pie(
                        activity_df,
                        values='count',
                        names='action',
                        title='Activity Types'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No activity data available.")
            
            # Daily activity trend
            st.markdown("#### Daily Activity Trend")
            daily_trend = self.activity_logger.get_daily_activity_trend(days)
            
            if not daily_trend.empty:
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=daily_trend['date'],
                    y=daily_trend['activity_count'],
                    mode='lines+markers',
                    name='Total Activities',
                    line=dict(color='#1f77b4', width=2)
                ))
                
                fig.add_trace(go.Scatter(
                    x=daily_trend['date'],
                    y=daily_trend['unique_users'],
                    mode='lines+markers',
                    name='Unique Users',
                    line=dict(color='#ff7f0e', width=2)
                ))
                
                fig.update_layout(
                    title='Daily Activity and User Engagement',
                    xaxis_title='Date',
                    yaxis_title='Count',
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No daily trend data available.")
            
        except Exception as e:
            self.logger.error(f"Error showing user engagement section: {e}")
            st.error("Unable to load user engagement statistics.")
    
    def _show_content_performance_section(self, days: int) -> None:
        """Display content performance metrics section."""
        try:
            st.markdown("### 📝 Content Performance Metrics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Top articles by views
                st.markdown("#### Top Articles by Views")
                top_articles = self._get_top_articles_by_views(limit=10)
                
                if not top_articles.empty:
                    st.dataframe(
                        top_articles[['title', 'author', 'views', 'avg_rating']],
                        column_config={
                            "title": "Article Title",
                            "author": "Author",
                            "views": st.column_config.NumberColumn("Views", format="%d"),
                            "avg_rating": st.column_config.NumberColumn("Rating", format="%.1f")
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                else:
                    st.info("No article data available.")
            
            with col2:
                # Top content by feedback
                st.markdown("#### Top Content by Feedback")
                top_feedback = self._get_top_content_by_feedback(limit=10)
                
                if not top_feedback.empty:
                    st.dataframe(
                        top_feedback,
                        column_config={
                            "target_type": "Content Type",
                            "target_id": "Content ID",
                            "total_ratings": st.column_config.NumberColumn("Ratings", format="%d"),
                            "avg_stars": st.column_config.NumberColumn("Avg Stars", format="%.1f")
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                else:
                    st.info("No feedback data available.")
            
            # Feedback trends
            st.markdown("#### Feedback Trends")
            feedback_trend = self._get_feedback_trend(days)
            
            if not feedback_trend.empty:
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    x=feedback_trend['date'],
                    y=feedback_trend['feedback_count'],
                    name='Feedback Count',
                    marker_color='#2ca02c'
                ))
                
                fig.update_layout(
                    title='Daily Feedback Submissions',
                    xaxis_title='Date',
                    yaxis_title='Feedback Count',
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No feedback trend data available.")
            
            # Comments trends
            st.markdown("#### Comment Activity")
            comment_trend = self._get_comment_trend(days)
            
            if not comment_trend.empty:
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    x=comment_trend['date'],
                    y=comment_trend['comment_count'],
                    name='Comment Count',
                    marker_color='#9467bd'
                ))
                
                fig.update_layout(
                    title='Daily Comment Activity',
                    xaxis_title='Date',
                    yaxis_title='Comment Count',
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No comment trend data available.")
            
        except Exception as e:
            self.logger.error(f"Error showing content performance section: {e}")
            st.error("Unable to load content performance metrics.")
    
    def _show_platform_growth_section(self, days: int) -> None:
        """Display platform growth and usage reports section."""
        try:
            st.markdown("### 📊 Platform Growth & Usage Reports")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # User growth
                st.markdown("#### User Growth")
                user_growth = self._get_user_growth_trend(days)
                
                if not user_growth.empty:
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=user_growth['date'],
                        y=user_growth['cumulative_users'],
                        mode='lines+markers',
                        name='Cumulative Users',
                        fill='tozeroy',
                        line=dict(color='#17becf', width=2)
                    ))
                    
                    fig.update_layout(
                        title='Cumulative User Growth',
                        xaxis_title='Date',
                        yaxis_title='Total Users',
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No user growth data available.")
            
            with col2:
                # Content growth
                st.markdown("#### Content Growth")
                content_growth = self._get_content_growth_trend(days)
                
                if not content_growth.empty:
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=content_growth['date'],
                        y=content_growth['cumulative_articles'],
                        mode='lines+markers',
                        name='Articles',
                        line=dict(color='#d62728', width=2)
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=content_growth['date'],
                        y=content_growth['cumulative_comments'],
                        mode='lines+markers',
                        name='Comments',
                        line=dict(color='#9467bd', width=2)
                    ))
                    
                    fig.update_layout(
                        title='Cumulative Content Growth',
                        xaxis_title='Date',
                        yaxis_title='Total Count',
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No content growth data available.")
            
            # Engagement rate over time
            st.markdown("#### Engagement Rate Trend")
            engagement_rate = self._get_engagement_rate_trend(days)
            
            if not engagement_rate.empty:
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=engagement_rate['date'],
                    y=engagement_rate['engagement_rate'],
                    mode='lines+markers',
                    name='Engagement Rate',
                    line=dict(color='#e377c2', width=2)
                ))
                
                fig.update_layout(
                    title='Daily Engagement Rate (Activities per Active User)',
                    xaxis_title='Date',
                    yaxis_title='Engagement Rate',
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No engagement rate data available.")
            
        except Exception as e:
            self.logger.error(f"Error showing platform growth section: {e}")
            st.error("Unable to load platform growth reports.")
    
    def _show_activity_breakdown_section(self, days: int) -> None:
        """Display detailed activity breakdown section."""
        try:
            st.markdown("### 🔍 Detailed Activity Breakdown")
            
            # Get activity summary
            activity_summary = self.activity_logger.get_activity_summary(days)
            
            if activity_summary['activity_by_type']:
                activity_df = pd.DataFrame(activity_summary['activity_by_type'])
                
                # Sort by count
                activity_df = activity_df.sort_values('count', ascending=False)
                
                # Create horizontal bar chart
                fig = px.bar(
                    activity_df,
                    x='count',
                    y='action',
                    orientation='h',
                    title='Activity Types Breakdown',
                    labels={'count': 'Number of Activities', 'action': 'Activity Type'}
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Show detailed table
                st.markdown("#### Activity Details")
                st.dataframe(
                    activity_df,
                    column_config={
                        "action": "Activity Type",
                        "count": st.column_config.NumberColumn("Count", format="%d")
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No activity breakdown data available.")
            
        except Exception as e:
            self.logger.error(f"Error showing activity breakdown section: {e}")
            st.error("Unable to load activity breakdown.")
    
    # Helper methods for data retrieval
    
    def _get_total_users(self) -> int:
        """Get total number of registered users."""
        try:
            import yaml
            with open("config.yaml", 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return len(config.get('credentials', {}).get('usernames', {}))
        except Exception as e:
            self.logger.error(f"Error getting total users: {e}")
            return 0
    
    def _get_published_articles_count(self) -> int:
        """Get count of published articles."""
        try:
            query = "SELECT COUNT(*) as count FROM articles WHERE status = 'published'"
            result = self.db_manager.execute_query(query, ())
            return int(result.iloc[0]['count']) if not result.empty else 0
        except Exception as e:
            self.logger.error(f"Error getting published articles count: {e}")
            return 0
    
    def _get_total_comments_count(self) -> int:
        """Get total count of comments."""
        try:
            query = "SELECT COUNT(*) as count FROM comments WHERE is_approved = 1"
            result = self.db_manager.execute_query(query, ())
            return int(result.iloc[0]['count']) if not result.empty else 0
        except Exception as e:
            self.logger.error(f"Error getting total comments count: {e}")
            return 0
    
    def _get_total_feedback_count(self) -> int:
        """Get total count of feedback submissions."""
        try:
            query = "SELECT COUNT(*) as count FROM user_feedback"
            result = self.db_manager.execute_query(query, ())
            return int(result.iloc[0]['count']) if not result.empty else 0
        except Exception as e:
            self.logger.error(f"Error getting total feedback count: {e}")
            return 0
    
    def _get_top_articles_by_views(self, limit: int = 10) -> pd.DataFrame:
        """Get top articles by view count."""
        try:
            query = """
                SELECT title, author, views, avg_rating, total_feedback
                FROM articles
                WHERE status = 'published'
                ORDER BY views DESC
                LIMIT ?
            """
            return self.db_manager.execute_query(query, (limit,))
        except Exception as e:
            self.logger.error(f"Error getting top articles by views: {e}")
            return pd.DataFrame()
    
    def _get_top_content_by_feedback(self, limit: int = 10) -> pd.DataFrame:
        """Get top content by feedback count."""
        try:
            query = """
                SELECT target_type, target_id, total_ratings, avg_stars, thumbs_up, thumbs_down
                FROM content_stats
                ORDER BY total_ratings DESC
                LIMIT ?
            """
            return self.db_manager.execute_query(query, (limit,))
        except Exception as e:
            self.logger.error(f"Error getting top content by feedback: {e}")
            return pd.DataFrame()
    
    def _get_feedback_trend(self, days: int) -> pd.DataFrame:
        """Get daily feedback submission trend."""
        try:
            query = """
                SELECT 
                    DATE(timestamp) as date,
                    COUNT(*) as feedback_count
                FROM user_feedback
                WHERE timestamp >= datetime('now', '-' || ? || ' days')
                GROUP BY DATE(timestamp)
                ORDER BY date ASC
            """
            return self.db_manager.execute_query(query, (days,))
        except Exception as e:
            self.logger.error(f"Error getting feedback trend: {e}")
            return pd.DataFrame()
    
    def _get_comment_trend(self, days: int) -> pd.DataFrame:
        """Get daily comment submission trend."""
        try:
            query = """
                SELECT 
                    DATE(timestamp) as date,
                    COUNT(*) as comment_count
                FROM comments
                WHERE timestamp >= datetime('now', '-' || ? || ' days')
                GROUP BY DATE(timestamp)
                ORDER BY date ASC
            """
            return self.db_manager.execute_query(query, (days,))
        except Exception as e:
            self.logger.error(f"Error getting comment trend: {e}")
            return pd.DataFrame()
    
    def _get_user_growth_trend(self, days: int) -> pd.DataFrame:
        """Get user growth trend over time."""
        try:
            # Since we don't have user registration dates in the database,
            # we'll use first activity as a proxy for user join date
            query = """
                SELECT 
                    DATE(first_activity) as date,
                    COUNT(*) as new_users,
                    SUM(COUNT(*)) OVER (ORDER BY DATE(first_activity)) as cumulative_users
                FROM (
                    SELECT 
                        username,
                        MIN(timestamp) as first_activity
                    FROM user_activity
                    WHERE timestamp >= datetime('now', '-' || ? || ' days')
                    GROUP BY username
                )
                GROUP BY DATE(first_activity)
                ORDER BY date ASC
            """
            return self.db_manager.execute_query(query, (days,))
        except Exception as e:
            self.logger.error(f"Error getting user growth trend: {e}")
            return pd.DataFrame()
    
    def _get_content_growth_trend(self, days: int) -> pd.DataFrame:
        """Get content growth trend over time."""
        try:
            # Get article growth
            query_articles = """
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as new_articles,
                    SUM(COUNT(*)) OVER (ORDER BY DATE(created_at)) as cumulative_articles
                FROM articles
                WHERE created_at >= datetime('now', '-' || ? || ' days')
                GROUP BY DATE(created_at)
                ORDER BY date ASC
            """
            articles_df = self.db_manager.execute_query(query_articles, (days,))
            
            # Get comment growth
            query_comments = """
                SELECT 
                    DATE(timestamp) as date,
                    COUNT(*) as new_comments,
                    SUM(COUNT(*)) OVER (ORDER BY DATE(timestamp)) as cumulative_comments
                FROM comments
                WHERE timestamp >= datetime('now', '-' || ? || ' days')
                GROUP BY DATE(timestamp)
                ORDER BY date ASC
            """
            comments_df = self.db_manager.execute_query(query_comments, (days,))
            
            # Merge the dataframes
            if not articles_df.empty and not comments_df.empty:
                merged = pd.merge(
                    articles_df[['date', 'cumulative_articles']],
                    comments_df[['date', 'cumulative_comments']],
                    on='date',
                    how='outer'
                ).ffill().fillna(0)
                return merged
            elif not articles_df.empty:
                articles_df['cumulative_comments'] = 0
                return articles_df[['date', 'cumulative_articles', 'cumulative_comments']]
            elif not comments_df.empty:
                comments_df['cumulative_articles'] = 0
                return comments_df[['date', 'cumulative_articles', 'cumulative_comments']]
            else:
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Error getting content growth trend: {e}")
            return pd.DataFrame()
    
    def _get_engagement_rate_trend(self, days: int) -> pd.DataFrame:
        """Get daily engagement rate trend."""
        try:
            query = """
                SELECT 
                    DATE(timestamp) as date,
                    COUNT(*) as total_activities,
                    COUNT(DISTINCT username) as unique_users,
                    CAST(COUNT(*) AS FLOAT) / COUNT(DISTINCT username) as engagement_rate
                FROM user_activity
                WHERE timestamp >= datetime('now', '-' || ? || ' days')
                GROUP BY DATE(timestamp)
                ORDER BY date ASC
            """
            return self.db_manager.execute_query(query, (days,))
        except Exception as e:
            self.logger.error(f"Error getting engagement rate trend: {e}")
            return pd.DataFrame()
    
    def generate_report(self, days: int = 30) -> Dict[str, Any]:
        """
        Generate comprehensive analytics report.
        
        Args:
            days: Number of days to include in report
            
        Returns:
            Dict[str, Any]: Complete analytics report data
        """
        try:
            activity_summary = self.activity_logger.get_activity_summary(days)
            
            report = {
                'generated_at': datetime.now().isoformat(),
                'period_days': days,
                'overview': {
                    'total_users': self._get_total_users(),
                    'active_users': activity_summary['active_users'],
                    'total_activities': activity_summary['total_activities'],
                    'published_articles': self._get_published_articles_count(),
                    'total_comments': self._get_total_comments_count(),
                    'total_feedback': self._get_total_feedback_count()
                },
                'engagement': {
                    'activities_per_user': activity_summary['activities_per_user'],
                    'top_users': activity_summary['top_users'],
                    'activity_by_type': activity_summary['activity_by_type']
                },
                'content_performance': {
                    'top_articles': self._get_top_articles_by_views(10).to_dict('records'),
                    'top_feedback_content': self._get_top_content_by_feedback(10).to_dict('records')
                }
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            return {}


# Global analytics dashboard instance
_analytics_dashboard = None

def get_analytics_dashboard(db_manager: DatabaseManager, 
                           activity_logger: ActivityLogger) -> AnalyticsDashboard:
    """
    Get singleton analytics dashboard instance.
    
    Args:
        db_manager: Database manager instance
        activity_logger: Activity logger instance
        
    Returns:
        AnalyticsDashboard: Singleton analytics dashboard instance
    """
    global _analytics_dashboard
    if _analytics_dashboard is None:
        _analytics_dashboard = AnalyticsDashboard(db_manager, activity_logger)
    return _analytics_dashboard
