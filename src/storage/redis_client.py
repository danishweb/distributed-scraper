from redis.asyncio import Redis
import json

class RedisClient:
    def __init__(self, host='localhost', port=6379, decode_responses=True):
        self.redisClient = Redis(host=host, port=port, decode_responses=decode_responses)
        self.task_queue = "scraper:tasks"
    

    async def add_task(self, url:str, priority:int):
        try:
            existing_tasks = await self.redisClient.lrange(self.task_queue, 0, -1)
            for task in existing_tasks:
                task_data = json.loads(task)
                if task_data["url"] == url:
                    return False
            task = json.dumps({
                "url": url,
                "priority": priority,
                "retires": 0
            })
            await self.redisClient.lpush(self.task_queue, task)
            return True
        except Exception as e:
            print(f"Error adding task: {e}")
            return False

    async def get_task(self):
        try:
            tasks = await self.redisClient.lrange(self.task_queue, 0, -1)
            if tasks:
                tasks = [json.loads(task) for task in tasks]
                task = max(tasks, key=lambda x: x["priority"])
                return task
            return None
        except Exception as e:
            print(f"Error getting task: {e}")
            return None

    async def remove_task(self, obj=None, url=None):
        try:
            if obj:
                await self.redisClient.lrem(self.task_queue, 0, json.dumps(obj))
            elif url:
                tasks = await self.redisClient.lrange(self.task_queue, 0, -1)
                for task in tasks:
                    task_data = json.loads(task)
                    if task_data["url"] == url:
                        await self.redisClient.lrem(self.task_queue, 0, task)
                        break
        except Exception as e:
            print(f"Error removing task: {e}")