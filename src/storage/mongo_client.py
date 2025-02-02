from motor.motor_asyncio import AsyncIOMotorClient
from src.utils.patterns.singleton import SingletonMeta

class MongoClient(metaclass=SingletonMeta):
    def __init__(self, host='localhost', port=27017):
        if not hasattr(self, 'client'):
            self.client = AsyncIOMotorClient(host=host, port=port)
            self.db = self.client['scraper']

    async def init_db(self):
        """Initialize database with required indexes"""
        from src.repositories.proxy_repo import ProxyRepository
        
        # Initialize repositories
        proxy_repo = ProxyRepository()
        
        # Setup indexes for each collection
        await proxy_repo.setup_indexes()
        
        # Add other repository index setup here as needed