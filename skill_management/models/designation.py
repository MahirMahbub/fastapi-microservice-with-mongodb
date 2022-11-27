from beanie import Document
from pydantic import Field


class Designations(Document):
    id: int = Field(ge=1, description='id of designation')
    designation: str = Field(min_length=2, description="designation of the user")

    class Settings:
        use_revision = True
        use_state_management = True
        validate_on_save = True
