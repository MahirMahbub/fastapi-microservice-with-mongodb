import os

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

# async def init_redis_pool() -> redis.Redis:
#     redis_c = await redis.from_url(
#         global_settings.redis_url,
#         encoding="utf-8",
#         db=global_settings.redis_db,
#         decode_responses=True,
#     )
#     return redis_c