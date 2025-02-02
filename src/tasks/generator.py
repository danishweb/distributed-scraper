import os
import sys
import logging

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.storage.redis_client import RedisClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Generator:
    def __init__(self):
        self.redisClient = RedisClient()


    async def add_url(self, url:str, priority:int):
        try:
            if not url.strip().startswith(("http://", "https://")):
                logger.info(f"Invalid URL: {url}. Skipping.")
                return
            success = await self.redisClient.add_task(url, priority)

            if success:
                logger.info(f"Added URL: {url}")
            else:
                logger.info(f"URL already exists: {url}")
            return success
        except Exception as e:
            logger.error(f"Error adding URL: {url}. Error: {str(e)}")
            return False