from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, root_validator, dataclasses, Field


@dataclasses.dataclass
class EnumData:
    id: int = Field(gt=0, description="id is enum value")
    name: str = Field(description="name is enum key")


class DateMixin(BaseModel):
    created_at: datetime = datetime.now()
    updated_at: Optional[datetime] = None

    class Config:
        validate_assignment = True

    @root_validator
    def number_validator(cls, values: dict[str, Any]) -> dict[str, Any]:
        if values["updated_at"]:
            values["updated_at"] = datetime.now()
        else:
            values["updated_at"] = values["created_at"]
        return values


# class ResponseSchema(BaseModel):
class ErrorMessage(BaseModel):
    message: str = "An error message"
    # error_data: dict[str, Any] = {}
