import re
from datetime import datetime, date, timezone, timedelta

from pydantic import Field, BaseModel, EmailStr, UUID4, validator

from skill_management.schemas.base import EnumData, PaginatedResponse, ResponseEnumData
from skill_management.schemas.designation import DesignationDataResponse, ProfileDesignationResponse
from skill_management.schemas.education import ProfileEducationResponse
from skill_management.schemas.experience import ProfileExperienceResponse
from skill_management.schemas.skill import ProfileSkillDataResponse, ProfileSkillResponse


class ProfileBase(BaseModel):
    name: str | None = Field(max_length=20, min_length=2, description="name of the user")
    # email: EmailStr = Field(description="email address of the user")


class ProfileBasicResponse(ProfileBase):
    id: UUID4 | None = Field(description="id of the user profile")
    url: str | None = Field(description="api endpoint for profile details by id")
    email: EmailStr | None = Field(description="email address of the user")
    mobile: str | None = Field(description="mobile number of the user")
    designation: DesignationDataResponse | None = Field(description="designation basic details of the profile user")
    skills: list[ProfileSkillDataResponse] | None

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
    gender: int = Field(description="gender of the user")
    mobile: str = Field(description="mobile number of the user")
    address: str = Field(max_length=255, description="address of the user")
    about: str = Field(max_length=500, description="about of the user")
    _picture_url: str = Field(max_length=255, description="image response api url of user profile picture")
    experience_year: int = Field(description="experience year of the user")


class ProfilePersonalDetailsResponse(BaseModel):
    name: str | None = Field(max_length=20, min_length=2, description="name of the user")
    date_of_birth: date | None = Field(description="date of birth of the user")
    gender: int | None = Field(description="gender of the user")
    mobile: str | None = Field(description="mobile number of the user")
    address: str | None = Field(max_length=255, description="address of the user")
    about: str | None = Field(max_length=500, description="about of the user")
    _picture_url: str | None = Field(max_length=255, description="image response api url of user profile picture")
    experience_year: int | None = Field(description="experience year of the user")


class ProfileResponse(BaseModel):
    id: UUID4 | None = Field(description="id of the user profile")
    email: EmailStr | None = Field(description="email address of the user")
    designation: ProfileDesignationResponse | None = Field(description="designation details of the profile user")
    skills: list[ProfileSkillResponse] | None
    experience: list[ProfileExperienceResponse] | None
    education: list[ProfileEducationResponse] | None
    personal_details: ProfilePersonalDetailsResponse | None
    profile_status: ResponseEnumData | None = Field(description="profile status/ job type of the user")
    _latest_cv_url: str | None = Field(description="latest CV file response api url")

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
                    "personal_details":
                        {
                            "name": "Chelsey Adams",
                            "date_of_birth": datetime.now(timezone.utc).date() - timedelta(days=10000),
                            "gender": 1,
                            "mobile": "+01611123456",
                            "address": "House: X, State:Y, Z, Country",
                            "about": "Personal Information",
                            "experience_year": 4,
                            "_picture_url": "/files/2"
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
                    "_latest_cv_url": "/file/1"
                }
        }


class PaginatedProfileResponse(PaginatedResponse):
    items: list[ProfileBasicResponse] | None

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
