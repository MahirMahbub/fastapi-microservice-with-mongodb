import uuid
from typing import cast

from beanie import PydanticObjectId
from fastapi import APIRouter, Request, Body, Depends, UploadFile, File, Path, Query
from fastapi.responses import ORJSONResponse

from skill_management.enums import SkillCategoryEnum
from skill_management.schemas.base import ErrorMessage
from skill_management.schemas.file import SkillCertificateResponse
from skill_management.schemas.skill import CreateSkillDataRequest, GetSkillDataResponse, \
    GetSkillDataResponseList, CreateSkillListDataResponse, CreateSkillDataAdminRequest, ProfileSkillDetailsResponse
from skill_management.services.skill import SkillService
from skill_management.utils.auth_manager import JWTBearer, JWTBearerAdmin
from skill_management.utils.logger import get_logger
from skill_management.utils.profile_manager import get_profile_email

skill_router: APIRouter = APIRouter(tags=["skill"])
logger = get_logger()


@skill_router.post("/profile/skills",
                   response_class=ORJSONResponse,
                   response_model=CreateSkillListDataResponse,
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
                                           "experience_year": 4,  # Optional
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
                       user_id: str = Depends(JWTBearer()),
                       service: SkillService = Depends()):
    """
    **Create:** Must provide all the data necessary including *"skill_id"* for creating a new skill. *"status"* is optional.


    **Update:** For update purposes provide *"skill_id"*. Other attributes are optional.
    """
    email = await get_profile_email(user_id=user_id, request=request)
    return await service.create_or_update_skill_by_user(skill_request=skill, email=email)


@skill_router.post("/admin/profile/skills",
                   response_class=ORJSONResponse,
                   response_model=CreateSkillListDataResponse,
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
async def create_skill_by_admin(request: Request,  # type: ignore
                                skill_request: CreateSkillDataAdminRequest = Body(..., examples={
                                    "CREATE": {
                                        "summary": "Create Body",
                                        "description": "a example of body for create operation",
                                        "value": {
                                            "profile_id": uuid.uuid4(),
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
                                                    "profile_id": uuid.uuid4(),
                                                    "skill_id": 1,
                                                    "experience_year": 4,  # Optional
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
                                admin_user_id: str = Depends(JWTBearerAdmin()),
                                service: SkillService = Depends()):
    """
    **Create:** Must provide all the data necessary including *"skill_id"* for creating a new skill. *"status"* is optional.


    **Update:** For update purposes provide *"skill_id"*. Other attributes are optional.
    """
    return await service.create_or_update_skill_by_admin(skill_request=skill_request)


@skill_router.post("/profile/skills/{skill_id}/upload-certificate",
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
                             skill_id: int = Path(..., description="provide the skill id"),
                             files: list[UploadFile] = File(None, description="select certificate files to upload"),
                             user_id: str = Depends(JWTBearer()),
                             service: SkillService = Depends()):
    email = await get_profile_email(user_id=user_id, request=request)
    return await service.upload_certificate(skill_id=skill_id, files=files, email=email)


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


@skill_router.get("/profile/admin/user-profiles/{profile_id}/skills",
                  response_class=ORJSONResponse,
                  response_model=ProfileSkillDetailsResponse,
                  status_code=200,
                  responses={
                      404: {
                          "model": ErrorMessage,
                          "description": "The skills details are not available"
                      },
                      200: {
                          "description": "The skills requested by profile id",
                      },
                  })
async def get_profile_skills_by_admin(request: Request,  # type: ignore
                                     user_id: str = Depends(JWTBearerAdmin()),
                                     profile_id: PydanticObjectId = Path(...,
                                                                         description="input profile id of the user",
                                                                         alias="profile_id"),
                                     service: SkillService = Depends()):
    return await service.get_skill_details_by_admin(profile_id=profile_id)


@skill_router.get("/profile/user-profiles/skills",
                  response_class=ORJSONResponse,
                  response_model=ProfileSkillDetailsResponse,
                  status_code=200,
                  responses={
                      404: {
                          "model": ErrorMessage,
                          "description": "The skills details are not available"
                      },
                      200: {
                          "description": "The skills requested by profile id",
                      },
                  })
async def get_profile_skills_by_user(request: Request,  # type: ignore
                                    user_id: str = Depends(JWTBearer()),
                                    service: SkillService = Depends()):
    email = await get_profile_email(user_id=user_id, request=request)
    return await service.get_skill_details_by_user(email=cast(str, email))
