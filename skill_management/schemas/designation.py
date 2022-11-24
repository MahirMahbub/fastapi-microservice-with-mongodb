from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, validator

from skill_management.enums import UserStatusEnum
from skill_management.schemas.base import EnumData, ResponseEnumData


class DesignationBase(BaseModel):
    designation: str | None = Field(min_length=2, description="designation of the user")


class DesignationDataResponse(DesignationBase):
    designation_id: int | None = Field(ge=1, description="id of designation")


class ProfileDesignationResponse(DesignationDataResponse):
    start_date: datetime | None = Field(description="start date of designated job")
    end_date: datetime | None = Field(description="end date of designated job")
    designation_status: ResponseEnumData | None = Field(description="designation status of designated job")

    @validator("end_date", always=True)
    def validate_end_date(cls, value: datetime, values: dict[str, Any]) -> datetime | None:
        if values["start_date"] is None:
            return None
        if values["start_date"] > value:
            raise ValueError("end_date must be greater than start_date")
        return value


class DesignationCreateRequest(BaseModel):
    designation_id: int = Field(ge=1, description="autoincrement id of designation")
    start_date: datetime | None = Field(description="start date of designated job")
    end_date: datetime | None = Field(description='''end date of designated job
    
    > start_date''')
    status: UserStatusEnum | None = Field(UserStatusEnum.active,
                                          description="""designation data validity status
                                           
    1: active, 3: delete""")

    @validator("end_date", always=True)
    def validate_end_date(cls, value: datetime, values: dict[str, Any]) -> datetime | None:
        if values["start_date"] is None:
            return None
        if values["start_date"] > value:
            raise ValueError("end_date must be greater than start_date")
        return value
