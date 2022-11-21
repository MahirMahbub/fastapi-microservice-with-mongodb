from fastapi import APIRouter, Request, Body, Depends, UploadFile, File, Path

from skill_management.schemas.base import ErrorMessage
from skill_management.schemas.skill import CreateSkillDataResponse, CreateSkillDataRequest, SkillCertificateResponse, \
    GetSkillDataResponse
from skill_management.utils.auth_manager import JWTBearer
from skill_management.utils.logger import get_logger

skill_router: APIRouter = APIRouter(tags=["skill"])
logger = get_logger()


@skill_router.post("/profile/skills",
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
                       skill: CreateSkillDataRequest = Body(...),
                       user_id: str = Depends(JWTBearer())):
    pass


@skill_router.post("/profile/skills/upload-certificate",
                   response_model=SkillCertificateResponse,
                   status_code=201,
                   responses={
                       400: {
                           "model": ErrorMessage,
                           "description": "The certificates are not created"
                       },
                       201: {
                           "description": "The certificates are successfully created",
                       },
                   })
async def upload_certificate(request: Request,  # type: ignore
                             files: list[UploadFile] = File(None),
                             user_id: str = Depends(JWTBearer())):
    pass


@skill_router.get("/profile/skills/{id_}",
                  response_model=GetSkillDataResponse,
                  status_code=200,
                  responses={
                      400: {
                          "model": ErrorMessage,
                          "description": "The certificates are not created"
                      },
                      200: {
                          "description": "The certificates are successfully created",
                      },
                  })
async def get_skill(request: Request,  # type: ignore
                    id_: int = Path(...),
                    user_id: str = Depends(JWTBearer())):
    pass
