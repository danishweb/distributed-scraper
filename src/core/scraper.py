import aiohttp
from bs4 import BeautifulSoup

async def scrape_product(url: str, headers: dict, timeout: int, proxy: str = None) -> dict:
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(
            url, 
            timeout=timeout,
            proxy=proxy
        ) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "lxml")
            
        return {
            "title": soup.select_one("#productTitle").text.strip() if soup.select_one("#productTitle") else "Title not found",
        }