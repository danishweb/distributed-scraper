import asyncio
import logging
from typing import Dict, Any

from src.storage.redis_client import RedisClient
from src.core.scraper import scrape_product
from src.core.proxy_manager import ProxyManager
from config.settings import HEADERS

logger = logging.getLogger(__name__)

class Worker:
    def __init__(self, worker_id: str):
        """Initialize a worker process
        
        Args:
            worker_id: Unique identifier for this worker
        """
        self.worker_id = worker_id
        self.redis_client = RedisClient()
        self.proxy_manager = ProxyManager()
        self.running = False
        
    async def process_task(self, task: Dict[str, Any]) -> bool:
        try:
            url = task['url']
            priority = task['priority']
            
            # Get a proxy from the proxy manager
            proxy = self.proxy_manager.get_proxy()
            
            # Process the task using our scraper
            result = await scrape_product(
                url=url,
                headers=HEADERS,
                timeout=30,
                proxy=proxy
            )
            
            logger.info(f"Worker {self.worker_id}: Task completed. Result: {result}")
            await self.redis_client.remove_task(obj=task)
            return True
            
        except Exception as e:
            logger.error(f"Worker {self.worker_id}: Error processing task: {e}")
            return False
    
    async def start(self):
        """Start the worker process"""
        logger.info(f"Worker {self.worker_id}: Starting...")
        self.running = True
        
        while self.running:
            task = await self.redis_client.get_task()
            if task:
                logger.info(f"Worker {self.worker_id}: Processing task: {task}")
                await self.process_task(task)
            else:
                logger.info(f"Worker {self.worker_id}: No tasks available. Waiting...")
                await asyncio.sleep(5)  # Wait before checking again
    
    def stop(self):
        """Stop the worker process"""
        logger.info(f"Worker {self.worker_id}: Stopping...")
        self.running = False