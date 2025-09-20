import os
import logging
from serpapi import GoogleSearch
from typing import Dict, List, Optional, Any
from .content_cache import SEOContentCache

logger = logging.getLogger(__name__)


class SmartResearchAgent:
    """Enhanced research agent that uses semantic caching to avoid costly API calls"""

    def __init__(self, similarity_threshold: float = 0.82):
        self.api_key = os.getenv('SERP_API_KEY')
        if not self.api_key:
            raise ValueError("SERP_API_KEY not found in environment variables")

        self.cache = SEOContentCache()
        self.similarity_threshold = similarity_threshold

    def smart_competitive_analysis(self, keyword: str, num_results: int = 10) -> Dict[str, Any]:
        """
        Perform competitive analysis with intelligent caching

        Args:
            keyword: The keyword to analyze
            num_results: Number of results to fetch (if not cached)

        Returns:
            Analysis data (either from cache or fresh API call)
        """
        logger.info(f"Searching for similar analysis to: {keyword}")

        # Check cache first
        cached_result = self.cache.find_similar_analysis(keyword, self.similarity_threshold)

        if cached_result['found']:
            logger.info(f"Found similar topic: {cached_result['original_topic']}")
            logger.info(f"Similarity: {cached_result['similarity']:.2%}")
            logger.info("Using cached data - No API calls needed!")

            # Adapt cached data for new keyword
            adapted_data = self.cache.adapt_cached_data(
                original_topic=cached_result['original_topic'],
                new_topic=keyword,
                cached_data=cached_result
            )

            return {
                'source': 'cache_adapted',
                'adaptation_info': adapted_data['adaptation_info'],
                'top_competitors': adapted_data['competitive_analysis']['top_competitors'],
                'people_also_ask': adapted_data['competitive_analysis']['people_also_ask'],
                'related_searches': adapted_data['competitive_analysis']['related_searches'],
                'trending_topics': adapted_data['trending_topics']
            }

        else:
            logger.info("No similar topics found in cache")
            logger.info("Performing fresh API analysis...")

            # Perform fresh analysis
            return self._fresh_competitive_analysis(keyword, num_results)

    def _fresh_competitive_analysis(self, keyword: str, num_results: int = 10) -> Dict[str, Any]:
        """Perform fresh competitive analysis using SerpAPI"""
        search = GoogleSearch({
            "q": keyword,
            "api_key": self.api_key,
            "num": num_results,
            "hl": "en",
            "gl": "us"
        })

        results = search.get_dict()

        # Extract competitive insights
        analysis = {
            "top_competitors": [],
            "people_also_ask": [],
            "related_searches": []
        }

        # Top organic results analysis
        if "organic_results" in results:
            for result in results["organic_results"][:5]:
                competitor = {
                    "title": result.get("title", ""),
                    "snippet": result.get("snippet", ""),
                    "link": result.get("link", ""),
                    "position": result.get("position", 0)
                }
                analysis["top_competitors"].append(competitor)

        # People also ask questions
        if "people_also_ask" in results:
            analysis["people_also_ask"] = [
                paa.get("question", "") for paa in results["people_also_ask"]
            ]

        # Related searches
        if "related_searches" in results:
            analysis["related_searches"] = [
                rs.get("query", "") for rs in results["related_searches"]
            ]

        # Get trending topics
        trending_data = self._fresh_trending_topics(keyword)

        # Cache the fresh results
        self.cache.cache_serp_analysis(
            topic=keyword,
            competitive_data=analysis,
            trending_data=trending_data
        )

        logger.info("Fresh analysis cached for future use")

        return {
            'source': 'fresh_api',
            'top_competitors': analysis['top_competitors'],
            'people_also_ask': analysis['people_also_ask'],
            'related_searches': analysis['related_searches'],
            'trending_topics': trending_data
        }

    def _fresh_trending_topics(self, base_keyword: str) -> List[Dict]:
        """Get trending topics related to base keyword"""
        search = GoogleSearch({
            "q": f"{base_keyword} 2024 trends",
            "api_key": self.api_key,
            "tbm": "nws",
            "hl": "en",
            "gl": "us"
        })

        results = search.get_dict()
        trending = []

        if "news_results" in results:
            for news in results["news_results"][:5]:
                trending.append({
                    "title": news.get("title", ""),
                    "source": news.get("source", ""),
                    "date": news.get("date", "")
                })

        return trending

    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        return self.cache.get_cache_stats()

    def force_fresh_analysis(self, keyword: str, num_results: int = 10) -> Dict[str, Any]:
        """Force a fresh analysis even if cache exists"""
        logger.info("Forcing fresh analysis (ignoring cache)")
        return self._fresh_competitive_analysis(keyword, num_results)

    def clear_cache(self) -> bool:
        """Clear all cached data"""
        return self.cache.clear_cache()

    # Backward compatibility method
    def competitive_analysis(self, keyword: str, num_results: int = 10) -> Dict:
        """Backward compatible method"""
        result = self.smart_competitive_analysis(keyword, num_results)

        # Return in original format
        return {
            'top_competitors': result['top_competitors'],
            'people_also_ask': result['people_also_ask'],
            'related_searches': result['related_searches']
        }

    def trending_topics(self, base_keyword: str) -> List[Dict]:
        """Backward compatible trending topics method"""
        # Check if we have cached trending data
        cached_result = self.cache.find_similar_analysis(base_keyword, self.similarity_threshold)

        if cached_result['found']:
            return cached_result.get('trending_topics', [])
        else:
            return self._fresh_trending_topics(base_keyword)