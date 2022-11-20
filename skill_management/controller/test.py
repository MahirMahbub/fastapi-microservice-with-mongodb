from fastapi import APIRouter, Depends

from skill_management.utils.auth_manager import JWTBearer
from skill_management.utils.logger import get_logger

test_router: APIRouter = APIRouter()
logger = get_logger()


@test_router.get("/hello/{name}", dependencies=[Depends(JWTBearer())])
def say_hello(name: str) -> dict[str, str]:
    logger.info("Testing Route")
    return {"message": f"Hello {name}"}
