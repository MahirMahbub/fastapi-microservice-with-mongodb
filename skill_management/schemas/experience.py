from datetime import datetime, timezone, timedelta
from typing import Any

from pydantic import BaseModel, Field, validator

from skill_management.enums import StatusEnum
from skill_management.schemas.base import EnumData


class ProfileExperienceDesignationResponse(BaseModel):
    designation_id: int = Field(description="designation id for profile experience")
    designation: str = Field(description="designation for profile experience")


class ProfileExperienceResponse(BaseModel):
    experience_id: int = Field(gt=0, description="autoincrement experience id for this profile")
    company_name: str = Field(max_length=30, description="name of company that user worked on")
    job_responsibility: str = Field(max_length=255, description="responsibility for job on the company")
    designation: ProfileExperienceDesignationResponse = Field(description="designation for this profile experience")
    start_date: datetime = Field(description="start date of experience")
    end_date: datetime = Field(description="end date of experience")
    status: EnumData = Field(description="designation status of experience")

    @validator("end_date", always=True)
    def validate_end_date(cls, value: datetime, values: dict[str, Any]) -> datetime | None:
        if values["start_date"] is None:
            return None
        if values["start_date"] > value:
            raise ValueError("end_date must be greater than start_date")
        return value


class ExperienceCreateRequest(BaseModel):
    company_name: str = Field(max_length=30, description="name of company that user worked on")
    job_responsibility: str = Field(max_length=255, description="responsibility for job on the company")
    designation_id: int = Field(description="designation id for profile experience")
    start_date: datetime = Field(description="start date of experience")
    end_date: datetime = Field(description='''end date of experience
    
    > start_date''')
    status: str = Field(description='''designation status of experience
    
    '''+", ".join([data.name for data in StatusEnum]))

    @validator("end_date", always=True)
    def validate_end_date(cls, value: datetime, values: dict[str, Any]) -> datetime | None:
        if values["start_date"] is None:
            return None
        if values["start_date"] > value:
            raise ValueError("end_date must be greater than start_date")
        return value

    @validator("status", always=True)
    def validate_status(cls, value: str) -> str | None:
        if value not in [data.name for data in StatusEnum]:
            raise ValueError("status must be valid")
        return value

    class Config:
        schema_extra = {
            "example":
                {
                    "company_name": "X Software",
                    "job_responsibility": "Backend Development",
                    "designation_id": 2,
                    "start_date": datetime.now(timezone.utc) - timedelta(days=500),
                    "end_date": datetime.now(timezone.utc) - timedelta(days=200),
                    "status": "active"
                }
        }


class ExperienceCreateResponse(ProfileExperienceResponse):
    class Config:
        schema_extra = {
            "example":
                {
                    "experience_id": 1,
                    "company_name": "X Software",
                    "job_responsibility": "Backend Development",
                    "designation": {
                        "designation_id": 2,
                        "designation": "Software Developer"
                    },
                    "start_date": datetime.now(timezone.utc) - timedelta(days=500),
                    "end_date": datetime.now(timezone.utc) - timedelta(days=200),
                    "status": {
                        "id": 1,
                        "name": "active"
                    }
                }
        }
