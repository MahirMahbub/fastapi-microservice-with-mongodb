from fastapi import APIRouter, Request, Body, Depends, UploadFile, File

from skill_management.schemas.base import ErrorMessage
from skill_management.schemas.skill import SkillDataResponse, SkillDataRequest, SkillCertificateResponse
from skill_management.utils.auth_manager import JWTBearer
from skill_management.utils.logger import get_logger

skill_router: APIRouter = APIRouter(tags=["skill"])
logger = get_logger()


@skill_router.post("/profile/skill",
                   response_model=SkillDataResponse,
                   status_code=201,
                   responses={
                       400: {
                           "model": ErrorMessage,
                           "description": "The skill is not created"
                       },
                       201: {
                           "description": "The skill is successfully created",
                       },
                   },
                   )
async def skill_create(request: Request,  # type: ignore
                       skill: SkillDataRequest = Body(...),
                       jwt_data: str = Depends(JWTBearer())):
    pass


@skill_router.post("/profile/skill/upload-certificate",
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
                   },
                   )
async def upload_certificate(request: Request,  # type: ignore
                             files: list[UploadFile] = File(None),
                             jwt_data: str = Depends(JWTBearer())):
    pass
