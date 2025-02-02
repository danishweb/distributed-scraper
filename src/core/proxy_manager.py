import random
import aiohttp
import asyncio
from typing import List, Optional
from config.settings import PROXY_URLS, HEADERS

class ProxyManager:
    def __init__(self):
        self.proxies: List[str] = []
        self.working_proxies: List[str] = []
        self.proxies = [f"http://{url}" for url in PROXY_URLS if url.strip()]
    
    def get_proxies(self) -> List[str]:
        """Get the list of working proxies"""
        return self.working_proxies if self.working_proxies else self.proxies
    
    def get_proxy(self) -> Optional[str]:
        """Get a random proxy from the list of working proxies"""
        proxy_list = self.get_proxies()
        if not proxy_list:
            return None
        return random.choice(proxy_list)
    
    async def check_proxy(self, proxy: str) -> bool:
        """Check if the proxy is working using aiohttp"""
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(headers=HEADERS, timeout=timeout) as session:
                async with session.get(
                    "https://httpbin.org/ip",
                    proxy=proxy,
                    ssl=False
                ) as response:
                    return response.status == 200
        except:
            return False
    
    async def update_proxy_file(self, proxies: List[str]):
        """Update the proxies.txt file with working proxies"""
        # Convert http://proxy:port back to proxy:port format
        cleaned_proxies = [proxy.replace('http://', '') for proxy in proxies]
        
        try:
            with open("proxies.txt", "w") as f:  # Use 'w' to overwrite with only working proxies
                for proxy in cleaned_proxies:
                    f.write(f"{proxy}\n")
            print(f"Updated proxies.txt with {len(cleaned_proxies)} working proxies")
        except Exception as e:
            print(f"Error updating proxy file: {e}")

    async def validate_proxies(self):
        """Validate all proxies and keep only the working ones"""
        if not self.proxies:
            print("No proxies available in proxies.txt")
            return
            
        tasks = [self.check_proxy(proxy) for proxy in self.proxies]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        self.working_proxies = [
            proxy for proxy, is_working in zip(self.proxies, results)
            if isinstance(is_working, bool) and is_working
        ]
        
        if not self.working_proxies:
            print("Warning: No working proxies found!")
        else:
            await self.update_proxy_file(self.working_proxies)
            print(f"Found {len(self.working_proxies)} working proxies")