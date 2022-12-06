from beanie import Document
from pydantic import Field


class Designations(Document):
    id: int = Field(ge=1, description='id of designation')  # type: ignore
    designation: str = Field(min_length=2, description="designation of the user")

    class Settings:
        use_revision = False

class CustomDesignations(Document):
    id: int = Field(ge=1, description='id of custom designation')  # type: ignore
    designation: str = Field(min_length=2, description="custom designation of the user")

    class Settings:
        use_revision = False