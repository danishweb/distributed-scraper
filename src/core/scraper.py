import aiohttp
from bs4 import BeautifulSoup
from aiohttp import ClientTimeout
from typing import Optional, Dict, Any

async def scrape_product(url: str, headers: dict, timeout: int, proxy: Optional[str] = None) -> Dict[str, Any]:
    timeout_obj = ClientTimeout(total=timeout)
    
    # Configure proxy with proper format
    proxy_auth = None
    if proxy:
        # Check if proxy has authentication
        if '@' in proxy:
            auth_part = proxy.split('@')[0].replace('http://', '')
            proxy_auth = aiohttp.BasicAuth(
                login=auth_part.split(':')[0],
                password=auth_part.split(':')[1]
            )
    
    try:
        async with aiohttp.ClientSession(headers=headers, timeout=timeout_obj) as session:
            async with session.get(
                url,
                proxy=proxy,
                proxy_auth=proxy_auth,
                ssl=False  
            ) as response:
                if response.status == 403:
                    raise Exception(f"{response.status}, message='Forbidden', url='{proxy}'")
                elif response.status != 200:
                    raise Exception(f"HTTP {response.status}: {response.reason}")
                
                html = await response.text()
                soup = BeautifulSoup(html, "lxml")
                
                return {
                    "title": soup.select_one("#productTitle").text.strip() if soup.select_one("#productTitle") else "Title not found",
                }
                
    except aiohttp.ClientError as e:
        raise Exception(f"Connection error with proxy {proxy}: {str(e)}")
    except Exception as e:
        raise Exception(f"Error scraping with proxy {proxy}: {str(e)}")