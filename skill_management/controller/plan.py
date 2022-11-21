from fastapi import APIRouter, Depends, Body, Request

from skill_management import schemas
from skill_management.schemas.base import Message
from skill_management.schemas.plan import PlanCreate, PlanResponse
from skill_management.utils.auth_manager import JWTBearer
from skill_management.utils.logger import get_logger

plan_router: APIRouter = APIRouter(tags=["plan"])
logger = get_logger()


@plan_router.post("/profile/plan",
                  response_model=PlanResponse,
                  status_code=201,
                  responses={
                      400: {
                          "model": Message,
                          "description": "The plan is not created"
                      },
                      201: {
                          "description": "The plan was successfully created",
                      },
                  },
                  )
async def plan_create(request: Request, plan: PlanCreate=Body(...), jwt_data: str = Depends(JWTBearer())):  # type: ignore
    pass
