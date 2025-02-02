from typing import Generic, TypeVar, Optional, List, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def find_one(self, id: str) -> Optional[ModelType]:
        doc = await self.collection.find_one({"_id": ObjectId(id)})
        return self.model(**doc) if doc else None

    async def find_many(self, filter_dict: Dict = None) -> List[ModelType]:
        cursor = self.collection.find(filter_dict or {})
        return [self.model(**doc) async for doc in cursor]