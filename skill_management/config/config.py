import os

import aioredis
from aioredis import Redis
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from skill_management.models.designation import Designations
from skill_management.models.enums import (PlanType, Status, UserStatus, FileType, SkillCategory, SkillType, \
                                           DesignationStatus, Gender, EnumInitializer)
from skill_management.models.file import Files
from skill_management.models.plan import Plans
from skill_management.models.profile import Profiles
from skill_management.models.skill import Skills
from skill_management.utils.initial_data import initialize_database


async def initiate_database() -> None:
    if os.getenv("ENVIRONMENT") == "local":
        client = AsyncIOMotorClient(os.getenv("LOCAL_DATABASE_URL"))
    else:
        client = AsyncIOMotorClient(os.getenv("DATABASE_URL"))
    await init_beanie(database=client.get_default_database(),
                      document_models=[EnumInitializer, PlanType, Status, UserStatus, FileType, SkillCategory,
                                       SkillType, DesignationStatus, Gender, Designations, Files, Profiles, Plans,
                                       Skills])  # type: ignore
    # , Files, Plans,
    # Profiles, Skills
    await initialize_database()


async def initiate_redis_pool() -> Redis:
    redis_connection = await aioredis.from_url(
        os.getenv("REDIS_AUTH_URL"),
        password=os.getenv("REDIS_PASSWORD"),
        encoding="utf-8",
        db=os.getenv("REDIS_USER_DB"),
        decode_responses=True,
    )
    return redis_connection
