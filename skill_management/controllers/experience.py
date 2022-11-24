from fastapi import APIRouter, Request, Depends, Body
from fastapi.responses import ORJSONResponse

from skill_management.schemas.base import ErrorMessage
from skill_management.schemas.experience import ExperienceCreateRequest, ExperienceCreateResponse
from skill_management.utils.auth_manager import JWTBearer
from skill_management.utils.logger import get_logger

experience_router: APIRouter = APIRouter(tags=["experience"])
logger = get_logger()


@experience_router.post("/profile/experiences",
                        response_class=ORJSONResponse,
                        response_model=ExperienceCreateResponse,
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
async def create_experience(request: Request,  # type: ignore
                            experience: ExperienceCreateRequest = Body(..., examples={
                                "CREATE": {
                                    "summary": "Create Body",
                                    "description": "a example of body for create operation",
                                    "value": {
                                        "company_name": "X Software",
                                        "job_responsibility": "Backend Development",
                                        "designation_id": 2,
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
                                                "designation_id": 2,
                                                "start_date": "2021-07-12T11:55:30.858969+00:00",
                                                "end_date": "2022-05-08T11:55:30.858980+00:00",
                                                "status": 2
                                            },
                                    }

                            }, description="input experience data"),
                            user_id: str = Depends(JWTBearer())):
    """
    **Create:** Must provide all the data except experience id [status is optional]


    **Update:** Must provide experience id. Other attributes are optional.
    """
    pass
