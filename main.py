import os
import sys
import asyncio
import argparse
import uuid

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from src.core.proxy_manager import ProxyManager
from src.tasks.generator import Generator
from src.tasks.worker import Worker
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
        "https://www.amazon.com/dp/B0B8Q9FGMD",
        "https://www.amazon.com/dp/B0B8Q9FGME", 
        "https://www.amazon.com/dp/B0B8Q9FGMF",
    ]
    for index, url in enumerate(urls, 1):
        await generator.add_url(url, index)
    logger.info("Tasks generated successfully")

async def process_tasks(num_workers: int = 2):
    workers = []
    for i in range(num_workers):
        worker_id = f"worker_{uuid.uuid4().hex[:8]}"
        worker = Worker(worker_id)
        workers.append(worker)
    
    # Start all workers
    worker_tasks = [worker.start() for worker in workers]
    try:
        # Wait for all workers to complete
        await asyncio.gather(*worker_tasks)
    except KeyboardInterrupt:
        logger.info("Shutting down workers...")
        for worker in workers:
            worker.stop()

async def clean_proxies():
    """Validate all proxies and keep only the working ones"""
    proxy_manager = ProxyManager()
    await proxy_manager.validate_proxies()
    logger.info("Proxy validation completed")
    
async def main():
    parser = argparse.ArgumentParser(description='Distributed Scraper')
    parser.add_argument('--mode', choices=['generate', 'process', 'clean_proxies'], required=True,
                      help='Mode to run: generate tasks, process tasks, or clean proxies')
    parser.add_argument('--workers', type=int, default=2,
                      help='Number of worker processes (only for process mode)')
    
    args = parser.parse_args()
    
    if args.mode == 'generate':
        await generate_tasks()
    elif args.mode == 'process':
        await process_tasks(args.workers)
    elif args.mode == 'clean_proxies':
        await clean_proxies()

if __name__ == "__main__":
    asyncio.run(main())
