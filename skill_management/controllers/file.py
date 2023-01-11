from typing import cast

from beanie import PydanticObjectId
from fastapi import APIRouter, Request, Depends, UploadFile, File, Path, Form, status
from fastapi.responses import ORJSONResponse
from starlette.responses import FileResponse

from skill_management.enums import UserStatusEnum
from skill_management.schemas.base import ErrorMessage, SuccessMessage
from skill_management.schemas.file import FileUploadResponse
from skill_management.services.file import FileService
from skill_management.utils.auth_manager import JWTBearer, JWTBearerAdmin
from skill_management.utils.logger import get_logger
from skill_management.utils.profile_manager import get_profile_email

file_router: APIRouter = APIRouter(tags=["file"])
logger = get_logger()


@file_router.post("/profile/files/upload-resume",
                  response_class=ORJSONResponse,
                  response_model=FileUploadResponse,
                  status_code=status.HTTP_201_CREATED,
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
                        file_status: UserStatusEnum = Form(UserStatusEnum.active, description="status of the file"),
                        service: FileService = Depends(FileService),
                        user_id: str = Depends(JWTBearer())):
    email = await get_profile_email(user_id=user_id, request=request)
    return await service.create_resume(file, file_status, email)


@file_router.post("/profile/files/upload-profile-picture",
                  response_class=ORJSONResponse,
                  response_model=FileUploadResponse,
                  status_code=status.HTTP_201_CREATED,
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
                                 file_status: UserStatusEnum = Form(UserStatusEnum.active,
                                                                    description="status of the file"),
                                 service: FileService = Depends(FileService),
                                 user_id: str = Depends(JWTBearer())):
    email = await get_profile_email(user_id=user_id, request=request)
    return await service.create_profile_picture(file, file_status, email)


@file_router.get('/profile/files/response/{file_id}',
                 response_class=FileResponse,
                 status_code=status.HTTP_200_OK,
                 responses={
                     400: {
                         "model": ErrorMessage,
                         "description": "The profile picture is not available"
                     },
                     200: {
                         "description": "The profile picture is rendered or file provided as attachment",
                     },
                 })
async def get_file_response_for_user(request: Request,  # type: ignore
                                     file_id: PydanticObjectId = Path(...,
                                                                      description="input file id for file response"),
                                     user_id: str = Depends(JWTBearer()),
                                     service: FileService = Depends(FileService)):
    email = await get_profile_email(user_id=user_id, request=request)
    return await service.get_file_response_by_user(file_id, email)


@file_router.get('/admin/files/response/{file_id}',
                 response_class=FileResponse,
                 status_code=status.HTTP_200_OK,
                 responses={
                     400: {
                         "model": ErrorMessage,
                         "description": "The profile picture is not available"
                     },
                     200: {
                         "description": "The profile picture is rendered or file provided as attachment",
                     },
                 })
async def get_file_response_for_admin(request: Request,  # type: ignore
                                      file_id: PydanticObjectId = Path(...,
                                                                       description="input file id for file response"),
                                      admin_user_id: str = Depends(JWTBearerAdmin()),
                                      service: FileService = Depends(FileService)):
    # email = await get_profile_email(user_id=user_id, request=request)
    return await service.get_file_response_by_admin(file_id)


@file_router.delete('/admin/files/{file_id}',
                    response_class=ORJSONResponse,
                    status_code=status.HTTP_200_OK,
                    responses={
                        400: {
                            "model": ErrorMessage,
                            "description": "The profile picture can not be deleted"
                        },
                        200: {
                            "model": SuccessMessage,
                            "description": "The profile picture is deleted successfully",
                        },
                    })
async def delete_file_by_admin(request: Request,  # type: ignore
                               file_id: PydanticObjectId = Path(...,
                                                                description="input file id for file response"),
                               admin_user_id: str = Depends(JWTBearerAdmin()),
                               service: FileService = Depends(FileService)):
    # email = await get_profile_email(user_id=user_id, request=request)
    return await service.delete_file_by_admin(file_id)


@file_router.delete('/profile/files/{file_id}',
                    response_class=ORJSONResponse,
                    status_code=status.HTTP_200_OK,
                    responses={
                        400: {
                            "model": ErrorMessage,
                            "description": "The profile picture can not be deleted"
                        },
                        200: {
                            "model": SuccessMessage,
                            "description": "The profile picture is deleted successfully",
                        },
                    })
async def delete_file_by_user(request: Request,  # type: ignore
                              file_id: PydanticObjectId = Path(...,
                                                               description="input file id for file response"),
                              user_id: str = Depends(JWTBearer()),
                              service: FileService = Depends(FileService)):
    email = await get_profile_email(user_id=user_id, request=request)
    return await service.delete_file_by_user(file_id, email)


@file_router.get('/profile-picture/{profile_id}',
                    response_class=ORJSONResponse,
                    status_code=status.HTTP_200_OK,
                    responses={
                        404: {
                            "model": ErrorMessage,
                            "description": "The profile picture can not be found"
                        },
                        200: {
                            "model": SuccessMessage,
                            "description": "The profile picture is found successfully",
                        },
                    })
async def get_profile_picture(request: Request,
                              profile_id: PydanticObjectId = Path(...,
                                                                  description="input file id for file response"),
                              service: FileService = Depends(FileService)):
    return await service.get_profile_picture(cast(PydanticObjectId, profile_id))
