import os
from datetime import datetime, timezone
from typing import cast

from beanie import PydanticObjectId
from fastapi import UploadFile, status, HTTPException
from fastapi.responses import FileResponse
from pydantic import ValidationError

from skill_management.enums import UserStatusEnum, FileTypeEnum, StatusEnum
from skill_management.models.file import Files
from skill_management.repositories.file import FileRepository
from skill_management.repositories.profile import ProfileRepository
from skill_management.schemas.base import ResponseEnumData
from skill_management.schemas.file import FileUploadResponse
from skill_management.schemas.profile import ProfileView
from skill_management.utils.file_name_search import next_file_name

IMAGE_FORMAT = (
    '.ras', '.xwd', '.bmp', '.jpe',
    '.jpg', '.jpeg', '.xpm', '.ief', '.pbm',
    '.tif', '.gif', '.ppm', '.xbm', '.tiff',
    '.rgb', '.pgm', '.png', '.pnm')


class FileService:
    def __init__(self) -> None:
        self.file_path = os.getcwd() + cast(str, os.getenv("FILE_UPLOAD_PATH"))

    @staticmethod
    async def read(path: str) -> str:
        with open(path, 'r') as f:
            return f.read()

    @staticmethod
    async def write(data: bytes, save_path: str) -> int:
        with open(save_path, 'wb') as f:
            return f.write(data)

    async def create_resume(self, file: UploadFile, file_status: UserStatusEnum,
                            email: str) -> FileUploadResponse | None:
        extension, file_pattern, main_file_name = await self._get_filename_and_extension(file)
        if not extension == "pdf":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Only pdf files are allowed")
        file_name: str = await next_file_name(file_pattern, self.file_path, main_file_name)
        ########################
        save_path = self.file_path + file_name
        await self.write(file.file.read(), save_path)
        profile_crud_manager = ProfileRepository()
        profile: ProfileView | None = cast(
            ProfileView, await profile_crud_manager.get_by_query(
                query={"user_id": email},
                projection_model=ProfileView
            )
        )
        return await self._create_file(file_name=file_name, location=self.file_path,
                                       owner=cast(ProfileView, profile).id,
                                       file_status=file_status, file_type=FileTypeEnum.resume,
                                       file_size=os.path.getsize(save_path), skill_id=None)
        # headers = {'Content-Disposition': 'attachment; filename=%s' % file_name}
        # return FileResponse(path=save_path, headers=headers)

    async def create_profile_picture(self, file: UploadFile,
                                     file_status: UserStatusEnum, email: str) -> FileUploadResponse | None:
        extension, file_pattern, main_file_name = await self._get_filename_and_extension(file)
        if not "." + extension in IMAGE_FORMAT:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Only pdf files are allowed. allowed formats are: " + ", ".join(IMAGE_FORMAT))
        file_name: str = await next_file_name(file_pattern, self.file_path, main_file_name)
        ########################
        save_path = self.file_path + file_name
        await self.write(file.file.read(), save_path)
        profile_crud_manager = ProfileRepository()
        profile: ProfileView = cast(ProfileView, await profile_crud_manager.get_by_query(
            query={"user_id": email},
            projection_model=ProfileView))

        return await self._create_file(file_name=file_name, location=self.file_path, owner=profile.id,
                                       file_status=file_status, file_type=FileTypeEnum.picture,
                                       file_size=os.path.getsize(save_path), skill_id=None)
        # headers = {'Content-Disposition': 'attachment; filename=%s' % file_name}
        # return FileResponse(path=save_path, headers=headers)

    async def create_certificate(self, file: UploadFile,
                                 skill_id: int,
                                 file_status: UserStatusEnum,
                                 email: str) -> FileUploadResponse | None:
        extension, file_pattern, main_file_name = await self._get_filename_and_extension(file)
        if not "." + extension in IMAGE_FORMAT:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Only pdf files are allowed. allowed formats are: " + ", ".join(IMAGE_FORMAT))
        file_name: str = await next_file_name(file_pattern, self.file_path, main_file_name)
        ########################
        save_path = self.file_path + file_name
        await self.write(file.file.read(), save_path)
        profile_crud_manager = ProfileRepository()
        profile: ProfileView | None = cast(
            ProfileView, await profile_crud_manager.get_by_query(
                query={"user_id": email},
                projection_model=ProfileView
            )
        )
        return await self._create_file(file_name=file_name,
                                       location=self.file_path,
                                       owner=cast(ProfileView, profile).id,
                                       file_status=file_status,
                                       file_type=FileTypeEnum.certificate,
                                       file_size=os.path.getsize(save_path),
                                       skill_id=skill_id)

    @staticmethod
    async def _get_filename_and_extension(file: UploadFile) -> tuple[str, str, str]:
        name, extension = file.filename.split(".")
        file_pattern: str = name + "(" + "%s" + ")" + "." + extension
        main_file_name: str = name + "." + extension
        return extension, file_pattern, main_file_name

    @staticmethod
    async def _create_file(file_name: str, location: str,
                           owner: PydanticObjectId, file_status: UserStatusEnum,
                           file_type: FileTypeEnum,
                           file_size: int, skill_id: int | None = None) -> FileUploadResponse | None:
        try:
            file = Files(file_name=file_name,
                         location=location,
                         owner=owner,
                         status=cast(StatusEnum, file_status),
                         file_type=file_type,
                         file_size=file_size / 1000,
                         skill_id=skill_id,
                         created_at=cast(datetime, datetime.now(timezone.utc).isoformat()))
            if file_type == FileTypeEnum.picture:
                file_crud_manager = FileRepository()
                changed_response = cast(
                    Files, await file_crud_manager.update_by_query(
                        query={
                            "owner": owner,
                            "file_type": FileTypeEnum.picture
                        }, item_dict={
                            "status": UserStatusEnum.delete
                        }
                    )
                )
            await file.insert()
        except ValidationError as valid_exec:
            os.remove(location + file_name)
            return None
        try:
            response = FileUploadResponse(file_id=cast(PydanticObjectId, file.id),
                                          file_name=file.file_name,
                                          file_type=ResponseEnumData(id=file.file_type,
                                                                     name=FileTypeEnum(file.file_type).name),
                                          file_size=str(file.file_size) + "KB",
                                          status=ResponseEnumData(id=file.status,
                                                                  name=StatusEnum(file.status).name),
                                          file_response_url="/profile/files/response/" + str(file.id),
                                          admin_file_response_url="/admin/files/response/" + str(file.id))
        except ValidationError as valid_exec:
            response = None
        return response

    @staticmethod
    async def get_file_response_by_user(file_id: PydanticObjectId, email: str) -> FileResponse:
        profile_crud_manager = ProfileRepository()
        profile: ProfileView | None = cast(
            ProfileView | None, await profile_crud_manager.get_by_query(
                query={"user_id": email},
                projection_model=ProfileView
            )
        )
        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile is not found"
            )
        file: Files | None = await Files.find(
            {
                "_id": file_id,
                "status": UserStatusEnum.active
            }
        ).first_or_none()
        if file is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        # headers = {'Content-Disposition': 'attachment; filename=%s' % file.file_name}
        if not file.file_type == FileTypeEnum.picture:
            headers = {'Content-Disposition': 'attachment; filename=%s' % file.file_name}
            return FileResponse(path=file.location + file.file_name, headers=headers)
        else:
            return FileResponse(path=file.location + file.file_name)

    @staticmethod
    async def get_file_response_by_admin(file_id: PydanticObjectId) -> FileResponse:
        file: Files | None = await Files.find(
            {
                "_id": file_id,
                "status": UserStatusEnum.active
            }
        ).first_or_none()
        if file is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        # headers = {'Content-Disposition': 'attachment; filename=%s' % file.file_name}
        if not file.file_type == FileTypeEnum.picture:
            headers = {'Content-Disposition': 'attachment; filename=%s' % file.file_name}
            return FileResponse(path=file.location + file.file_name, headers=headers)
        else:
            return FileResponse(path=file.location + file.file_name)

    @staticmethod
    async def delete_file_by_admin(file_id: PydanticObjectId) -> None:
        file_crud_manager = FileRepository()
        file: Files = cast(Files, await file_crud_manager.get_by_query(query={
            "_id": file_id,
            "status": UserStatusEnum.active
        }))
        if file is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        changed_response = cast(Files, await file_crud_manager.update_by_query(query={
            "_id": file_id
        }, item_dict={"status": UserStatusEnum.delete}))
        if changed_response is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File not deleted"
            )
        if not changed_response.status == UserStatusEnum.delete:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File not deleted")
        else:
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail="File deleted")

    @staticmethod
    async def delete_file_by_user(file_id: PydanticObjectId, email: str) -> None:
        file_crud_manager = FileRepository()
        profile_crud_manager = ProfileRepository()
        profile: ProfileView | None = cast(
            ProfileView | None, await profile_crud_manager.get_by_query(
                query={"user_id": email},
                projection_model=ProfileView
            )
        )
        if profile is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        file: Files = cast(Files, await file_crud_manager.get_by_query(query={
            "_id": file_id,
            "status": UserStatusEnum.active,
            "owner": profile.id
        }))
        if file is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        changed_response = cast(Files, await file_crud_manager.update_by_query(query={
            "_id": file_id
        }, item_dict={"status": UserStatusEnum.delete}))
        if changed_response is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File not deleted"
            )
        if not changed_response.status == UserStatusEnum.delete:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File not deleted")
        else:
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail="File deleted")

    @staticmethod
    async def get_profile_picture(profile_id: PydanticObjectId) -> FileResponse:
        file: Files | None = await Files.find(
            {
                "owner": profile_id,
                "status": UserStatusEnum.active,
                "file_type": FileTypeEnum.picture
            }
        ).first_or_none()
        if file is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile picture not found"
            )
        else:
            headers = {'Content-Disposition': 'attachment; filename=%s' % file.file_name}
            return FileResponse(path=file.location + file.file_name, headers=headers)