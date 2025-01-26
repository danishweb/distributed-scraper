import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Scraping Configuration
USER_AGENT = os.getenv('USER_AGENT')
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))

# Proxy Settings
USE_PROXY = os.getenv('USE_PROXY', 'false').lower() == 'true'
PROXY_URL = os.getenv('PROXY_URL')

# HTTP Headers
HEADERS = {
    'User-Agent': USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}

# Proxy configuration for aiohttp
PROXY_CONFIG = {
    'proxy': PROXY_URL if USE_PROXY else None
}