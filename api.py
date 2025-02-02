from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
import logging
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.core.proxy_manager import ProxyManager
from src.storage.mongo_client import MongoClient

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for database initialization"""
    logger.info("Initializing database...")
    mongo_client = MongoClient()
    await mongo_client.init_db()
    logger.info("Database initialized successfully")
    
    yield
    
    logger.info("Shutting down...")

app = FastAPI(lifespan=lifespan)

@app.post("/proxies/migrate")
async def migrate_proxies():
    """Migrate proxies from text file to MongoDB"""
    try:
        proxy_manager = ProxyManager()
        result = await proxy_manager.migrate_from_file()
        logger.info(f"Proxy migration completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Error migrating proxies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/proxies/clean")
async def clean_proxies():
    """Validate and clean proxies"""
    try:
        proxy_manager = ProxyManager()
        result = await proxy_manager.validate_proxies()
        logger.info("Proxy validation completed")
        return result
    except Exception as e:
        logger.error(f"Error cleaning proxies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/proxies")
async def get_proxies():
    """Get all active proxies"""
    try:
        proxy_manager = ProxyManager()
        proxies = await proxy_manager.get_proxies()
        return {"proxies": proxies}
    except Exception as e:
        logger.error(f"Error fetching proxies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))