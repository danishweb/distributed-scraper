import os
import sys
import asyncio
import argparse
import uuid
import textwrap
import uvicorn

__version__ = "1.0.0"

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

def create_parser():
    """Create the command line parser"""
    parser = argparse.ArgumentParser(
        description=textwrap.dedent('''
            Distributed Scraper - A tool for distributed web scraping
            
            Example usage:
              %(prog)s generate                     # Generate sample scraping tasks
              %(prog)s process --workers 4          # Process tasks with 4 workers
              %(prog)s clean-proxies               # Validate and clean proxy list
        '''),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate sample scraping tasks')
    generate_parser.add_argument('--urls-file', type=str, help='Path to file containing URLs to scrape')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process scraping tasks')
    process_parser.add_argument('--workers', type=int, default=2,
                             help='Number of worker processes (default: 2)')
    process_parser.add_argument('--timeout', type=int, default=3600,
                             help='Timeout in seconds for the entire process (default: 3600)')
    
    # Clean proxies command
    clean_parser = subparsers.add_parser('clean-proxies', help='Validate and clean proxy list')
    clean_parser.add_argument('--timeout', type=int, default=10,
                           help='Timeout in seconds for each proxy check (default: 10)')
    
    # Add API server command
    api_parser = subparsers.add_parser('serve', help='Start the FastAPI server')
    api_parser.add_argument('--host', type=str, default="localhost",
                          help='Host to bind the server to (default: localhost)')
    api_parser.add_argument('--port', type=int, default=8000,
                          help='Port to bind the server to (default: 8000)')
    return parser

async def main():
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'generate':
            await generate_tasks()
        elif args.command == 'process':
            await process_tasks(args.workers)
        elif args.command == 'clean-proxies':
            await clean_proxies()
        elif args.command == 'serve':
            uvicorn.run("api:app", host=args.host, port=args.port, reload=True)
    
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
