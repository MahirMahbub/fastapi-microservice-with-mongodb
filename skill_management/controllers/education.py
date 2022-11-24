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
                           education: EducationCreateRequest = Body(
                               examples={
                                   "CREATE": {
                                       "summary": "Create Body",
                                       "description": "a example of body for create operation",
                                       "value":
                                           {
                                               "degree_name": "B.Sc in Computer Science",
                                               "school_name": "University of Dhaka",
                                               "passing_year": "2019",
                                               "grade": 3.80
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
                           user_id: str = Depends(JWTBearer())):
    """
    **Create:** Must provide all the data except *"education_id"*. *"status"* is optional.
    
    
    **Update:** Must provide *"education_id"*. Other attributes are optional.
    """


pass
