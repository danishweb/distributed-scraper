import random
import aiohttp
from datetime import datetime
from typing import Any, Dict, List, Optional
from config.settings import HEADERS
from src.repositories.proxy_repo import ProxyRepository
from src.models.proxy import ProxyCreate

class ProxyManager:
    def __init__(self):
        self.repo = ProxyRepository()
    
    async def get_proxies(self) -> List[str]:
        """Get the list of all active proxies"""
        proxies = await self.repo.get_active_proxies()
        return [proxy.url for proxy in proxies]
    
    async def check_proxy(self, proxy_url: str) -> tuple[bool, float]:
        """Check if the proxy is working using aiohttp and return status and response time"""
        start_time = datetime.utcnow()
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(headers=HEADERS, timeout=timeout) as session:
                async with session.get(
                    "https://httpbin.org/ip",
                    proxy=proxy_url,
                    ssl=False
                ) as response:
                    is_working = response.status == 200
                    response_time = (datetime.utcnow() - start_time).total_seconds()
                    return is_working, response_time
        except:
            return False, 0.0

    async def validate_proxies(self) -> Dict[str, Any]:
        """Validate all proxies and update their status in the database"""
        proxies = await self.repo.find_many({})
        if not proxies:
            return {"message": "No proxies available in database", "working_proxies": 0}
            
        working_count = 0
        for proxy in proxies:
            is_working, response_time = await self.check_proxy(proxy.url)
            
            if is_working:
                await self.repo.record_success(proxy.id, response_time)
                working_count += 1
            else:
                await self.repo.increment_failures(proxy.id, "Failed connection check")
        
        return {
            "message": "Proxy validation completed",
            "working_proxies": working_count
        }

    async def migrate_from_file(self, file_path: str = "proxies.txt") -> Dict[str, Any]:
        """Migrate proxies from text file to MongoDB"""
        try:
            with open(file_path, 'r') as f:
                proxy_lines = f.readlines()

            proxies = [line.strip() for line in proxy_lines if line.strip()]
            success_count = 0
            error_count = 0
            
            for proxy_url in proxies:
                try:
                    if not proxy_url.startswith('http://'):
                        proxy_url = f'http://{proxy_url}'
                    
                    is_working, _ = await self.check_proxy(proxy_url)
                    if not is_working:
                        continue

                    proxy = ProxyCreate(
                        url=proxy_url,
                        is_active=True,
                        blacklisted=False,
                        failures=0,
                        last_checked=datetime.utcnow()
                    )
                    await self.repo.create(proxy)
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    continue
            
            return {
                "message": "Migration completed",
                "total_processed": len(proxies),
                "success_count": success_count,
                "error_count": error_count
            }
                
        except FileNotFoundError:
            return {
                "message": f"Error: File {file_path} not found",
                "total_processed": 0,
                "success_count": 0,
                "error_count": 0
            }
        except Exception as e:
            return {
                "message": f"Error during migration: {str(e)}",
                "total_processed": 0,
                "success_count": 0,
                "error_count": 0
            }