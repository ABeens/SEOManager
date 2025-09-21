import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

from .research_agent import ResearchAgent
from .smart_research_agent import SmartResearchAgent
from .content_agents import PlannerAgent, WriterAgent, EditorAgent

# Configuration
class Config:
    """Configuration settings for the ManagerAgent"""
    # Default paths relative to the project root
    DEFAULT_OUTPUT_DIR = "./output_hierarchical"
    ASTRO_BLOG_DIR = "../seo-manager-blog/src/content/blog"
    ASTRO_PROJECT_DIR = "../seo-manager-blog"


class ManagerAgent:
    """Orchestrates the multi-agent blog post generation workflow"""

    def __init__(self, output_dir: str = None, use_smart_cache: bool = True,
                 astro_blog_dir: str = None, astro_project_dir: str = None):
        # Use config defaults if not provided
        self.output_dir = Path(output_dir or Config.DEFAULT_OUTPUT_DIR)
        self.output_dir.mkdir(exist_ok=True)
        self.astro_blog_dir = Path(astro_blog_dir or Config.ASTRO_BLOG_DIR)
        self.astro_project_dir = Path(astro_project_dir or Config.ASTRO_PROJECT_DIR)
        self.use_smart_cache = use_smart_cache

        # Initialize agents
        if use_smart_cache:
            self.researcher = SmartResearchAgent()
        else:
            self.researcher = ResearchAgent()

        self.planner = PlannerAgent()
        self.writer = WriterAgent()
        self.editor = EditorAgent()

    def generate_blog_post(self, topic: str, keyword: str, tone: str) -> Dict[str, Any]:
        """
        Generate a competitive blog post using multi-agent workflow

        Args:
            topic: The main topic for the blog post
            keyword: SEO keyword to target
            tone: Writing tone (e.g., 'professional', 'casual', 'technical')

        Returns:
            Dict containing the generated content and metadata
        """
        logger.info("Manager: Starting competitive research...")

        # Research phase with smart caching
        research_context = f"{topic}, {keyword}"

        if self.use_smart_cache:
            # Use smart research with caching
            smart_result = self.researcher.smart_competitive_analysis(keyword=research_context)
            competitive_data = {
                'top_competitors': smart_result['top_competitors'],
                'people_also_ask': smart_result['people_also_ask'],
                'related_searches': smart_result['related_searches']
            }
            trending_data = smart_result['trending_topics']

            # Add cache info to results
            if smart_result.get('adaptation_info'):
                logger.info(f"Adapted from: {smart_result['adaptation_info']['based_on']}")

        else:
            # Use traditional research
            competitive_data = self.researcher.competitive_analysis(keyword=research_context)
            trending_data = self.researcher.trending_topics(research_context)

        logger.info(f"Analyzed {len(competitive_data['top_competitors'])} competitors")
        logger.info(f"Found {len(competitive_data['people_also_ask'])} frequently asked questions")

        # Planning phase
        logger.info("Manager: Generating competitive outline...")
        outline = self.planner.generate_outline({
            "topic": topic,
            "keyword": research_context,
            "tone": tone,
            "competitors": competitive_data["top_competitors"],
            "people_ask": competitive_data["people_also_ask"],
            "related_searches": competitive_data["related_searches"],
            "trending": trending_data
        })

        # Writing phase
        logger.info("Manager: Writing content...")
        draft = self.writer.write_content(outline, keyword, tone)

        # Editing phase
        logger.info("Manager: Editing and polishing...")
        final_post = self.editor.edit_content(draft)

        # Prepare results
        result = {
            "topic": topic,
            "keyword": keyword,
            "tone": tone,
            "outline": outline,
            "draft": draft,
            "final_post": final_post,
            "competitive_analysis": competitive_data,
            "trending_topics": trending_data
        }

        # Save results
        self._save_results(result)

        # Save to Astro blog directory and build
        blog_slug = self._save_to_astro_blog(result)
        self._build_astro_project()

        # Add blog slug to result for frontend redirect
        result["blog_slug"] = blog_slug
        result["blog_url"] = f"/blog/{blog_slug}"

        logger.info("Blog post generated successfully")
        return result

    def _save_results(self, result: Dict[str, Any]) -> None:
        """Save generation results to files"""

        # Save complete metadata
        metadata = {
            "topic": result["topic"],
            "keyword": result["keyword"],
            "tone": result["tone"],
            "outline": result["outline"],
            "competitive_analysis": result["competitive_analysis"],
            "trending_topics": result["trending_topics"]
        }

        with open(self.output_dir / "post_metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        # Save competitive research separately
        with open(self.output_dir / "competitive_research.json", "w", encoding="utf-8") as f:
            json.dump(result["competitive_analysis"], f, ensure_ascii=False, indent=2)

        # Save final blog post
        with open(self.output_dir / "post.md", "w", encoding="utf-8") as f:
            f.write(result["final_post"])

        logger.info("Files saved to ./output_hierarchical/")

    def _save_to_astro_blog(self, result: Dict[str, Any]) -> None:
        """Save blog post to Astro blog directory with proper frontmatter"""
        try:
            # Create filename from topic
            topic_slug = result["topic"].lower().replace(" ", "-").replace("'", "").replace(":", "")
            topic_slug = "".join(char for char in topic_slug if char.isalnum() or char == "-")
            filename = f"{topic_slug}.md"

            # Get current date and time for frontmatter
            current_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            # Generate relevant tags from topic and keyword
            tags = self._generate_tags(result['topic'], result['keyword'])

            # Create Astro frontmatter
            frontmatter = f"""---
title: "{result['topic'].capitalize()}"
description: "A comprehensive guide about {result['topic']}"
pubDate: "{current_date}"
author: "SEO Manager"
tags: {tags}
---
"""

            # Combine frontmatter with content
            astro_content = frontmatter + result["final_post"]

            # Save to Astro blog directory
            astro_file_path = self.astro_blog_dir / filename
            with open(astro_file_path, "w", encoding="utf-8") as f:
                f.write(astro_content)

            logger.info(f"Blog post saved to Astro directory: {astro_file_path}")

        except Exception as e:
            logger.error(f"Error saving to Astro blog directory: {e}")

    def _generate_tags(self, topic: str, keyword: str) -> str:
        """Generate relevant tags from topic and keyword"""
        tags = []

        # Add keyword as primary tag
        if keyword:
            tags.append(keyword.lower())

        # Extract words from topic (filter out common words)
        common_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'about', 'how', 'what', 'when', 'where', 'why', 'who', 'which'}

        topic_words = [word.lower().strip('.,!?:;') for word in topic.split()
                      if word.lower().strip('.,!?:;') not in common_words and len(word) > 2]

        # Add up to 3 meaningful words from topic
        for word in topic_words[:3]:
            if word not in tags:
                tags.append(word)

        # Add generic tags
        tags.extend(["guide", "tutorial"])

        # Format as JSON array for YAML
        formatted_tags = [f'"{tag}"' for tag in tags[:5]]  # Limit to 5 tags
        return f"[{', '.join(formatted_tags)}]"

    def _build_astro_project(self) -> None:
        """Build the Astro project after adding new content"""
        # Check if we're in development mode
        environment = os.getenv('ENVIRONMENT', 'development')

        if environment == 'development':
            logger.info("Development mode: Skipping build - Astro dev server will auto-reload")
            return

        try:
            logger.info("Production mode: Building Astro project...")

            # Change to Astro project directory and run build
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=self.astro_project_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                logger.info("Astro project built successfully")
                logger.info(f"Build output: {result.stdout}")
            else:
                logger.error(f"Astro build failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            logger.error("Astro build timed out after 5 minutes")
        except Exception as e:
            logger.error(f"Error building Astro project: {e}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics if using smart cache"""
        if self.use_smart_cache and hasattr(self.researcher, 'get_cache_statistics'):
            return self.researcher.get_cache_statistics()
        return {"cache_enabled": False}

    def clear_cache(self) -> bool:
        """Clear cache if using smart cache"""
        if self.use_smart_cache and hasattr(self.researcher, 'clear_cache'):
            return self.researcher.clear_cache()
        return False