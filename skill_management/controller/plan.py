from fastapi import APIRouter, Depends, Body, Request

from skill_management.schemas.base import ErrorMessage
from skill_management.schemas.plan import PlanRequest, PlanResponse
from skill_management.utils.auth_manager import JWTBearer
from skill_management.utils.logger import get_logger

plan_router: APIRouter = APIRouter(tags=["plan"])
logger = get_logger()


@plan_router.post("/profile/plan",
                  response_model=PlanResponse,
                  status_code=201,
                  responses={
                      400: {
                          "model": ErrorMessage,
                          "description": "The plan is not created"
                      },
                      201: {
                          "description": "The plan is successfully created",
                      },
                  },
                  )
async def plan_create(request: Request,  # type: ignore
                      plan: PlanRequest = Body(...),
                      jwt_data: str = Depends(JWTBearer())):
    pass
