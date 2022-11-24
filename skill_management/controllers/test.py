from fastapi import APIRouter, Depends

# from skill_management.models.plan import Plan
from skill_management.utils.auth_manager import JWTBearer
from skill_management.utils.logger import get_logger

test_router: APIRouter = APIRouter()
logger = get_logger()


@test_router.get("/hello/{name}")
async def say_hello(name: str) -> dict[str, str]:
    # plan = Plan(skill_id=1)
    # await plan.insert()
    # logger.info("Testing Route")
    # return {"message": f"Hello {name}", "plan": plan.id}
    pass
