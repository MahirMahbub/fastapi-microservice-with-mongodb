from fastapi import APIRouter, Request, Depends, UploadFile, File, Path
from fastapi.responses import ORJSONResponse
from starlette.responses import FileResponse

from skill_management.schemas.base import ErrorMessage
from skill_management.schemas.file import ResumeUploadResponse, ProfilePictureUploadResponse
from skill_management.utils.auth_manager import JWTBearer
from skill_management.utils.logger import get_logger

file_router: APIRouter = APIRouter(tags=["file"])
logger = get_logger()


@file_router.post("/profile/skills/upload-resume",
                  response_class=ORJSONResponse,
                  response_model=ResumeUploadResponse,
                  status_code=201,
                  responses={
                      400: {
                          "model": ErrorMessage,
                          "description": "The resume is not uploaded"
                      },
                      201: {
                          "description": "The resume is successfully uploaded",
                      },
                  })
async def upload_resume(request: Request,  # type: ignore
                        file: UploadFile = File(description="select certificate files to upload"),
                        user_id: str = Depends(JWTBearer())):
    pass


@file_router.post("/profile/skills/upload-profile-picture",
                  response_class=ORJSONResponse,
                  response_model=ProfilePictureUploadResponse,
                  status_code=201,
                  responses={
                      400: {
                          "model": ErrorMessage,
                          "description": "The profile picture is not uploaded"
                      },
                      201: {
                          "description": "The profile picture  is successfully uploaded",
                      },
                  })
async def upload_profile_picture(request: Request,  # type: ignore
                                 file: UploadFile = File(description="select certificate files to upload"),
                                 user_id: str = Depends(JWTBearer())):
    pass


@file_router.get('/file/{file-id}',
                 response_class=FileResponse,
                 status_code=200,
                 responses={
                     400: {
                         "model": ErrorMessage,
                         "description": "The profile picture is not available"
                     },
                     200: {
                         "description": "The profile picture is rendered",
                     },
                 })
async def response_file(file_id: int = Path(..., description="input file id for file response", alias="file-id"),  # type: ignore
                        user_id: str = Depends(JWTBearer())):
    pass
