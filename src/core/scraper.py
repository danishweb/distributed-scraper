from typing import Optional
from aiohttp import ClientTimeout, ClientSession

class AsyncScraper:
    def __init__(self):
        self.session = ClientSession(headers={
            "User-Agent": 
                "Mozilla/5.0 (EthicalScraper/1.0)"
            },
            timeout=ClientTimeout(total=10)
        )
        pass

    async def fetch(self, url:str) -> Optional[str]:
        pass

