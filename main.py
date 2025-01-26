import os
import sys
import asyncio

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from config.settings import HEADERS, REQUEST_TIMEOUT, PROXY_CONFIG
from src.core.scraper import scrape_product

async def main():
    url = "https://www.amazon.com/dp/B0B8Q9FGMD?_encoding=UTF8&psc=1&ref_=cm_sw_r_cp_ud_dp_82ANBZWC3ED5T32G6G9A_1&newOGT=1"
    result = await scrape_product(url, HEADERS, REQUEST_TIMEOUT, PROXY_CONFIG['proxy'])
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
