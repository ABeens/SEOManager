"""
Example usage of the SEO Manager with smart caching system
"""

import logging
from dotenv import load_dotenv
from agents.manager_agent import ManagerAgent
from utils.logger_config import LoggingConfig

# Load environment variables
load_dotenv()

# Configure logging
LoggingConfig.testing()
logger = logging.getLogger(__name__)


def main():
    # Initialize manager with smart caching enabled (default)
    manager = ManagerAgent(use_smart_cache=True)

    # Test topics that should demonstrate caching benefits
    test_topics = [
        ("content marketing for ecommerce", "content marketing", "professional"),
        ("email marketing for ecommerce", "email marketing", "professional"),  # Similar to first
        ("social media marketing for startups", "social media", "casual"),
        ("digital marketing for startups", "digital marketing", "casual"),  # Similar to third
    ]

    logger.info("Testing SEO Content Cache System")
    logger.info("=" * 50)

    for i, (topic, keyword, tone) in enumerate(test_topics, 1):
        logger.info(f"\nTest {i}: {topic}")
        logger.info("-" * 30)

        # Generate blog post
        result = manager.generate_blog_post(topic, keyword, tone)

        logger.info(f"Generated post for: {topic}")
        logger.info(f"Content length: {len(result['final_post'])} characters")
        logger.info(f"Competitors analyzed: {len(result['competitive_analysis']['top_competitors'])}")

        # Show cache statistics after each run
        stats = manager.get_cache_stats()
        if stats.get('total_cached_topics'):
            logger.info(f"Total cached topics: {stats['total_cached_topics']}")

    logger.info("\n" + "=" * 50)
    logger.info("All tests completed!")

    # Final cache statistics
    final_stats = manager.get_cache_stats()
    logger.info(f"Final cache stats: {final_stats}")


def test_cache_similarity():
    """Test the cache similarity detection"""
    manager = ManagerAgent(use_smart_cache=True)

    logger.info("\nTesting Cache Similarity Detection")
    logger.info("=" * 50)

    # First topic - will create cache entry
    logger.info("\n1. First topic (will be cached):")
    result1 = manager.generate_blog_post(
        "content marketing for restaurants",
        "restaurant marketing",
        "professional"
    )

    # Similar topic - should use cache
    logger.info("\n2. Similar topic (should use cache):")
    result2 = manager.generate_blog_post(
        "content marketing for cafes",
        "cafe marketing",
        "professional"
    )

    # Very different topic - should NOT use cache
    logger.info("\n3. Different topic (should NOT use cache):")
    result3 = manager.generate_blog_post(
        "machine learning algorithms",
        "AI algorithms",
        "technical"
    )


def clear_cache_example():
    """Example of clearing the cache"""
    manager = ManagerAgent(use_smart_cache=True)

    logger.info("\nCache Management Example")
    logger.info("=" * 30)

    # Show current stats
    stats = manager.get_cache_stats()
    logger.info(f"Before clear: {stats}")

    # Clear cache
    success = manager.clear_cache()
    logger.info(f"Cache cleared: {success}")

    # Show stats after clear
    stats_after = manager.get_cache_stats()
    logger.info(f"After clear: {stats_after}")


if __name__ == "__main__":
    # Run main example
    main()

    # Uncomment to test specific features
    # test_cache_similarity()
    # clear_cache_example()