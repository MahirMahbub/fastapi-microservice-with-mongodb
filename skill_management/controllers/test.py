import os

import aioredis
from fastapi import APIRouter, Depends, Request

# from skill_management.models.plan import Plan
from skill_management.utils.auth_manager import JWTBearer
from skill_management.utils.logger import get_logger

test_router: APIRouter = APIRouter()
logger = get_logger()


# @test_router.get("/hello/{name}")
# async def say_hello(request: Request, name: str):
#     # plan = Plan(skill_id=1)
#     # await plan.insert()
#     # logger.info("Testing Route")
#     # return {"message": f"Hello {name}", "plan": plan.id}
#     # redis = await aioredis.from_url(
#     #     os.getenv("REDIS_AUTH_URL"),
#     #     password=os.getenv("REDIS_PASSWORD"),
#     #     encoding="utf-8",
#     #     db=os.getenv("REDIS_USER_DB"),
#     #     decode_responses=True,
#     # )
#     await request.app.state.redis_connection.set("my-key", "value")
#     val = await request.app.state.redis_connection.get("my-key")
#     print(val)
#     return val
