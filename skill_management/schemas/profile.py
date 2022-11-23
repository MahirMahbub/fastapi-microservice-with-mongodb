import re
from datetime import datetime, date, timezone, timedelta
from typing import Any, Sequence

from pydantic import Field, BaseModel, EmailStr, UUID4, validator

from skill_management.schemas.base import EnumData, PaginatedResponse
from skill_management.schemas.education import ProfileEducationResponse
from skill_management.schemas.experience import ProfileExperienceResponse
from skill_management.schemas.skill import ProfileSkillDataResponse, ProfileSkillResponse


class DesignationBase(BaseModel):
    designation: str = Field(min_length=2, description="designation of the employee")


class DesignationDataResponse(DesignationBase):
    designation_id: int = Field(gt=0, description="autoincrement id of designation")


class ProfileBase(BaseModel):
    name: str = Field(max_length=20, min_length=2, description="name of the user")
    # email: EmailStr = Field(description="email address of the user")


class ProfileBasicResponse(ProfileBase):
    id: UUID4 = Field(description="id of the user profile")
    url: str = Field(description="api endpoint for profile details by id")
    email: EmailStr = Field(description="email address of the user")
    mobile: str = Field(description="mobile number of the user")
    designation: DesignationDataResponse = Field(description="designation basic details of the profile user")
    skills: list[ProfileSkillDataResponse]

    @validator("mobile", always=True)
    def validate_mobile(cls, value: str) -> str:
        regex = r"^(\+)[1-9][0-9\-\(\)\.]{9,15}$"
        if value and not re.search(regex, value, re.I):
            raise ValueError("Phone Number Invalid.")
        return value

    class Config:
        schema_extra = {
            "example":
                {
                    "id": "954eba99-b1ec-4c1f-b5b1-3cc9db9e59e0",
                    "_url": "/admin/user-profiles/954eba99-b1ec-4c1f-b5b1-3cc9db9e59e0",
                    "email": "developer.ixorasolution@gmail.com",
                    "name": "Chelsey Adams",
                    "mobile": "+01611123456",
                    "designation":
                        {
                            "designation_id": 1,
                            "designation": "Software Engineer"
                        },
                    "skills": [
                        {
                            "experience_year": 4,
                            "level": 4,
                            "skill_name": "react",
                            "skill_id": 1
                        },
                        {
                            "experience_year": 4,
                            "level": 7,
                            "skill_name": "django",
                            "skill_id": 2
                        }
                    ]

                }
        }


class ProfilePersonalDetails(BaseModel):
    name: str = Field(max_length=20, min_length=2, description="name of the user")
    date_of_birth: date = Field(description="date of birth of the user")
    gender: EnumData = Field(description="gender of the user")
    mobile: str = Field(description="mobile number of the user")
    address: str = Field(max_length=255, description="address of the user")
    about: str = Field(max_length=500, description="about of the user")
    _picture_url: str = Field(max_length=255, description="image response api url of user profile picture")
    experience_year: int = Field(description="experience year of the user")


class ProfileDesignationResponse(DesignationDataResponse):
    start_date: datetime = Field(description="start date of designated job")
    end_date: datetime = Field(description="end date of designated job")
    designation_status: EnumData = Field(description="designation status of designated job")

    @validator("end_date", always=True)
    def validate_end_date(cls, value: datetime, values: dict[str, Any]) -> datetime | None:
        if values["start_date"] is None:
            return None
        if values["start_date"] > value:
            raise ValueError("end_date must be greater than start_date")
        return value


