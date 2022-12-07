from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, root_validator, dataclasses, Field


@dataclasses.dataclass
class EnumData:
    id: int = Field(gt=0, description="id is enum value")
    name: str = Field(description="name is enum key")


class ResponseEnumData(BaseModel):
    id: int | None = Field(gt=0, description="id is enum value")
    name: str | None = Field(description="name is enum key")


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


class ErrorMessage(BaseModel):
    detail: str = "An error message"
class SuccessMessage(BaseModel):
    detail: str = "An success message"

class PaginatedResponse(BaseModel):
    previous_page: int | None = Field(description="previous page of current pagination page")
    next_page: int | None = Field(description="next page of current pagination page")
    has_previous: bool | None = Field(description="bool indicator whether current page has previous page")
    has_next: bool | None = Field(description="bool indicator whether current page has next page")
    total_items: int | None = Field(description="total number of items")
    pages: int | None = Field(description="total number of pages")
