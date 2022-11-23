from fastapi import APIRouter, Request, Body, Depends, UploadFile, File, Path, Query
from fastapi.responses import ORJSONResponse

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
                       skill: CreateSkillDataRequest = Body(..., description="provide all required attributes to "
                                                                             "create a new skill"),
                       user_id: str = Depends(JWTBearer())):
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
                         skill_category: str | None = Query(default=None, description="input skill category as string",
                                                            alias="skill-category"),
                         skill_name: str | None = Query(default=None, description="input skill name as string",
                                                        alias="skill-name"),
                         user_id: str = Depends(JWTBearer())):
    pass
