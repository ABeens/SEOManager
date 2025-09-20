import os
from serpapi import GoogleSearch
from typing import Dict, List


class ResearchAgent:
    """Research agent for competitive analysis using SerpAPI"""

    def __init__(self):
        self.api_key = os.getenv('SERP_API_KEY')
        if not self.api_key:
            raise ValueError("SERP_API_KEY not found in environment variables")

    def competitive_analysis(self, keyword: str, num_results: int = 10) -> Dict:
        """Analyze top competing articles for a keyword"""
        search = GoogleSearch({
            "q": keyword,
            "api_key": self.api_key,
            "num": num_results,
            "hl": "en",  # English results
            "gl": "us"   # US location
        })

        results = search.get_dict()

        # Extract competitive insights
        analysis = {
            "top_competitors": [],
            "trending_topics": [],
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

        return analysis

    def trending_topics(self, base_keyword: str) -> List[Dict]:
        """Get trending topics related to base keyword"""
        search = GoogleSearch({
            "q": f"{base_keyword} 2024 trends",
            "api_key": self.api_key,
            "tbm": "nws",  # News results
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