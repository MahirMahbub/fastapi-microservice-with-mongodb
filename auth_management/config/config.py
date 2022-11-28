import os

import aioredis
from aioredis import Redis
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from auth_management.entities.user import User


# class Settings(BaseSettings):
#     DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
#     LOCAL_DATABASE_URL: Optional[str] = os.getenv("LOCAL_DATABASE_URL")
#     VERIFY_TOKEN_SECRET_KEY: str = os.getenv("VERIFY_TOKEN_SECRET_KEY")
#     RESET_PASSWORD_TOKEN_SECRET_KEY: str = os.getenv("RESET_PASSWORD_TOKEN_SECRET_KEY")
#     ENCRYPTION_ALGORITHM: str = os.getenv("ENCRYPTION_ALGORITHM")
#     FRONT_END_URL: str = os.getenv("FRONT_END_URL")
#     SENDER_EMAIL: str = os.getenv("SENDER_EMAIL")
#     SENDER_PASSWORD: str = os.getenv("SENDER_PASSWORD")
#     GMAIL_PORT: int = os.getenv("GMAIL_PORT")
#     SMTP_SERVER: str = os.getenv("SMTP_SERVER")
#     TLS: int = os.getenv("TLS")
#
#     class Config:
#         env_file = ".env"
#         orm_mode = True


async def initiate_database() -> None:
    if os.getenv("ENVIRONMENT") == "local":
        client = AsyncIOMotorClient(os.getenv("LOCAL_DATABASE_URL"))
    else:
        client = AsyncIOMotorClient(os.getenv("DATABASE_URL"))
    await init_beanie(database=client.auth,
                      document_models=[User])


async def initiate_redis_pool() -> Redis:
    redis_connection = await aioredis.from_url(
        os.getenv("REDIS_AUTH_URL"),
        password=os.getenv("REDIS_PASSWORD"),
        encoding="utf-8",
        db=os.getenv("REDIS_USER_DB"),
        decode_responses=True,
    )
    return redis_connection
