from datetime import datetime, timezone, timedelta
from typing import Any

from beanie import PydanticObjectId
from pydantic import BaseModel, Field, validator, root_validator

from skill_management.enums import StatusEnum, UserStatusEnum
from skill_management.schemas.base import ResponseEnumData
from skill_management.schemas.designation import DesignationDataResponse


class ProfileExperienceDesignationResponse(BaseModel):
    designation_id: int | None = Field(description="designation id for profile experience")
    designation: str | None = Field(description="designation for profile experience")


class ProfileExperienceResponse(BaseModel):
    experience_id: int | None = Field(ge=1, description="autoincrement experience id for this profile")
    company_name: str | None = Field(max_length=30, description="name of company that user worked on")
    job_responsibility: str | None = Field(max_length=255, description="responsibility for job on the company")
    designation: ProfileExperienceDesignationResponse | None = Field(
        description="designation for this profile experience")
    start_date: datetime | None = Field(description="start date of experience")
    end_date: datetime | None = Field(description="end date of experience")
    status: ResponseEnumData | None = Field(description="designation status of experience")

    @validator("end_date", always=True)
    def validate_end_date(cls, value: datetime, values: dict[str, Any]) -> datetime | None:
        if values["start_date"] is None:
            return None
        if values["start_date"] > value:
            raise ValueError("end_date must be greater than start_date")
        return value


class ExperienceDesignation(DesignationDataResponse):
    pass


class ProfileExperience(BaseModel):
    experience_id: int = Field(ge=1, description="autoincrement experience id for this profile")
    company_name: str = Field(max_length=30, description="name of company that user worked on")
    job_responsibility: str | None = Field(max_length=255, description="responsibility for job on the company")
    designation: ExperienceDesignation = Field(
        description="designation for this profile experience")
    # designation_id: int | None = Field(None, description="designation id for profile experience")
    start_date: datetime | None = Field(description="start date of experience")
    end_date: datetime | None = Field(description="end date of experience")
    status: StatusEnum = Field(default=StatusEnum.active, description="designation status of experience")

    @validator("end_date", always=True)
    def validate_end_date(cls, value: datetime, values: dict[str, Any]) -> datetime | None:
        if values["start_date"] is None:
            return None
        if values["start_date"] > value:
            raise ValueError("end_date must be greater than start_date")
        return value


class ExperienceCreateRequest(BaseModel):
    experience_id: int | None = Field(ge=1, description="id of experiment for user")
    company_name: str | None = Field(max_length=30, description="name of company that user worked on")
    job_responsibility: str | None = Field(description="responsibility for job on the company")
    designation: str | None = Field(description="designation for profile experience")
    start_date: datetime | None = Field(description="start date of experience")
    end_date: datetime | None = Field(description='''end date of experience
    
    > start_date''')
    status: UserStatusEnum | None = Field(None,
                                          description="""experience data validity status
                                   
    1: active, 3: delete""")

    @root_validator
    def any_of(cls, values: dict[str, Any]) -> dict[str, Any]:
        experience_id = values.pop('experience_id')
        try:
            status = values.pop('status')
        except KeyError as key_exec:
            raise ValueError("status is not valid")
        if experience_id is None:
            if None in values.values():
                raise ValueError("You must provide all the experience information when constructing the new experience")
        values['experience_id'] = experience_id
        values['status'] = status
        return values

    @validator("end_date", always=True)
    def validate_end_date(cls, value: datetime, values: dict[str, Any]) -> datetime | None:
        if values["start_date"] is None:
            return None
        if values["start_date"] > value:
            raise ValueError("end_date must be greater than start_date")
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
                    "status": 1
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


class ExperienceCreateAdminRequest(BaseModel):
    profile_id: PydanticObjectId = Field(description="profile id for user")
    experience_id: int | None = Field(ge=1, description="id of experiment for user")
    company_name: str | None = Field(max_length=30, description="name of company that user worked on")
    job_responsibility: str | None = Field(max_length=255, description="responsibility for job on the company")
    designation: str | None = Field(description="designation for profile experience")
    start_date: datetime | None = Field(description="start date of experience")
    end_date: datetime | None = Field(description='''end date of experience

    > start_date''')
    status: UserStatusEnum = Field(UserStatusEnum.active,
                                   description="""experience data validity status

    1: active, 3: delete""")

    @root_validator
    def any_of(cls, values: dict[str, Any]) -> dict[str, Any]:
        experience_id = values.pop('experience_id')
        status = values.pop('status')
        if experience_id is None:
            if None in values.values():
                raise ValueError("You must provide all the experience information when constructing the new experience")
        values['experience_id'] = experience_id
        values['status'] = status
        return values

    @validator("end_date", always=True)
    def validate_end_date(cls, value: datetime, values: dict[str, Any]) -> datetime | None:
        if values["start_date"] is None:
            return None
        if values["start_date"] > value:
            raise ValueError("end_date must be greater than start_date")
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
                    "status": 1
                }
        }


class ExperienceListDataResponse(BaseModel):
    experiences: list[ExperienceCreateResponse]


class ProfileExperienceDetailsResponse(BaseModel):
    experiences: list[ProfileExperienceResponse]
