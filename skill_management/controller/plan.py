from fastapi import APIRouter, Depends, Body, Request
from fastapi.responses import ORJSONResponse

from skill_management.schemas.base import ErrorMessage
from skill_management.schemas.plan import PlanCreateRequest, PlanCreateResponse
from skill_management.utils.auth_manager import JWTBearer
from skill_management.utils.logger import get_logger

plan_router: APIRouter = APIRouter(tags=["plan"])
logger = get_logger()


@plan_router.post("/profile/plans",
                  response_class=ORJSONResponse,
                  response_model=PlanCreateResponse,
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
async def create_plan(request: Request,  # type: ignore
                      plan: PlanCreateRequest = Body(...),
                      user_id: str = Depends(JWTBearer())):
    """
    **Create:** must provide skill_id, start_date, end_date, plan_type for creating a plan
    **Update:** must plan_id. Others are optional
    """
    pass
