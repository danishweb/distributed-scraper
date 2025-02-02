from fastapi import FastAPI,HTTPException
from pydantic import BaseModel, Field
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.core.proxy_manager import ProxyManager
from src.tasks.generator import Generator

app = FastAPI()

class UrlInput(BaseModel):
    url: str
    priority: int = 1  

class TaskInput(BaseModel):
    urls: List[UrlInput]


@app.post("/tasks/generate")
async def generate_tasks(task_input: TaskInput):
    try:
        generator = Generator()
        for url in task_input.urls:
            await generator.add_url(url.url, url.priority)
        logger.info("Tasks generated successfully")
        return {"message": "Tasks generated successfully", "count": len(task_input.urls)}
    except Exception as e:
        logger.error(f"Error generating tasks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/proxies/clean")
async def clean_proxies():
    try:
        proxy_manger = ProxyManager()
        working_proxies = await proxy_manger.validate_proxies()
        logger.info("Proxy validation completed")
        return {"message": working_proxies.message, "working_proxies":  working_proxies.working_proxies}
    except Exception as e:
        logger.error(f"Error cleaning proxies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))