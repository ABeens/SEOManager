from dotenv import load_dotenv
from agents.manager_agent import ManagerAgent
from utils.logger_config import LoggingConfig
import logging

# Load environment variables
load_dotenv()

# Configure logging
LoggingConfig.development()
logger = logging.getLogger(__name__)

# ---------------------------
# CLI Usage (Legacy)
# ---------------------------
if __name__ == "__main__":
    manager = ManagerAgent()
    result = manager.generate_blog_post("Costa Rica", "tourism", "fun")
    logger.info("\nBlog post generated successfully!")
    logger.info(f"Final content: {len(result['final_post'])} characters")
    logger.info(f"Competitors analyzed: {len(result['competitive_analysis']['top_competitors'])}")
    logger.info(f"Questions found: {len(result['competitive_analysis']['people_also_ask'])}")
