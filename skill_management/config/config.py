import os

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient



async def initiate_database() -> None:
    if os.getenv("ENVIRONMENT") == "local":
        client = AsyncIOMotorClient(os.getenv("LOCAL_DATABASE_URL"))
    else:
        client = AsyncIOMotorClient(os.getenv("DATABASE_URL"))
    await init_beanie(database=client.get_default_database(),
                      document_models=[])
