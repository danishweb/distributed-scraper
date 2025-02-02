from storage.redis_client import RedisClient
import asyncio
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Worker:
    def __init__(self):
        self.redisClient = RedisClient()

    async def work(self):
        while True:
            task = await self.redisClient.get_task()
            if task:
                try:
                    url, priority = json.loads(task)
                    print(url, priority)
                except Exception as e:
                    logger.error(f"Error processing task: {e}")
            await asyncio.sleep(1)