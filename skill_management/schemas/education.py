from datetime import date
from typing import Any

from beanie import PydanticObjectId
from pydantic import BaseModel, Field, validator, root_validator

from skill_management.enums import UserStatusEnum, StatusEnum
from skill_management.schemas.base import ResponseEnumData


class EducationBase(BaseModel):
    degree_name: str | None = Field(max_length=30, description="degree name of the user education")
    school_name: str | None = Field(max_length=30, description="school name of the user education")
    passing_year: str | None = Field(max_length=4, description="passing year of the user education")
    grade: float | None = Field(ge=2.5, le=5.0)

    @validator("passing_year", always=True)
    def validate_passing_year(cls, value: str) -> str:
        try:
            passing_year: int = int(value)
        except ValueError as val_exec:
            raise ValueError("Not a year")
        if not 1971 <= passing_year <= date.today().year:
            raise ValueError("Not a valid year, must be between 1970 and this year")
        return value


class ProfileEducation(BaseModel):
    education_id: int = Field(ge=1, description="id of user's education")
    degree_name: str | None = Field(None, max_length=30, description="degree name of the user's education")
    school_name: str | None = Field(None, max_length=30, description="school name of the user's education")
    passing_year: str | None = Field(None, max_length=4, description="passing year of the user's education")
    grade: float | None = Field(None, ge=2.5, le=5.0, description="grade of the user's education'")
    status: StatusEnum|None = Field(StatusEnum.active,
                               description="""education data validity status

    1: active, 3: delete""")


class EducationCreateRequest(BaseModel):
    """
    Must provide education id or other information[status is optional]
    """
    education_id: int | None = Field(ge=1, description="id of user's education")
    degree_name: str | None = Field(None, max_length=30, description="degree name of the user's education")
    school_name: str | None = Field(None, max_length=30, description="school name of the user's education")
    passing_year: str | None = Field(None, max_length=4, description="passing year of the user's education")
    grade: float | None = Field(None, ge=2.5, le=5.0, description="grade of the user's education'")
    status: UserStatusEnum | None = Field(None,
                                   description="""education data validity status
                                   
    1: active, 3: delete""")

    @root_validator
    def any_of(cls, values: dict[str, Any]) -> dict[str, Any]:
        education_id = values.pop('education_id')

        try:
            status = values.pop('status')
        except KeyError as key_exec:
            raise ValueError("status is not valid")
        if education_id is None:
            if None in values.values():
                raise ValueError("You must provide all the education information when constructing the new education")
        values['education_id'] = education_id
        values['status'] = status
        return values

    @validator("passing_year", always=True)
    def validate_passing_year(cls, value: str | None) -> str | None:
        if value is None:
            return value
        try:
            passing_year: int = int(value)
        except ValueError as val_exec:
            raise ValueError("Not a year")
        if not 1971 <= passing_year <= date.today().year:
            raise ValueError("Not a valid year, must be between 1970 and this year")
        return value


class EducationCreateAdminRequest(BaseModel):
    """
    Must provide education id or other information[status is optional]
    """
    profile_id: PydanticObjectId = Field(description="profile_id of the user")
    education_id: int | None = Field(ge=1, description="id of user's education")
    degree_name: str | None = Field(None, max_length=30, description="degree name of the user's education")
    school_name: str | None = Field(None, max_length=30, description="school name of the user's education")
    passing_year: str | None = Field(None, max_length=4, description="passing year of the user's education")
    grade: float | None = Field(None, ge=2.5, le=5.0, description="grade of the user's education'")
    status: StatusEnum|None = Field(None,
                               description="""education data validity status

    1: active, 3: delete""")

    @root_validator
    def any_of(cls, values: dict[str, Any]) -> dict[str, Any]:
        education_id = values.pop('education_id')
        try:
            status = values.pop('status')
        except KeyError as key_exec:
            raise ValueError("status is not valid")
        if education_id is None:
            if None in values.values():
                raise ValueError("You must provide all the education information when constructing the new education")
        values['education_id'] = education_id
        values['status'] = status
        return values

    @validator("passing_year", always=True)
    def validate_passing_year(cls, value: str | None) -> str | None:
        if value is None:
            return None
        try:
            passing_year: int = int(value)
        except ValueError as val_exec:
            raise ValueError("Not a year")
        if not 1971 <= passing_year <= date.today().year:
            raise ValueError("Not a valid year, must be between 1970 and this year")
        return value


class ProfileEducationResponse(EducationBase):
    education_id: int | None = Field(gt=0, description="id of the user education")
    status: ResponseEnumData| None = Field(description="status of the education")


class EducationCreateResponse(ProfileEducationResponse):
    status: ResponseEnumData | None

    class Config:
        schema_extra = {
            "example":
                {
                    "education_id": 1,
                    "degree_name": "B.Sc in Computer Science",
                    "school_name": "University of Dhaka",
                    "passing_year": "2019",
                    "grade": 3.80,
                    "status": 1
                },
        }


class EducationListDataResponse(BaseModel):
    educations: list[EducationCreateResponse]


class ProfileEducationDetailsResponse(BaseModel):
    educations: list[ProfileEducationResponse]
