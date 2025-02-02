import os
import sys
import asyncio
import argparse

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from src.core.proxy_manager import ProxyManager
from src.tasks.generator import Generator
from src.core.scraper import scrape_product
from src.storage.redis_client import RedisClient
from config.settings import HEADERS
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def generate_tasks():
    """Generate sample tasks and add them to Redis"""
    generator = Generator()
    urls = [
        "https://www.amazon.com/dp/B0B8QwGMD?th=1", 
    ]
    for index, url in enumerate(urls, 1):
        await generator.add_url(url, index)
    logger.info("Tasks generated successfully")

async def process_tasks():
    """Process tasks from Redis queue"""
    redis_client = RedisClient()
    while True:
        task = await redis_client.get_task()
        if task:
            logger.info(f"Processing task: {task}")
            try:
                # Get the URL and priority from task
                url = task['url']
                priority = task['priority']
                
                # Process the task using our scraper with default settings
                result = await scrape_product(
                    url=url,
                    headers=HEADERS,   
                    timeout=30, 
                    proxy=None  
                )
                logger.info(f"Task completed. Result: {result}")

                await redis_client.remove_task(obj=task)
            except Exception as e:
                logger.error(f"Error processing task: {e}")
        else:
            logger.info("No tasks available. Waiting...")
            await asyncio.sleep(5)  # Wait before checking again

async def clean_proxies():
    """Validate all proxies and keep only the working ones"""
    proxy_manager = ProxyManager()
    await proxy_manager.validate_proxies()
    logger.info("Proxy validation completed")
    
async def main():
    parser = argparse.ArgumentParser(description='Distributed Scraper')
    parser.add_argument('--mode', choices=['generate', 'process', 'clean_proxies'], required=True,
                      help='Mode to run: generate tasks or process tasks')
    
    args = parser.parse_args()
    
    if args.mode == 'generate':
        await generate_tasks()
    elif args.mode == 'process':
        await process_tasks()
    elif args.mode == 'clean_proxies':
        await clean_proxies()

if __name__ == "__main__":
    asyncio.run(main())
