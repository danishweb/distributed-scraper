import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Scraping Configuration
USER_AGENT = os.getenv('USER_AGENT')
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))

# Proxy Settings
try:
    PROXY_URLS = open('proxies.txt', 'r').read().splitlines()
except (FileNotFoundError, IOError):
    PROXY_URLS = []

# HTTP Headers
HEADERS = {
    'User-Agent': USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive'
}