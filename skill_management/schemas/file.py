from beanie import PydanticObjectId
from pydantic import BaseModel, Field, validator

from skill_management.enums import FileTypeEnum, StatusEnum
from skill_management.schemas.base import EnumData, ResponseEnumData


class ProfileCVFileUpload(BaseModel):
    status: EnumData = Field(description="CV file status")
    _cv_url: str = Field(description="cv url file response api url")


class FileUploadResponse(BaseModel):
    file_id: PydanticObjectId = Field(description="autoincrement id of the file")
    file_name: str = Field(description="name of the file to be uploaded")
    file_type: ResponseEnumData = Field(description="type of file to be uploaded")
    file_size: str = Field(description="file size in KB")
    status: ResponseEnumData = Field(description="status")
    file_response_url: str = Field(description="file url")
    admin_file_response_url: str = Field(description="file url for admin")

    class Config:
        schema_extra = {
            "example":
                {
                    "file_id": 1,
                    "file_name": "cv_x.pdf",
                    "file_type":
                        {
                            "id": 2,
                            "name": "resume"
                        },
                    "file_size": 1024,
                    "status": {
                        "id": 1,
                        "name": "active"
                    },
                    "file_response_url": "/profile/files/<uuid of the file id>",
                    "admin_file_response_url": "/admin/files/<uuid of the file id>"

                }
        }



# class ResumeUploadResponse(FileUploadResponse):
#     file_response_url: str = Field(max_length=255, description="resume file response api url")
#
#     class Config:
#         schema_extra = {
#             "example":
#                 {
#                     "file_id": 1,
#                     "file_name": "cv_x.pdf",
#                     "file_type":
#                         {
#                             "id": 2,
#                             "name": "resume"
#                         },
#                     "file_size": 1024,
#                     "status": {
#                         "id": 1,
#                         "name": "active"
#                     },
#                     "_file_response_url": "/file/1"
#
#                 }
#         }
#
#
# class ProfilePictureUploadResponse(FileUploadResponse):
#     file_response_url: str = Field(max_length=255, description="profile picture response api url")
#
#     class Config:
#         schema_extra = {
#             "example":
#                 {
#                     "file_id": 2,
#                     "file_name": "profile_picture_x.jpg",
#                     "file_type":
#                         {
#                             "id": 1,
#                             "name": "picture"
#                         },
#                     "file_size": 1024,
#                     "status": {
#                         "id": 1,
#                         "name": "active"
#                     },
#                     "_file_response_url": "/file/2"
#
#                 }
#         }


class SkillCertificateResponse(BaseModel):
    succeed_upload_list: list[str] = []
    failed_upload_list: list[str] = []


class FileResponse(BaseModel):
    file_name: str | None = Field(description="name of the file")
    url: str = Field(description="api url of the file")
    status: ResponseEnumData = Field(description="status of the file")
