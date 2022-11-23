from fastapi import APIRouter, Request, Depends, Body
from fastapi.responses import ORJSONResponse

from skill_management.schemas.base import ErrorMessage
from skill_management.schemas.education import EducationCreateRequest, EducationCreateResponse
from skill_management.utils.auth_manager import JWTBearer
from skill_management.utils.logger import get_logger

education_router: APIRouter = APIRouter(tags=["education"])
logger = get_logger()


@education_router.post("/profile/educations",
                       response_class=ORJSONResponse,
                       response_model=EducationCreateResponse,
                       status_code=201,
                       responses={
                            400: {
                                "model": ErrorMessage,
                                "description": "The education is not created"
                            },
                            201: {
                                "description": "The education is successfully created",
                            },
                        },
                       )
async def create_education(request: Request,  # type: ignore
                           education: EducationCreateRequest = Body(..., description="input education data"),
                           user_id: str = Depends(JWTBearer())):
    pass
