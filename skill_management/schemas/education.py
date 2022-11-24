from datetime import date
from typing import Any

from pydantic import BaseModel, Field, validator, root_validator

from skill_management.enums import UserStatusEnum


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


class EducationCreateRequest(BaseModel):
    """
    Must provide education id or other information[status is optional]
    """
    education_id: int | None = Field(ge=1, description="id of user's education")
    degree_name: str | None = Field(None, max_length=30, description="degree name of the user's education")
    school_name: str | None = Field(None, max_length=30, description="school name of the user's education")
    passing_year: str | None = Field(None, max_length=4, description="passing year of the user's education")
    grade: float | None = Field(None, ge=2.5, le=5.0, description="grade of the user's education'")
    status: UserStatusEnum = Field(UserStatusEnum.active,
                                   description="""education data validity status
                                   
    1: active, 3: delete""")

    @root_validator
    def any_of(cls, values: dict[str, Any]) -> dict[str, Any]:
        education_id = values.pop('education_id')
        status = values.pop('status')
        if education_id is None:
            if None in values.values():
                raise ValueError("You must provide all the education information when constructing the new education")
        values['education_id'] = education_id
        values['status'] = status
        return values

    @validator("passing_year", always=True)
    def validate_passing_year(cls, value: str) -> str:
        try:
            passing_year: int = int(value)
        except ValueError as val_exec:
            raise ValueError("Not a year")
        if not 1971 <= passing_year <= date.today().year:
            raise ValueError("Not a valid year, must be between 1970 and this year")
        return value

    class Config:
        schema_extra = {
            "example":
                {
                    "degree_name": "B.Sc in Computer Science",
                    "school_name": "University of Dhaka",
                    "passing_year": "2019",
                    "grade": 3.80
                }
        }


class ProfileEducationResponse(EducationBase):
    education_id: int | None = Field(gt=0, description="id of the user education")


class EducationCreateResponse(ProfileEducationResponse):
    class Config:
        schema_extra = {
            "example":
                {
                    "education_id": 2,
                    "degree_name": "B.Sc in Computer Science",
                    "school_name": "University of Dhaka",
                    "passing_year": "2019",
                    "grade": 3.80
                },
        }
