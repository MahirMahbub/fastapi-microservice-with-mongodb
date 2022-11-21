from fastapi import APIRouter, Request, Body, Depends

from skill_management.schemas.base import Message
from skill_management.schemas.skill import SkillDataResponse, SkillDataRequest
from skill_management.utils.auth_manager import JWTBearer
from skill_management.utils.logger import get_logger

skill_router: APIRouter = APIRouter(tags=["skill"])
logger = get_logger()


@skill_router.post("/profile/skill",
                   response_model=SkillDataResponse,
                   status_code=201,
                   responses={
                       400: {
                           "model": Message,
                           "description": "The skill is not created"
                       },
                       201: {
                           "description": "The skill was successfully created",
                       },
                   },
                   )
async def skill_create(request: Request, skill: SkillDataRequest = Body(...),
                       jwt_data: str = Depends(JWTBearer())):  # type: ignore
    pass
