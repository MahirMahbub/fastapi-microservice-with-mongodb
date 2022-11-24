from fastapi import APIRouter, Request, Body, Depends, UploadFile, File, Path, Query
from fastapi.responses import ORJSONResponse

from skill_management.enums import SkillCategoryEnum
from skill_management.schemas.base import ErrorMessage
from skill_management.schemas.file import SkillCertificateResponse
from skill_management.schemas.skill import CreateSkillDataResponse, CreateSkillDataRequest, GetSkillDataResponse, \
    GetSkillDataResponseList
from skill_management.utils.auth_manager import JWTBearer
from skill_management.utils.logger import get_logger

skill_router: APIRouter = APIRouter(tags=["skill"])
logger = get_logger()


@skill_router.post("/profile/skills",
                   response_class=ORJSONResponse,
                   response_model=CreateSkillDataResponse,
                   status_code=201,
                   responses={
                       400: {
                           "model": ErrorMessage,
                           "description": "The skill is not created"
                       },
                       201: {
                           "description": "The skill is successfully created",
                       },
                   })
async def create_skill(request: Request,  # type: ignore
                       skill: CreateSkillDataRequest = Body(..., examples={
                           "CREATE": {
                               "summary": "Create Body",
                               "description": "a example of body for create operation",
                               "value": {
                                   "skill_id": 1,
                                   "experience_year": 4,
                                   "number_of_projects": 4,
                                   "level": 5,
                                   "training_duration": 2,
                                   "achievements": "1",
                                   "achievements_description": "It is the achievement's description",
                                   "certificate": "1",
                               },
                           },

                           "UPDATE":
                               {
                                   "summary": "Update Body",
                                   "description": "a example of body for update operation",
                                   "value":
                                       {
                                           "skill_id": 1,
                                           "experience_year": 4, # Optional
                                           "number_of_projects": 4,
                                           "level": 5,
                                           "training_duration": 2,
                                           "achievements": "1",
                                           "achievements_description": "It is the achievement's description",
                                           "certificate": "1",
                                           "status": 2
                                       },
                               }

                       },
                                                            description="provide all required attributes to "
                                                                        "create a new skill"),
                       user_id: str = Depends(JWTBearer())):
    """
    **Create:** Must provide all the data necessary including *"skill_id"* for creating a new skill. *"status"* is optional.


    **Update:** For update purposes provide *"skill_id"*. Other attributes are optional.
    """
    pass


@skill_router.post("/profile/skills/upload-certificate",
                   response_class=ORJSONResponse,
                   response_model=SkillCertificateResponse,
                   status_code=201,
                   responses={
                       400: {
                           "model": ErrorMessage,
                           "description": "The certificates are not uploaded"
                       },
                       201: {
                           "description": "The certificates are successfully uploaded",
                       },
                   })
async def upload_certificate(request: Request,  # type: ignore
                             files: list[UploadFile] = File(None, description="select certificate files to upload"),
                             user_id: str = Depends(JWTBearer())):
    pass


@skill_router.get("/skills/{skill-id}",
                  response_class=ORJSONResponse,
                  response_model=GetSkillDataResponse,
                  status_code=200,
                  responses={
                      404: {
                          "model": ErrorMessage,
                          "description": "The skill details is not available"
                      },
                      200: {
                          "description": "The skill requested by id",
                      },
                  })
async def get_skill(request: Request,  # type: ignore
                    skill_id: int = Path(..., description="provide skill id to get skill information",
                                         alias="skill-id"),
                    user_id: str = Depends(JWTBearer())):
    pass


@skill_router.get("/skills",
                  response_class=ORJSONResponse,
                  response_model=GetSkillDataResponseList,
                  status_code=200,
                  responses={
                      404: {
                          "model": ErrorMessage,
                          "description": "The skill list is not available"
                      },
                      200: {
                          "description": "The skill list requested",
                      },
                  }
                  )
async def get_skill_list(request: Request,  # type: ignore
                         skill_category: SkillCategoryEnum | None = Query(default=None,
                                                                          alias="skill-category",
                                                                          description="""input skill category as string
                                                                          
    frontend: 1, backend: 2, devops: 3, qa: 4, database: 5, network: 6, fullstack: 7"""),
                         skill_name: str | None = Query(default=None, description="input skill name as string",
                                                        alias="skill-name"),
                         user_id: str = Depends(JWTBearer())):
    pass
