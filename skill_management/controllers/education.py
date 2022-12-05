import uuid

from fastapi import APIRouter, Request, Depends, Body
from fastapi.responses import ORJSONResponse

from skill_management.schemas.base import ErrorMessage
from skill_management.schemas.education import EducationCreateRequest, EducationListDataResponse, \
    EducationCreateAdminRequest
from skill_management.services.education import EducationService
from skill_management.utils.auth_manager import JWTBearer, JWTBearerAdmin
from skill_management.utils.logger import get_logger
from skill_management.utils.profile_manager import get_profile_email

education_router: APIRouter = APIRouter(tags=["education"])
logger = get_logger()


@education_router.post("/profile/educations",
                       response_class=ORJSONResponse,
                       response_model=EducationListDataResponse,
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
async def create_education_by_user(request: Request,  # type: ignore
                                   education_request: EducationCreateRequest = Body(
                                       examples={
                                           "CREATE": {
                                               "summary": "Create Body",
                                               "description": "a example of body for create operation",
                                               "value":
                                                   {
                                                       "degree_name": "B.Sc in Computer Science",
                                                       "school_name": "University of Dhaka",
                                                       "passing_year": "2019",
                                                       "grade": 3.80,
                                                       "status": 1
                                                   }
                                           },

                                           "UPDATE":
                                               {
                                                   "summary": "Update Body",
                                                   "description": "a example of body for update operation",
                                                   "value":
                                                       {
                                                           "education_id": 1,
                                                           "degree_name": "B.Sc in Computer Science",
                                                           "school_name": "University of Dhaka",
                                                           "passing_year": "2019",
                                                           "grade": 3.80,
                                                           "status": 1
                                                       },
                                               }

                                       },

                                       description="input education data"),
                                   user_id: str = Depends(JWTBearer()),
                                   service: EducationService = Depends()):
    """
    **Create:** Must provide all the data except *"education_id"*. *"status"* is optional.
    
    
    **Update:** Must provide *"education_id"*. Other attributes are optional.
    """

    email = await get_profile_email(user_id=user_id, request=request)
    return await service.create_or_update_education_by_user(education_request=education_request,
                                                            email=email)


@education_router.post("/admin/profile/educations",
                       response_class=ORJSONResponse,
                       response_model=EducationListDataResponse,
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
async def create_education_by_admin(request: Request,  # type: ignore
                                    education_request: EducationCreateAdminRequest = Body(
                                       examples={
                                           "CREATE": {
                                               "summary": "Create Body",
                                               "description": "a example of body for create operation",
                                               "value":
                                                   {
                                                       "profile_id": uuid.uuid4(),
                                                       "degree_name": "B.Sc in Computer Science",
                                                       "school_name": "University of Dhaka",
                                                       "passing_year": "2019",
                                                       "grade": 3.80,
                                                       "status": 1
                                                   }
                                           },

                                           "UPDATE":
                                               {
                                                   "summary": "Update Body",
                                                   "description": "a example of body for update operation",
                                                   "value":
                                                       {
                                                           "profile_id": uuid.uuid4(),
                                                           "education_id": 1,
                                                           "degree_name": "B.Sc in Computer Science",
                                                           "school_name": "University of Dhaka",
                                                           "passing_year": "2019",
                                                           "grade": 3.80,
                                                           "status": 1
                                                       },
                                               }

                                       },

                                       description="input education data"),
                                    user_id: str = Depends(JWTBearerAdmin()),
                                    service: EducationService = Depends()):
    """
    **Create:** Must provide all the data except *"education_id"*. *"status"* is optional.


    **Update:** Must provide *"education_id"*. Other attributes are optional.
    """

    email = await get_profile_email(user_id=user_id, request=request)
    return await service.create_or_update_education_by_admin(education_request=education_request)
