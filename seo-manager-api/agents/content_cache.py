import json
import logging
import chromadb
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)


class SEOContentCache:
    """Semantic cache system for SEO content to avoid costly API calls"""

    def __init__(self, cache_dir: str = "./seo_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=str(self.cache_dir))
        self.collection = self.client.get_or_create_collection(
            name="seo_topics",
            metadata={"hnsw:space": "cosine"}
        )

    def find_similar_analysis(self, topic: str, similarity_threshold: float = 0.82) -> Dict[str, Any]:
        """
        Search for similar SEO analysis in cache

        Args:
            topic: The topic to search for
            similarity_threshold: Minimum similarity score (0-1)

        Returns:
            Dict with found status and cached data if available
        """
        try:
            results = self.collection.query(
                query_texts=[topic],
                n_results=3
            )

            if not results['documents'][0]:
                return {'found': False}

            for i, distance in enumerate(results['distances'][0]):
                similarity = 1 - distance
                if similarity >= similarity_threshold:
                    metadata = results['metadatas'][0][i]

                    return {
                        'found': True,
                        'similarity': similarity,
                        'original_topic': results['documents'][0][i],
                        'serp_data': json.loads(metadata['serp_data']),
                        'competitors': json.loads(metadata['competitors']),
                        'people_also_ask': json.loads(metadata['people_also_ask']),
                        'related_searches': json.loads(metadata['related_searches']),
                        'trending_topics': json.loads(metadata.get('trending_topics', '[]')),
                        'cached_date': metadata['date'],
                        'id': results['ids'][0][i]
                    }

            return {'found': False}

        except Exception as e:
            logger.error(f"Error searching cache: {e}")
            return {'found': False}

    def cache_serp_analysis(self, topic: str, competitive_data: Dict, trending_data: List) -> bool:
        """
        Cache complete SERP analysis data

        Args:
            topic: The analyzed topic
            competitive_data: Competitive analysis from ResearchAgent
            trending_data: Trending topics data

        Returns:
            Success status
        """
        try:
            # Create unique ID
            topic_hash = hashlib.md5(topic.encode()).hexdigest()
            timestamp = int(datetime.now().timestamp())
            doc_id = f"serp_{topic_hash}_{timestamp}"

            # Prepare metadata
            metadata = {
                'serp_data': json.dumps(competitive_data.get('top_competitors', [])),
                'competitors': json.dumps(competitive_data.get('top_competitors', [])),
                'people_also_ask': json.dumps(competitive_data.get('people_also_ask', [])),
                'related_searches': json.dumps(competitive_data.get('related_searches', [])),
                'trending_topics': json.dumps(trending_data),
                'date': datetime.now().isoformat(),
                'topic_hash': topic_hash
            }

            # Store in ChromaDB
            self.collection.add(
                documents=[topic],
                metadatas=[metadata],
                ids=[doc_id]
            )

            return True

        except Exception as e:
            logger.error(f"Error caching analysis: {e}")
            return False

    def adapt_cached_data(self, original_topic: str, new_topic: str, cached_data: Dict) -> Dict[str, Any]:
        """
        Adapt cached analysis data for a new similar topic

        Args:
            original_topic: The original cached topic
            new_topic: The new topic to adapt for
            cached_data: The cached analysis data

        Returns:
            Adapted analysis data
        """
        # Extract main terms for substitution
        original_main_term = self._extract_main_term(original_topic)
        new_main_term = self._extract_main_term(new_topic)

        # Adapt competitors data
        adapted_competitors = []
        for competitor in cached_data.get('competitors', []):
            adapted_competitor = competitor.copy()
            # Keep structure but note it's adapted
            adapted_competitor['adapted_from'] = original_topic
            adapted_competitor['adaptation_note'] = f"Structure from {original_main_term} analysis"
            adapted_competitors.append(adapted_competitor)

        # Adapt People Also Ask questions
        adapted_paa = []
        for question in cached_data.get('people_also_ask', []):
            # Try to substitute main terms
            adapted_question = question.replace(original_main_term, new_main_term)
            if adapted_question != question:
                adapted_paa.append(adapted_question)
            else:
                # If no substitution possible, keep original but mark as reference
                adapted_paa.append(f"[Similar to {original_main_term}] {question}")

        # Adapt related searches
        adapted_related = []
        for search in cached_data.get('related_searches', []):
            adapted_search = search.replace(original_main_term, new_main_term)
            adapted_related.append(adapted_search)

        # Create adapted result structure
        adapted_result = {
            'adaptation_info': {
                'based_on': original_topic,
                'adapted_for': new_topic,
                'similarity': cached_data.get('similarity', 0),
                'cached_date': cached_data.get('cached_date'),
                'adaptation_date': datetime.now().isoformat()
            },
            'competitive_analysis': {
                'top_competitors': adapted_competitors,
                'people_also_ask': adapted_paa,
                'related_searches': adapted_related
            },
            'trending_topics': cached_data.get('trending_topics', []),
            'serp_data': cached_data.get('serp_data', [])
        }

        return adapted_result

    def _extract_main_term(self, topic: str) -> str:
        """Extract the main term from a topic for substitution"""
        # Simple extraction - can be made more sophisticated
        words = topic.lower().split()

        # Filter out common words
        stop_words = {'for', 'in', 'on', 'with', 'the', 'a', 'an', 'and', 'or', 'but', 'to', 'of'}
        main_words = [word for word in words if word not in stop_words]

        # Return the first significant word or the whole topic
        return main_words[0] if main_words else topic

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about the cache"""
        try:
            all_items = self.collection.get()
            total_items = len(all_items['ids']) if all_items['ids'] else 0

            return {
                'total_cached_topics': total_items,
                'cache_directory': str(self.cache_dir),
                'collection_name': self.collection.name
            }

        except Exception as e:
            return {'error': str(e)}

    def clear_cache(self) -> bool:
        """Clear all cached data"""
        try:
            self.client.delete_collection(name="seo_topics")
            self.collection = self.client.get_or_create_collection(
                name="seo_topics",
                metadata={"hnsw:space": "cosine"}
            )
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False