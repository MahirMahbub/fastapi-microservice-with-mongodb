from beanie import Document, PydanticObjectId
from pydantic import Field

from skill_management.enums import StatusEnum, FileTypeEnum


class Files(Document):
    file_name: str = Field(description="name of the file to be uploaded")
    file_type: FileTypeEnum = Field(description="type of file to be uploaded")
    file_size: float = Field(le=2040, description="file size in KB")
    status: StatusEnum = Field(description="status of the file")
    location: str = Field(description="location of the file")
    owner: PydanticObjectId = Field(description="owner of the file")
    skill_id: int|None = Field(None, description="skill id of the file that is a certificate")

    class Settings:
        use_revision = True
        use_state_management = True
        validate_on_save = True
