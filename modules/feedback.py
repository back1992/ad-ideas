"""
Feedback System for 广告思想简史 Platform

This module provides comprehensive feedback collection and management
using both streamlit-feedback component and Streamlit's built-in st.feedback.
"""

import streamlit as st
from streamlit_feedback import streamlit_feedback
import logging
from utils.i18n import t
from utils.logger import create_logger
import pandas as pd
from typing import Optional, Dict, Any, List
from datetime import datetime
from modules.database import DatabaseManager


class FeedbackSystem:
    """
    Comprehensive feedback system with multiple feedback types and statistics.
    
    Handles feedback collection, storage, retrieval, and real-time statistics
    using both streamlit-feedback component and Streamlit's built-in feedback widgets.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize FeedbackSystem with database manager.
        
        Args:
            db_manager: Database manager instance for data persistence
        """
        self.db_manager = db_manager
        self.logger = create_logger('FeedbackSystem')
        
    
    def collect_feedback(self, target_type: str, target_id: str, 
                        feedback_type: str = "thumbs",
                        optional_text_label: str = "Please provide additional feedback (optional)") -> Optional[Dict[str, Any]]:
        """
        Collect user feedback for specific content.
        
        Args:
            target_type: Type of content ('timeline', 'figures', 'campaigns', 'article')
            target_id: Unique identifier for the content
            feedback_type: Type of feedback widget ('thumbs', 'stars', 'faces')
            optional_text_label: Label for optional text feedback
            
        Returns:
            Optional[Dict[str, Any]]: Feedback data if submitted, None otherwise
        """
        try:
            # Check if user is authenticated
            username = st.session_state.get('username')
            if not username:
                st.warning(t('login_to_feedback'))
                return None

            # Check if user has already provided feedback
            if self.has_user_feedback(username, target_type, target_id):
                st.success("You have already provided feedback for this content.")
                self.show_feedback_stats(target_type, target_id)
                return None

            # Display feedback collection interface
            st.markdown(f"### 💭 {t('feedback_prompt')}")
            
            # Create unique key for feedback widget
            feedback_key = f"feedback_{target_type}_{target_id}_{username}"
            
            feedback = None
            
            if feedback_type == "stars":
                # Use Streamlit's built-in st.feedback for stars
                st.markdown("**Rate this content:**")
                star_rating = st.feedback("stars", key=f"{feedback_key}_stars")
                
                # Add optional text input
                feedback_text = st.text_area(
                    optional_text_label,
                    key=f"{feedback_key}_text",
                    max_chars=500
                )
                
                # Submit button for stars feedback
                if st.button("Submit Rating", key=f"{feedback_key}_submit"):
                    if star_rating is not None:
                        feedback = {
                            "score": star_rating,
                            "text": feedback_text
                        }
                    else:
                        st.warning("Please select a star rating before submitting.")
            
            elif feedback_type in ["thumbs", "faces"]:
                # Use streamlit-feedback component for thumbs and faces
                feedback = streamlit_feedback(
                    feedback_type=feedback_type,
                    optional_text_label=optional_text_label,
                    key=feedback_key
                )
            
            else:
                st.error(f"Unsupported feedback type: {feedback_type}")
                return None
            
            if feedback:
                # Save feedback to database
                success = self.save_feedback(
                    username=username,
                    target_type=target_type,
                    target_id=target_id,
                    feedback_type=feedback_type,
                    feedback_value=feedback.get("score"),
                    feedback_text=feedback.get("text", "")
                )
                
                if success:
                    st.success("🎉 Thank you for your feedback!")
                    self.logger.info(f"Feedback saved for user {username} on {target_type}:{target_id}")
                    
                    # Update content statistics
                    self.update_content_stats(target_type, target_id)
                    
                    # Show updated statistics
                    self.show_feedback_stats(target_type, target_id)
                    
                    return feedback
                else:
                    st.error("Failed to save feedback. Please try again.")
                    
            return None
            
        except Exception as e:
            self.logger.error(f"Error collecting feedback: {e}")
            st.error("An error occurred while collecting feedback.")
            return None
    
    def _normalize_feedback_value(self, feedback_value: Any, feedback_type: str) -> int:
        """
        Normalize feedback values to consistent integers for database storage.
        
        Args:
            feedback_value: Raw feedback value from widget
            feedback_type: Type of feedback ('thumbs', 'stars', 'faces')
            
        Returns:
            int: Normalized integer value
        """
        try:
            # If already an integer, return as-is
            if isinstance(feedback_value, int):
                return feedback_value
            
            # Handle string values
            if isinstance(feedback_value, str):
                # Thumbs feedback
                if feedback_type == "thumbs":
                    if feedback_value in ['👍', 'thumbs_up', '1', 1]:
                        return 1
                    elif feedback_value in ['👎', 'thumbs_down', '0', 0]:
                        return 0
                
                # Faces feedback - map emojis to integers
                elif feedback_type == "faces":
                    emoji_map = {
                        '😞': 0, '😐': 1, '🙂': 2, '😊': 3, '😍': 4,
                        'sad': 0, 'neutral': 1, 'slight_smile': 2, 'smile': 3, 'heart_eyes': 4
                    }
                    return emoji_map.get(feedback_value, 2)  # Default to neutral
                
                # Try to convert string to int
                try:
                    return int(feedback_value)
                except ValueError:
                    pass
            
            # Default fallback
            return 2  # Neutral/middle value
            
        except Exception as e:
            self.logger.warning(f"Error normalizing feedback value {feedback_value}: {e}")
    def _format_feedback_value_for_display(self, feedback_value: Any, feedback_type: str) -> str:
        """
        Format feedback value for display.
        
        Args:
            feedback_value: Stored feedback value
            feedback_type: Type of feedback
            
        Returns:
            str: Formatted display value
        """
        try:
            # Convert to int if possible
            if isinstance(feedback_value, str):
                try:
                    value = int(feedback_value)
                except ValueError:
                    return str(feedback_value)
            else:
                value = int(feedback_value) if feedback_value is not None else 0
            
            # Format based on feedback type
            if feedback_type == "thumbs":
                return "👍 Positive" if value == 1 else "👎 Negative"
            elif feedback_type == "stars":
                return f"⭐ {value + 1}/5 stars"  # Convert 0-4 to 1-5
            elif feedback_type == "faces":
                face_map = {0: "😞 Sad", 1: "😐 Neutral", 2: "🙂 Slight Smile", 3: "😊 Happy", 4: "😍 Love"}
                return face_map.get(value, f"😐 Rating: {value}")
            else:
                return str(value)
                
        except Exception:
            return str(feedback_value)
    
    def save_feedback(self, username: str, target_type: str, target_id: str,
                     feedback_type: str, feedback_value: Any, feedback_text: str) -> bool:
        """
        Save feedback to database.
        
        Args:
            username: Username providing feedback
            target_type: Type of content
            target_id: Content identifier
            feedback_type: Type of feedback
            feedback_value: Feedback value (any type, will be normalized)
            feedback_text: Optional text feedback
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            # Normalize feedback value to consistent integer
            normalized_value = self._normalize_feedback_value(feedback_value, feedback_type)
            
            query = """
                INSERT INTO user_feedback 
                (username, target_type, target_id, feedback_type, feedback_value, feedback_text)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            affected_rows = self.db_manager.execute_update(
                query, 
                (username, target_type, target_id, feedback_type, normalized_value, feedback_text)
            )
            
            return affected_rows > 0
            
        except Exception as e:
            self.logger.error(f"Error saving feedback: {e}")
            return False
    
    def has_user_feedback(self, username: str, target_type: str, target_id: str) -> bool:
        """
        Check if user has already provided feedback for specific content.
        
        Args:
            username: Username to check
            target_type: Type of content
            target_id: Content identifier
            
        Returns:
            bool: True if user has provided feedback, False otherwise
        """
        try:
            query = """
                SELECT COUNT(*) as count 
                FROM user_feedback 
                WHERE username = ? AND target_type = ? AND target_id = ?
            """
            
            result = self.db_manager.execute_query(query, (username, target_type, target_id))
            return bool(result.iloc[0]['count'] > 0) if not result.empty else False
            
        except Exception as e:
            self.logger.error(f"Error checking user feedback: {e}")
            return False
    
    def get_feedback_stats(self, target_type: str, target_id: str) -> Dict[str, Any]:
        """
        Get aggregated feedback statistics for content.
        
        Args:
            target_type: Type of content
            target_id: Content identifier
            
        Returns:
            Dict[str, Any]: Statistics dictionary
        """
        try:
            query = """
                SELECT 
                    feedback_type,
                    COUNT(*) as total_count,
                    AVG(feedback_value) as avg_rating,
                    SUM(CASE WHEN feedback_value >= 1 THEN 1 ELSE 0 END) as positive_count,
                    SUM(CASE WHEN feedback_value = 0 THEN 1 ELSE 0 END) as negative_count
                FROM user_feedback 
                WHERE target_type = ? AND target_id = ?
                GROUP BY feedback_type
            """
            
            result = self.db_manager.execute_query(query, (target_type, target_id))
            
            stats = {
                'total_feedback': 0,
                'avg_rating': 0.0,
                'positive_count': 0,
                'negative_count': 0,
                'by_type': {}
            }
            
            if not result.empty:
                for _, row in result.iterrows():
                    feedback_type = row['feedback_type']
                    stats['by_type'][feedback_type] = {
                        'total_count': row['total_count'],
                        'avg_rating': row['avg_rating'],
                        'positive_count': row['positive_count'],
                        'negative_count': row['negative_count']
                    }
                    
                    # Aggregate totals
                    stats['total_feedback'] += row['total_count']
                    stats['positive_count'] += row['positive_count']
                    stats['negative_count'] += row['negative_count']
                
                # Calculate overall average
                if stats['total_feedback'] > 0:
                    total_score = sum(
                        type_stats['avg_rating'] * type_stats['total_count']
                        for type_stats in stats['by_type'].values()
                    )
                    stats['avg_rating'] = total_score / stats['total_feedback']
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting feedback stats: {e}")
            return {'total_feedback': 0, 'avg_rating': 0.0, 'positive_count': 0, 'negative_count': 0, 'by_type': {}}
    
    def show_feedback_stats(self, target_type: str, target_id: str) -> None:
        """
        Display feedback statistics for content.
        
        Args:
            target_type: Type of content
            target_id: Content identifier
        """
        try:
            stats = self.get_feedback_stats(target_type, target_id)
            
            if stats['total_feedback'] == 0:
                st.info("No feedback yet. Be the first to share your thoughts!")
                return
            
            # Display overall statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Feedback", stats['total_feedback'])
            
            with col2:
                if stats['avg_rating'] > 0:
                    st.metric("Average Rating", f"{stats['avg_rating']:.1f}")
                else:
                    st.metric("Average Rating", "N/A")
            
            with col3:
                if stats['positive_count'] + stats['negative_count'] > 0:
                    positive_ratio = stats['positive_count'] / (stats['positive_count'] + stats['negative_count']) * 100
                    st.metric("Positive Feedback", f"{positive_ratio:.0f}%")
                else:
                    st.metric("Positive Feedback", "N/A")
            
            # Display detailed statistics by feedback type
            if len(stats['by_type']) > 1:
                st.markdown("#### Feedback Breakdown")
                
                for feedback_type, type_stats in stats['by_type'].items():
                    with st.expander(f"{feedback_type.title()} Feedback ({type_stats['total_count']} responses)"):
                        if feedback_type == "thumbs":
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"👍 Thumbs Up: {type_stats['positive_count']}")
                            with col2:
                                st.write(f"👎 Thumbs Down: {type_stats['negative_count']}")
                        
                        elif feedback_type == "stars":
                            st.write(f"⭐ Average Stars: {type_stats['avg_rating']:.1f}/5")
                        
                        elif feedback_type == "faces":
                            st.write(f"😊 Average Rating: {type_stats['avg_rating']:.1f}/5")
            
        except Exception as e:
            self.logger.error(f"Error displaying feedback stats: {e}")
            st.error("Unable to display feedback statistics.")
    
    def update_content_stats(self, target_type: str, target_id: str) -> None:
        """
        Update aggregated content statistics in content_stats table.
        
        Args:
            target_type: Type of content
            target_id: Content identifier
        """
        try:
            # Get current feedback statistics
            stats = self.get_feedback_stats(target_type, target_id)
            
            # Calculate thumbs up/down specifically
            thumbs_stats = stats['by_type'].get('thumbs', {})
            thumbs_up = thumbs_stats.get('positive_count', 0)
            thumbs_down = thumbs_stats.get('negative_count', 0)
            
            # Calculate average stars rating
            stars_stats = stats['by_type'].get('stars', {})
            avg_stars = stars_stats.get('avg_rating', 0.0)
            
            # Update or insert content statistics
            query = """
                INSERT OR REPLACE INTO content_stats 
                (target_type, target_id, thumbs_up, thumbs_down, avg_stars, total_ratings, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """
            
            self.db_manager.execute_update(
                query,
                (target_type, target_id, thumbs_up, thumbs_down, avg_stars, stats['total_feedback'])
            )
            
            self.logger.info(f"Content stats updated for {target_type}:{target_id}")
            
        except Exception as e:
            self.logger.error(f"Error updating content stats: {e}")
    
    def get_content_stats(self, target_type: str, target_id: str) -> Optional[Dict[str, Any]]:
        """
        Get content statistics from content_stats table.
        
        Args:
            target_type: Type of content
            target_id: Content identifier
            
        Returns:
            Optional[Dict[str, Any]]: Content statistics or None if not found
        """
        try:
            query = """
                SELECT * FROM content_stats 
                WHERE target_type = ? AND target_id = ?
            """
            
            result = self.db_manager.execute_query(query, (target_type, target_id))
            
            if not result.empty:
                row = result.iloc[0]
                return {
                    'thumbs_up': row['thumbs_up'],
                    'thumbs_down': row['thumbs_down'],
                    'avg_stars': row['avg_stars'],
                    'total_ratings': row['total_ratings'],
                    'last_updated': row['last_updated']
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting content stats: {e}")
            return None
    
    def get_user_feedback_history(self, username: str, limit: int = 50) -> pd.DataFrame:
        """
        Get user's feedback history.
        
        Args:
            username: Username to get history for
            limit: Maximum number of records to return
            
        Returns:
            pd.DataFrame: User feedback history
        """
        try:
            query = """
                SELECT target_type, target_id, feedback_type, feedback_value, 
                       feedback_text, timestamp
                FROM user_feedback 
                WHERE username = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """
            
            return self.db_manager.execute_query(query, (username, limit))
            
        except Exception as e:
            self.logger.error(f"Error getting user feedback history: {e}")
            return pd.DataFrame()
    
    def get_popular_content(self, target_type: Optional[str] = None, limit: int = 10) -> pd.DataFrame:
        """
        Get most popular content based on feedback.
        
        Args:
            target_type: Filter by content type (optional)
            limit: Maximum number of results
            
        Returns:
            pd.DataFrame: Popular content list
        """
        try:
            base_query = """
                SELECT target_type, target_id, thumbs_up, thumbs_down, 
                       avg_stars, total_ratings,
                       (thumbs_up + avg_stars * total_ratings) as popularity_score
                FROM content_stats
            """
            
            if target_type:
                query = base_query + " WHERE target_type = ? ORDER BY popularity_score DESC LIMIT ?"
                params = (target_type, limit)
            else:
                query = base_query + " ORDER BY popularity_score DESC LIMIT ?"
                params = (limit,)
            
            return self.db_manager.execute_query(query, params)
            
        except Exception as e:
            self.logger.error(f"Error getting popular content: {e}")
            return pd.DataFrame()


# Global feedback system instance
_feedback_system = None

def get_feedback_system(db_manager: DatabaseManager) -> FeedbackSystem:
    """
    Get singleton feedback system instance.
    
    Args:
        db_manager: Database manager instance
        
    Returns:
        FeedbackSystem: Singleton feedback system instance
    """
    global _feedback_system
    if _feedback_system is None:
        _feedback_system = FeedbackSystem(db_manager)
    return _feedback_system


class FeedbackDisplayComponents:
    """
    Additional display components for feedback visualization.
    
    Provides specialized display methods for different feedback types
    and enhanced statistics visualization.
    """
    
    def __init__(self, feedback_system: FeedbackSystem):
        """
        Initialize display components with feedback system.
        
        Args:
            feedback_system: FeedbackSystem instance
        """
        self.feedback_system = feedback_system
        self.logger = feedback_system.logger
    
    def display_thumbs_feedback(self, target_type: str, target_id: str, 
                               show_collection: bool = True) -> None:
        """
        Display thumbs up/down feedback interface and statistics.
        
        Args:
            target_type: Type of content
            target_id: Content identifier
            show_collection: Whether to show feedback collection interface
        """
        try:
            if show_collection:
                # Show feedback collection
                feedback = self.feedback_system.collect_feedback(
                    target_type, target_id, "thumbs", 
                    "Tell us more about your experience (optional)"
                )
            else:
                # Show only statistics
                self.feedback_system.show_feedback_stats(target_type, target_id)
                
        except Exception as e:
            self.logger.error(f"Error displaying thumbs feedback: {e}")
            st.error("Unable to display feedback interface.")
    
    def display_stars_feedback(self, target_type: str, target_id: str,
                              show_collection: bool = True) -> None:
        """
        Display star rating feedback interface and statistics.
        
        Args:
            target_type: Type of content
            target_id: Content identifier
            show_collection: Whether to show feedback collection interface
        """
        try:
            if show_collection:
                # Show feedback collection using Streamlit's built-in st.feedback
                feedback = self.feedback_system.collect_feedback(
                    target_type, target_id, "stars",
                    "Please share your detailed thoughts (optional)"
                )
            else:
                # Show only statistics
                self.feedback_system.show_feedback_stats(target_type, target_id)
                
        except Exception as e:
            self.logger.error(f"Error displaying stars feedback: {e}")
            st.error("Unable to display feedback interface.")
    
    def display_faces_feedback(self, target_type: str, target_id: str,
                              show_collection: bool = True) -> None:
        """
        Display emoji faces feedback interface and statistics.
        
        Args:
            target_type: Type of content
            target_id: Content identifier
            show_collection: Whether to show feedback collection interface
        """
        try:
            if show_collection:
                # Show feedback collection
                feedback = self.feedback_system.collect_feedback(
                    target_type, target_id, "faces",
                    "How did this content make you feel? (optional details)"
                )
            else:
                # Show only statistics
                self.feedback_system.show_feedback_stats(target_type, target_id)
                
        except Exception as e:
            self.logger.error(f"Error displaying faces feedback: {e}")
            st.error("Unable to display feedback interface.")
    
    def display_compact_stats(self, target_type: str, target_id: str) -> None:
        """
        Display compact feedback statistics suitable for content lists.
        
        Args:
            target_type: Type of content
            target_id: Content identifier
        """
        try:
            stats = self.feedback_system.get_feedback_stats(target_type, target_id)
            
            if stats['total_feedback'] == 0:
                st.caption("No feedback yet")
                return
            
            # Create compact display without nested columns
            feedback_text = f"📊 {stats['total_feedback']}"
            
            if stats['avg_rating'] > 0:
                rating_text = f"⭐ {stats['avg_rating']:.1f}"
            else:
                rating_text = "⭐ N/A"
            
            if stats['positive_count'] + stats['negative_count'] > 0:
                positive_ratio = stats['positive_count'] / (stats['positive_count'] + stats['negative_count']) * 100
                positive_text = f"👍 {positive_ratio:.0f}%"
            else:
                positive_text = "👍 No ratings"
            
            # Display as single line with separators
            st.caption(f"{feedback_text} | {rating_text} | {positive_text}")
                    
        except Exception as e:
            self.logger.error(f"Error displaying compact stats: {e}")
            st.caption("Stats unavailable")
    
    def display_trending_content(self, target_type: Optional[str] = None, limit: int = 5) -> None:
        """
        Display trending/popular content based on feedback.
        
        Args:
            target_type: Filter by content type (optional)
            limit: Number of items to display
        """
        try:
            popular_content = self.feedback_system.get_popular_content(target_type, limit)
            
            if popular_content.empty:
                st.info("No trending content available yet.")
                return
            
            st.markdown("### 🔥 Trending Content")
            
            for idx, row in popular_content.iterrows():
                with st.container():
                    # Display content info and stats in a single line format
                    content_title = f"**{row['target_type'].title()}**: {row['target_id']}"
                    
                    if row['avg_stars'] > 0:
                        stars_text = f"⭐ {row['avg_stars']:.1f}"
                    else:
                        stars_text = "⭐ N/A"
                    
                    total_votes = row['thumbs_up'] + row['thumbs_down']
                    if total_votes > 0:
                        positive_ratio = row['thumbs_up'] / total_votes * 100
                        thumbs_text = f"👍 {positive_ratio:.0f}%"
                    else:
                        thumbs_text = "👍 N/A"
                    
                    # Display as single line
                    st.write(f"{content_title} | {stars_text} | {thumbs_text}")
                    st.divider()
                    
        except Exception as e:
            self.logger.error(f"Error displaying trending content: {e}")
            st.error("Unable to display trending content.")
    
    def display_user_feedback_summary(self, username: str) -> None:
        """
        Display user's feedback activity summary.
        
        Args:
            username: Username to display summary for
        """
        try:
            history = self.feedback_system.get_user_feedback_history(username, 100)
            
            if history.empty:
                st.info("You haven't provided any feedback yet.")
                return
            
            # Convert DataFrame to consistent string types to avoid Arrow serialization issues
            history_clean = history.copy()
            for col in history_clean.columns:
                history_clean[col] = history_clean[col].astype(str)
            
            st.markdown("### 📈 Your Feedback Activity")
            
            # Summary statistics - use safe operations
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Feedback", len(history_clean))
            
            with col2:
                try:
                    # Convert feedback_value to numeric, handling any data type
                    numeric_values = pd.to_numeric(history['feedback_value'], errors='coerce')
                    avg_rating = numeric_values.mean()
                    if pd.notna(avg_rating):
                        st.metric("Average Rating", f"{avg_rating:.1f}")
                    else:
                        st.metric("Average Rating", "N/A")
                except Exception:
                    st.metric("Average Rating", "N/A")
            
            with col3:
                try:
                    # Convert timestamp strings to datetime for comparison
                    timestamps_dt = pd.to_datetime(history['timestamp'], errors='coerce')
                    week_ago = datetime.now() - pd.Timedelta(days=7)
                    recent_feedback = len(timestamps_dt[timestamps_dt >= week_ago])
                    st.metric("This Week", recent_feedback)
                except Exception:
                    st.metric("This Week", "N/A")
            
            # Feedback breakdown by type - safe version
            try:
                if len(history_clean) > 0:
                    # Use the cleaned DataFrame for counts
                    feedback_by_type = history_clean['feedback_type'].value_counts()
                    
                    st.markdown("#### Feedback by Type")
                    for feedback_type, count in feedback_by_type.items():
                        st.write(f"- **{feedback_type.title()}**: {count} responses")
            except Exception:
                st.write("Unable to display feedback breakdown")
            
            # Recent feedback - completely safe version
            try:
                if len(history_clean) > 0:
                    st.markdown("#### Recent Feedback")
                    recent_history = history_clean.head(5)
                    
                    for idx, row in recent_history.iterrows():
                        # All values are now strings, safe to use
                        safe_timestamp = row.get('timestamp', 'Unknown')[:10]
                        safe_target_type = row.get('target_type', 'Unknown').title()
                        safe_target_id = row.get('target_id', 'Unknown')
                        safe_feedback_type = row.get('feedback_type', 'Unknown').title()
                        safe_feedback_value = row.get('feedback_value', 'N/A')
                        safe_feedback_text = row.get('feedback_text', '')
                        
                        expander_title = f"{safe_target_type}: {safe_target_id} - {safe_timestamp}"
                        
                        with st.expander(expander_title):
                            st.write(f"**Type**: {safe_feedback_type}")
                            # Format the feedback value for better display
                            formatted_value = self.feedback_system._format_feedback_value_for_display(
                                safe_feedback_value, row.get('feedback_type', 'unknown')
                            )
                            st.write(f"**Rating**: {formatted_value}")
                            if safe_feedback_text and safe_feedback_text != 'nan':
                                st.write(f"**Comment**: {safe_feedback_text}")
            
            except Exception as recent_error:
                self.logger.error(f"Recent feedback display error: {recent_error}")
                st.write("Unable to display recent feedback")
                            
        except Exception as e:
            self.logger.error(f"Error displaying user feedback summary: {e}")
            st.error("Unable to display feedback summary. Please try refreshing the page.")


def get_feedback_display_components(feedback_system: FeedbackSystem) -> FeedbackDisplayComponents:
    """
    Get feedback display components instance.
    
    Args:
        feedback_system: FeedbackSystem instance
        
    Returns:
        FeedbackDisplayComponents: Display components instance
    """
    return FeedbackDisplayComponents(feedback_system)