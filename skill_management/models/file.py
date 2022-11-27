from beanie import Document
from pydantic import Field

from skill_management.enums import StatusEnum
from skill_management.schemas.base import EnumData


class Files(Document):
    id: int = Field(description="autoincrement id of the file")
    file_name: str = Field(description="name of the file to be uploaded")
    file_type: EnumData = Field(description="type of file to be uploaded")
    file_size: int = Field(le=2040, description="file size in KB")
    status: StatusEnum = Field(description="status of the file")