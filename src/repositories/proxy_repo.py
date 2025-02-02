from typing import List
from src.models.proxy import ProxyCreate, ProxyUpdate, ProxyInDB
from .base import BaseRepository

class ProxyRepository(BaseRepository[ProxyInDB, ProxyCreate, ProxyUpdate]):
    def __init__(self):
        from src.storage.mongo_client import MongoClient
        self.mongo = MongoClient()
        super().__init__(self.mongo.db.proxies)
        self.model = ProxyInDB

    async def get_active_proxies(self) -> List[ProxyInDB]:
        """Get all active, non-blacklisted proxies"""
        return await self.find_many({
            "is_active": True,
            "blacklisted": False
        })

    async def setup_indexes(self):
        """Setup required indexes"""
        await self.collection.create_index([("url", 1)], unique=True)
        await self.collection.create_index([("is_active", 1), ("blacklisted", 1)])
        await self.collection.create_index([("last_checked", 1)])

    async def create(self, proxy: ProxyCreate) -> ProxyInDB:
        """Create a new proxy"""
        return await self.collection.insert_one(proxy.model_dump())