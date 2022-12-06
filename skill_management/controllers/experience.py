import uuid

from fastapi import APIRouter, Request, Depends, Body
from fastapi.responses import ORJSONResponse

from skill_management.schemas.base import ErrorMessage
from skill_management.schemas.experience import ExperienceCreateRequest, ExperienceListDataResponse, \
    ExperienceCreateAdminRequest
from skill_management.services.experience import ExperienceService
from skill_management.utils.auth_manager import JWTBearer, JWTBearerAdmin
from skill_management.utils.logger import get_logger
from skill_management.utils.profile_manager import get_profile_email

experience_router: APIRouter = APIRouter(tags=["experience"])
logger = get_logger()


@experience_router.post("/profile/experiences",
                        response_class=ORJSONResponse,
                        response_model=ExperienceListDataResponse,
                        status_code=201,
                        responses={
                            400: {
                                "model": ErrorMessage,
                                "description": "The experience is not created"
                            },
                            201: {
                                "description": "The experience is successfully created",
                            },
                        },
                        )
async def create_experience_by_user(request: Request,  # type: ignore
                                    experience_request: ExperienceCreateRequest = Body(..., examples={
                                        "CREATE": {
                                            "summary": "Create Body",
                                            "description": "a example of body for create operation",
                                            "value": {
                                                "company_name": "X Software",
                                                "job_responsibility": "Backend Development",
                                                "designation": "Software Engineer",
                                                "start_date": "2021-07-12T11:55:30.858969+00:00",
                                                "end_date": "2022-05-08T11:55:30.858980+00:00",
                                            },
                                        },

                                        "UPDATE":
                                            {
                                                "summary": "Update Body",
                                                "description": "a example of body for update operation",
                                                "value":
                                                    {
                                                        "experience_id": 1,
                                                        "company_name": "X Software",
                                                        "job_responsibility": "Backend Development",
                                                        "designation": "Software Engineer",
                                                        "start_date": "2021-07-12T11:55:30.858969+00:00",
                                                        "end_date": "2022-05-08T11:55:30.858980+00:00",
                                                        "status": 2
                                                    },
                                            }

                                    }, description="input experience data"),
                                    user_id: str = Depends(JWTBearer()),
                                    service: ExperienceService = Depends()):
    """
    **Create:** Must provide all the data except *"experience_id"*. *"status"* is optional.


    **Update:** Must provide *"experience_id"*. Other attributes are optional.
    """
    email = await get_profile_email(user_id=user_id, request=request)
    return await service.create_or_update_experience_by_user(experience_request=experience_request,
                                                             email=email)


@experience_router.post("/admin/profile/experiences",
                        response_class=ORJSONResponse,
                        response_model=ExperienceListDataResponse,
                        status_code=201,
                        responses={
                            400: {
                                "model": ErrorMessage,
                                "description": "The experience is not created"
                            },
                            201: {
                                "description": "The experience is successfully created",
                            },
                        },
                        )
async def create_experience_by_admin(request: Request,  # type: ignore
                                    experience_request: ExperienceCreateAdminRequest = Body(..., examples={
                                        "CREATE": {
                                            "summary": "Create Body",
                                            "description": "a example of body for create operation",
                                            "value": {
                                                "profile_id": uuid.uuid4(),
                                                "company_name": "X Software",
                                                "job_responsibility": "Backend Development",
                                                "designation": "Software Engineer",
                                                "start_date": "2021-07-12T11:55:30.858969+00:00",
                                                "end_date": "2022-05-08T11:55:30.858980+00:00",
                                            },
                                        },

                                        "UPDATE":
                                            {
                                                "summary": "Update Body",
                                                "description": "a example of body for update operation",
                                                "value":
                                                    {
                                                        "experience_id": 1,
                                                        "profile_id": uuid.uuid4(),
                                                        "company_name": "X Software",
                                                        "job_responsibility": "Backend Development",
                                                        "designation": "Software Engineer",
                                                        "start_date": "2021-07-12T11:55:30.858969+00:00",
                                                        "end_date": "2022-05-08T11:55:30.858980+00:00",
                                                        "status": 2
                                                    },
                                            }

                                    }, description="input experience data"),
                                    admin_user_id: str = Depends(JWTBearerAdmin()),
                                    service: ExperienceService = Depends()):
    """
    **Create:** Must provide all the data except *"experience_id"*. *"status"* is optional.


    **Update:** Must provide *"experience_id"*. Other attributes are optional.
    """
    return await service.create_or_update_experience_by_admin(experience_request=experience_request)
