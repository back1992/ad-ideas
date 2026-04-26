"""
Manual test script for search functionality.

This script tests the search system without running the full Streamlit app.
"""

from modules.database import get_database_manager
from modules.search import get_search_system
from modules.recommendations import get_recommendation_engine

def test_search_system():
    """Test search system functionality."""
    print("=" * 60)
    print("Testing Search System")
    print("=" * 60)
    
    # Initialize systems
    db_manager = get_database_manager()
    search_system = get_search_system(db_manager)
    
    # Test 1: Search for articles
    print("\n1. Testing article search...")
    results = search_system.search("advertising", content_types=['articles'], limit=5)
    
    if 'articles' in results and not results['articles'].empty:
        print(f"✅ Found {len(results['articles'])} article(s)")
        print("\nTop result:")
        top = results['articles'].iloc[0]
        print(f"   Title: {top['title']}")
        print(f"   Author: {top['author']}")
        print(f"   Relevance: {top['relevance_score']}")
    else:
        print("⚠️  No articles found (this is OK if database is empty)")
    
    # Test 2: Search for comments
    print("\n2. Testing comment search...")
    results = search_system.search("test", content_types=['comments'], limit=5)
    
    if 'comments' in results and not results['comments'].empty:
        print(f"✅ Found {len(results['comments'])} comment(s)")
    else:
        print("⚠️  No comments found (this is OK if database is empty)")
    
    # Test 3: Combined search
    print("\n3. Testing combined search...")
    results = search_system.search("marketing", content_types=['articles', 'comments'], limit=10)
    
    total = sum(len(df) for df in results.values() if not df.empty)
    print(f"✅ Total results: {total}")
    
    print("\n" + "=" * 60)
    print("Search System Tests Complete")
    print("=" * 60)


def test_recommendation_engine():
    """Test recommendation engine functionality."""
    print("\n" + "=" * 60)
    print("Testing Recommendation Engine")
    print("=" * 60)
    
    # Initialize systems
    db_manager = get_database_manager()
    rec_engine = get_recommendation_engine(db_manager)
    
    # Test 1: Get trending articles
    print("\n1. Testing trending articles...")
    trending = rec_engine.get_trending_articles(limit=5)
    
    if not trending.empty:
        print(f"✅ Found {len(trending)} trending article(s)")
        print("\nTop trending:")
        top = trending.iloc[0]
        print(f"   Title: {top['title']}")
        print(f"   Score: {top['trending_score']:.2f}")
    else:
        print("⚠️  No trending articles (this is OK if database is empty)")
    
    # Test 2: Get related articles (if any exist)
    print("\n2. Testing related articles...")
    if not trending.empty:
        article_id = int(trending.iloc[0]['id'])
        related = rec_engine.get_related_articles(article_id, limit=3)
        
        if not related.empty:
            print(f"✅ Found {len(related)} related article(s)")
        else:
            print("⚠️  No related articles found")
    else:
        print("⚠️  Skipped (no articles in database)")
    
    print("\n" + "=" * 60)
    print("Recommendation Engine Tests Complete")
    print("=" * 60)


def check_database_content():
    """Check what content exists in the database."""
    print("\n" + "=" * 60)
    print("Database Content Check")
    print("=" * 60)
    
    db_manager = get_database_manager()
    
    # Check articles
    articles = db_manager.execute_query(
        "SELECT COUNT(*) as count FROM articles WHERE status = 'published'",
        ()
    )
    article_count = articles.iloc[0]['count'] if not articles.empty else 0
    print(f"\n📄 Published Articles: {article_count}")
    
    # Check comments
    comments = db_manager.execute_query(
        "SELECT COUNT(*) as count FROM comments WHERE is_approved = 1",
        ()
    )
    comment_count = comments.iloc[0]['count'] if not comments.empty else 0
    print(f"💬 Approved Comments: {comment_count}")
    
    # Check feedback
    feedback = db_manager.execute_query(
        "SELECT COUNT(*) as count FROM user_feedback",
        ()
    )
    feedback_count = feedback.iloc[0]['count'] if not feedback.empty else 0
    print(f"⭐ Feedback Entries: {feedback_count}")
    
    if article_count == 0:
        print("\n⚠️  Note: Database appears empty. Search will return no results.")
        print("   To test with data, create some articles through the app first.")
    
    print("=" * 60)


if __name__ == "__main__":
    print("\n🔍 Search & Recommendation System Test Suite\n")
    
    # Check database content first
    check_database_content()
    
    # Test search system
    test_search_system()
    
    # Test recommendation engine
    test_recommendation_engine()
    
    print("\n✅ All tests completed!\n")
    print("Next steps:")
    print("1. Run 'streamlit run streamlit_app.py' to test in the UI")
    print("2. Login and navigate to '🔍 搜索 / Search'")
    print("3. Try searching for content")
    print()
