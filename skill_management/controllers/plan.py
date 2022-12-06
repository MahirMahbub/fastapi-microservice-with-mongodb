from fastapi import APIRouter, Depends, Body, Request
from fastapi.responses import ORJSONResponse

from skill_management.schemas.base import ErrorMessage
from skill_management.schemas.plan import PlanCreateRequest, PlanCreateResponse
from skill_management.services.plan import PlanService
from skill_management.utils.auth_manager import JWTBearer
from skill_management.utils.logger import get_logger
from skill_management.utils.profile_manager import get_profile_email

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
async def create_plan_by_user(request: Request,  # type: ignore
                              plan: PlanCreateRequest = Body(..., examples={
                                  "CREATE": {
                                      "summary": "Create Body",
                                      "description": "a example of body for create operation",
                                      "value": {
                                          "plan_type": 1,
                                          "notes": "It is a note for the planning",
                                          "skill_id": 1,
                                          "status": 1,
                                          "start_date": "2022-11-24T11:59:28.549417+00:00",
                                          "end_date": "2022-11-25T11:59:28.549421+00:00",
                                          "task": [
                                              {
                                                  "description": "It is a task for the planning",
                                                  "status": 1
                                              }
                                          ]
                                      },
                                  },

                                  "UPDATE":
                                      {
                                          "summary": "Update Body",
                                          "description": "a example of body for update operation",
                                          "value":
                                              {
                                                  "plan_id": "954eba99-b1ec-4c1f-b5b1-3cc9db9e59e0",
                                                  "plan_type": 1,
                                                  "notes": "It is a note for the planning",
                                                  "skill_id": 1,
                                                  "start_date": "2022-11-24T11:59:28.549417+00:00",
                                                  "end_date": "2022-11-25T11:59:28.549421+00:00",
                                                  "delete_tasks": [2],
                                                  "status": 1,
                                                  "task": [
                                                      {
                                                          "task_id": 1,
                                                          "description": "It is a task for the planning",
                                                          "status": 2
                                                      }
                                                  ]
                                              }
                                      }

                              }, ),
                              service: PlanService = Depends(),
                              user_id: str = Depends(JWTBearer())):
    """
    **Create:** must provide *"skill_id"*, *"start_date"*, *"end_date"*, *"plan_type"* for creating a plan.
    
    **Update:** must provide *"plan_id"* for plan update and *"task_id"* for task update. Others are optional.
    """
    email = await get_profile_email(user_id=user_id, request=request)
    return await service.create_or_update_plan_by_user(plan_request=plan, email=email)
