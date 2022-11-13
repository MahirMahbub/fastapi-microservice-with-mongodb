import logging
import os
from typing import Optional

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseSettings

from auth_app.entities.user import User


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


async def initiate_database():
    client = AsyncIOMotorClient(os.getenv("DATABASE_URL"))
    await init_beanie(database=client.get_default_database(),
                      document_models=[User])
