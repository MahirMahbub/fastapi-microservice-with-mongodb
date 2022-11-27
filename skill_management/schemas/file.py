from pydantic import BaseModel, Field, validator

from skill_management.enums import FileTypeEnum, StatusEnum
from skill_management.schemas.base import EnumData, ResponseEnumData


class ProfileCVFileUpload(BaseModel):
    status: EnumData = Field(description="CV file status")
    _cv_url: str = Field(description="cv url file response api url")


class FileUploadResponse(BaseModel):
    file_id: int = Field(description="autoincrement id of the file")
    file_name: str = Field(description="name of the file to be uploaded")
    file_type: EnumData = Field(description="type of file to be uploaded")
    file_size: int = Field(le=2040, description="file size in KB")
    status: ResponseEnumData = Field(description="status")

    @validator("file_type", always=True)
    def validate_file_type(cls, value: str) -> str | None:
        if value not in [data.name for data in FileTypeEnum]:
            raise ValueError("file type must be valid")
        return value

    # @validator("status", always=True)
    # def validate_status(cls, value: str) -> str | None:
    #     if value not in [data.name for data in StatusEnum]:
    #         raise ValueError("status must be valid")
    #     return value


class ResumeUploadResponse(FileUploadResponse):
    _file_response_url: str = Field(max_length=255, description="resume file response api url")

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
                    "_file_response_url": "/file/1"

                }
        }


class ProfilePictureUploadResponse(FileUploadResponse):
    _file_response_url: str = Field(max_length=255, description="profile picture response api url")

    class Config:
        schema_extra = {
            "example":
                {
                    "file_id": 2,
                    "file_name": "profile_picture_x.jpg",
                    "file_type":
                        {
                            "id": 1,
                            "name": "picture"
                        },
                    "file_size": 1024,
                    "status": {
                        "id": 1,
                        "name": "active"
                    },
                    "_file_response_url": "/file/2"

                }
        }


class SkillCertificateResponse(BaseModel):
    succeed_upload_list: list[str] = []
    failed_upload_list: list[str] = []
