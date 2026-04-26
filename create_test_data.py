"""
Create test data for search functionality testing.

This script creates sample articles and comments to test search and recommendations.
"""

from modules.database import get_database_manager
from modules.articles import get_article_manager
from modules.auth import get_auth_manager
from modules.comments import get_comment_system

def create_sample_articles():
    """Create sample articles for testing."""
    print("Creating sample articles...")
    
    db_manager = get_database_manager()
    auth_manager = get_auth_manager(db_manager=db_manager)
    article_manager = get_article_manager(db_manager, auth_manager)
    
    sample_articles = [
        {
            "title": "The Evolution of Digital Advertising",
            "content": """# The Evolution of Digital Advertising

Digital advertising has transformed dramatically over the past two decades. From simple banner ads to sophisticated programmatic campaigns, the industry has evolved to meet changing consumer behaviors and technological advances.

## Key Milestones

1. **Early 2000s**: Banner ads and pop-ups dominated
2. **2010s**: Social media advertising emerged
3. **2020s**: AI-driven personalization and privacy concerns

The future of advertising lies in balancing personalization with privacy, creating authentic connections with audiences while respecting their data rights.""",
            "excerpt": "Exploring how digital advertising has evolved from simple banners to AI-driven campaigns.",
            "category": "Digital Marketing",
            "tags": "digital, advertising, evolution, technology",
            "author": "professor",
            "status": "published"
        },
        {
            "title": "Classic Advertising Campaigns That Changed History",
            "content": """# Classic Advertising Campaigns That Changed History

Some advertising campaigns transcend their commercial purpose to become cultural phenomena. This article explores iconic campaigns that shaped the advertising industry.

## Notable Examples

- **Nike's "Just Do It"**: Empowerment through sports
- **Apple's "Think Different"**: Celebrating innovation
- **Coca-Cola's "Share a Coke"**: Personalization at scale

These campaigns succeeded because they connected emotionally with audiences and reflected cultural values.""",
            "excerpt": "A look at iconic advertising campaigns that became cultural landmarks.",
            "category": "Advertising History",
            "tags": "classic, campaigns, history, branding",
            "author": "professor",
            "status": "published"
        },
        {
            "title": "Marketing Theory: Understanding Consumer Behavior",
            "content": """# Marketing Theory: Understanding Consumer Behavior

Consumer behavior is at the heart of effective marketing. Understanding what drives purchasing decisions helps create more effective advertising strategies.

## Key Concepts

1. **Maslow's Hierarchy of Needs**: Understanding motivation
2. **Cognitive Dissonance**: Post-purchase rationalization
3. **Social Proof**: The power of recommendations

Modern marketing combines these psychological principles with data analytics to create targeted, effective campaigns.""",
            "excerpt": "Exploring the psychological principles behind consumer purchasing decisions.",
            "category": "Marketing Theory",
            "tags": "marketing, theory, psychology, consumer behavior",
            "author": "professor",
            "status": "published"
        },
        {
            "title": "The Rise of Influencer Marketing",
            "content": """# The Rise of Influencer Marketing

Influencer marketing has become a dominant force in digital advertising. Brands partner with social media personalities to reach engaged audiences authentically.

## Why It Works

- **Trust**: Followers trust influencer recommendations
- **Reach**: Access to targeted demographics
- **Authenticity**: More genuine than traditional ads

However, challenges include measuring ROI and ensuring authentic partnerships.""",
            "excerpt": "How influencer marketing has transformed brand communication strategies.",
            "category": "Digital Marketing",
            "tags": "influencer, social media, marketing, digital",
            "author": "admin",
            "status": "published"
        },
        {
            "title": "Creative Strategies in Modern Advertising",
            "content": """# Creative Strategies in Modern Advertising

Creativity remains the cornerstone of effective advertising. This article explores strategies that help brands stand out in crowded markets.

## Effective Approaches

1. **Storytelling**: Creating emotional narratives
2. **Humor**: Making brands memorable
3. **Shock Value**: Breaking through the noise
4. **Minimalism**: Less is more

The best creative strategies align with brand values while surprising and delighting audiences.""",
            "excerpt": "Exploring creative approaches that make advertising campaigns memorable and effective.",
            "category": "Creative Strategies",
            "tags": "creativity, strategy, branding, campaigns",
            "author": "admin",
            "status": "published"
        }
    ]
    
    created_count = 0
    for article_data in sample_articles:
        success = article_manager.save_article(**article_data)
        if success:
            created_count += 1
            print(f"  ✅ Created: {article_data['title']}")
        else:
            print(f"  ❌ Failed: {article_data['title']}")
    
    print(f"\n✅ Created {created_count}/{len(sample_articles)} articles")
    return created_count


def create_sample_comments():
    """Create sample comments for testing."""
    print("\nCreating sample comments...")
    
    db_manager = get_database_manager()
    comment_system = get_comment_system(db_manager)
    
    sample_comments = [
        {
            "username": "student",
            "target_type": "article",
            "target_id": "1",
            "content": "Great article! The evolution of digital advertising is fascinating. I especially liked the section on AI-driven personalization."
        },
        {
            "username": "professor",
            "target_type": "article",
            "target_id": "1",
            "content": "Thank you! The balance between personalization and privacy will be crucial in the coming years."
        },
        {
            "username": "student",
            "target_type": "article",
            "target_id": "2",
            "content": "The Nike 'Just Do It' campaign is still relevant today. Amazing how some campaigns transcend time."
        },
        {
            "username": "admin",
            "target_type": "article",
            "target_id": "3",
            "content": "Understanding consumer psychology is essential for any marketer. Excellent overview of key theories."
        }
    ]
    
    created_count = 0
    for comment_data in sample_comments:
        success = comment_system.add_comment(**comment_data)
        if success:
            created_count += 1
            print(f"  ✅ Created comment by {comment_data['username']}")
        else:
            print(f"  ❌ Failed to create comment")
    
    print(f"\n✅ Created {created_count}/{len(sample_comments)} comments")
    return created_count


if __name__ == "__main__":
    print("\n📝 Creating Test Data for Search System\n")
    print("=" * 60)
    
    # Create articles
    article_count = create_sample_articles()
    
    # Create comments
    comment_count = create_sample_comments()
    
    print("\n" + "=" * 60)
    print("✅ Test Data Creation Complete!")
    print("=" * 60)
    print(f"\nCreated:")
    print(f"  📄 {article_count} articles")
    print(f"  💬 {comment_count} comments")
    print("\nYou can now test the search functionality:")
    print("1. Run: python test_search_manual.py")
    print("2. Or run: streamlit run streamlit_app.py")
    print()