class ProfileResponse(BaseModel):
    id: UUID4 = Field(description="id of the user profile")
    email: EmailStr = Field(description="email address of the user")
    designation: ProfileDesignationResponse = Field(description="designation details of the profile user")
    skills: list[ProfileSkillResponse]
    experience: list[ProfileExperienceResponse]
    education: list[ProfileEducationResponse]
    personal_details: ProfilePersonalDetails
    profile_status: EnumData = Field(description="profile status/ job type of the user")

    class Config:
        schema_extra = {
            "example":
                {
                    "id": "954eba99-b1ec-4c1f-b5b1-3cc9db9e59e0",
                    "email": "developer.ixorasolution@gmail.com",
                    "designation": {
                        "designation": "Software Engineer",
                        "designation_id": 1,
                        "start_date": datetime.now(timezone.utc),
                        "end_date": datetime.now(timezone.utc) + timedelta(days=1),
                        "designation_status": {
                            "id": 1,
                            "name": "active"
                        }
                    },
                    "skills": [
                        {
                            "skill_id": 1,
                            "skill_name": "react",
                            "skill_type": {
                                "id": 1,
                                "name": "core_skill"
                            },
                            "skill_category": [
                                {
                                    "id": 1,
                                    "name": "frontend"
                                },
                                {
                                    "id": 2,
                                    "name": "backend"
                                }
                            ],
                            "experience_year": 4,
                            "number_of_projects": 4,
                            "level": 5,
                            "training_duration": 2,
                            "achievements": "1",
                            "achievements_description": "It is the achievement's description",
                            "certificate": "1",
                            "status": {
                                "id": 1,
                                "name": "active"
                            }
                        }
                    ],
                    "experience": [
                        {
                            "experience_id": 1,
                            "company_name": "X Software",
                            "job_responsibility": "Backend Development",
                            "designation": {
                                "designation_id": 1,
                                "designation": "Software Developer"
                            },
                            "start_date": datetime.now(timezone.utc) - timedelta(days=1000),
                            "end_date": datetime.now(timezone.utc) - timedelta(days=500),
                            "status": {
                                "id": 1,
                                "name": "active"
                            }
                        },
                        {
                            "experience_id": 2,
                            "company_name": "Y Software",
                            "job_responsibility": "Backend Development",
                            "designation": {
                                "designation_id": 1,
                                "designation": "Software Engineer"
                            },
                            "start_date": datetime.now(timezone.utc) - timedelta(days=500),
                            "end_date": datetime.now(timezone.utc) - timedelta(days=200),
                            "status": {
                                "id": 1,
                                "name": "active"
                            }
                        }
                    ],
                    "education": [
                        {
                            "education_id": 2,
                            "degree_name": "B.Sc in Computer Science",
                            "school_name": "University of Dhaka",
                            "passing_year": "2019",
                            "grade": 4.00
                        },
                        {
                            "education_id": 1,
                            "degree_name": "HSC",
                            "school_name": "Dhaka Secondary and Higher Secondary Education Board",
                            "passing_year": "2015",
                            "grade": 5.00
                        }
                    ],
                    "profile_status": {
                        "id": 1,
                        "name": "full_time"
                    },
                }
        }


class PaginatedProfileResponse(PaginatedResponse):
    items: list[ProfileBasicResponse]

    class Config:
        schema_extra = {
            "example":
                {
                    "items": [
                        {
                            "id": "954eba99-b1ec-4c1f-b5b1-3cc9db9e59e0",
                            "_url": "/admin/user-profiles/954eba99-b1ec-4c1f-b5b1-3cc9db9e59e0",
                            "email": "developer.ixorasolution@gmail.com",
                            "name": "Chelsey Adams",
                            "mobile": "+01611123456",
                            "designation": {
                                "designation_id": 1,
                                "designation": "Software Engineer"
                            },
                            "skills": [
                                {
                                    "experience_year": 4,
                                    "level": 4,
                                    "skill_name": "react",
                                    "skill_id": 1
                                },
                                {
                                    "experience_year": 4,
                                    "level": 7,
                                    "skill_name": "django",
                                    "skill_id": 2
                                }
                            ]
                        }
                    ],
                    "previous_page": 0,
                    "next_page": 2,
                    "has_previous": False,
                    "has_next": True,
                    "total_items": 100,
                    "pages": 10
                }
        }
