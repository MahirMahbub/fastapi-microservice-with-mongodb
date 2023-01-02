import datetime
import uuid
from datetime import date, timezone, timedelta
from typing import Any

from beanie import PydanticObjectId
from pydantic import Field, BaseModel, EmailStr, validator, root_validator

from skill_management.enums import GenderEnum, ProfileStatusEnum, DesignationStatusEnum
from skill_management.schemas.base import PaginatedResponse, ResponseEnumData
from skill_management.schemas.designation import DesignationDataResponse, ProfileDesignationResponse, \
    DesignationDataCreate, ProfileDesignation
from skill_management.schemas.education import ProfileEducationResponse, ProfileEducation
from skill_management.schemas.experience import ProfileExperienceResponse, ProfileExperience
from skill_management.schemas.file import FileResponse
from skill_management.schemas.skill import ProfileSkillDataResponse, ProfileSkillResponse, ProfileSkill


class ProfileBase(BaseModel):
    name: str | None = Field(max_length=20, min_length=2, description="name of the user")


class ProfileBasicResponse(ProfileBase):
    id: PydanticObjectId | str | None = Field(description="id of the user profile")
    url: str | None = Field(description="api endpoint for profile details by id")
    email: EmailStr | None = Field(description="email address of the user")
    mobile: str | None = Field(description="mobile number of the user")
    designation: DesignationDataResponse | None = Field(description="designation basic details of the profile user")
    skills: list[ProfileSkillDataResponse] | None
    profile_status: ResponseEnumData | None = Field(description="profile status of the user")

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
    name: str | None = Field(max_length=20, min_length=2, description="name of the user")
    date_of_birth: date | None = Field(description="""date of birth of the user
    > 15 years or 5844 days
    """)
    gender: GenderEnum = Field(default=GenderEnum.others, description="gender of the user")
    mobile: str | None = Field(description="mobile number of the user")
    address: str | None = Field(max_length=255, description="address of the user")
    about: str | None = Field(max_length=500, description="about of the user")
    experience_year: int | None = Field(description="experience year of the user")

    @validator("date_of_birth", always=True)
    def validate_date_of_birth(cls, value: date | None) -> date | None:
        if value is None:
            return value
        if abs((datetime.datetime.now().date() - value).days) < 5844:
            raise ValueError("input a valid date of birth. you must be at least 15 years or 5844 days old.")
        return value


class ProfilePersonalDetailsResponse(BaseModel):
    name: str | None = Field(max_length=20, min_length=2, description="name of the user")
    date_of_birth: date | None = Field(description="date of birth of the user")
    gender: ResponseEnumData | None = Field(description="gender of the user")
    mobile: str | None = Field(description="mobile number of the user")
    address: str | None = Field(max_length=255, description="address of the user")
    about: str | None = Field(max_length=500, description="about of the user")
    picture_url: str | None = Field(max_length=255, description="image response api url of user profile picture")
    experience_year: int | None = Field(description="experience year of the user")
    cv_urls: list[FileResponse] = Field(min_items=0, max_items=3, description="cv urls of the user")

    @validator("date_of_birth", always=True)
    def validate_date_of_birth(cls, value: date | None) -> date | None:
        if value is None:
            return value
        if abs((datetime.datetime.now().date() - value).days) < 5844:
            raise ValueError("input a valid date of birth. you must be at least 15 years or 5844 days old.")
        return value


class ProfileDetailsResponse(BaseModel):
    id: PydanticObjectId | None = Field(description="id of the user profile")
    email: str | None = Field(description="email address of the user")
    personal_details: ProfilePersonalDetailsResponse | None
    profile_status: ResponseEnumData | None = Field(description="profile status/ job type of the user")

    class Config:
        schema_extra = {
            "example": {
                "id": uuid.uuid4(),
                "email": "developer.ixorasolution@gmail.com",
                "personal_details": {
                    "name": "Chelsey Adams",
                    "date_of_birth": (datetime.datetime.now() - datetime.timedelta(days=5543)).date(),
                    "gender": {
                        "id": 1,
                        "name": "male"
                    },
                    "mobile": "+01611123456",
                    "address": "House: X, State:Y, Z, Country",
                    "about": "about the user",
                    "picture_url": "/profile/files/response/42242mjj2424",
                    "experience_year": 4
                },
                "profile_status": {
                    "id": 1,
                    "name": "active"
                },
                "cv_urls": [
                    {
                        "file_name": "Academic CV.pdf",
                        "url": "/profile/files/response/6399930b837c0dae0cd1cc9b",
                        "status": {
                            "id": 1,
                            "name": "active"
                        }
                    }
                ]
            }
        }


class ProfileResponse(BaseModel):
    id: PydanticObjectId | None = Field(description="id of the user profile")
    email: EmailStr | None = Field(description="email address of the user")
    designation: ProfileDesignationResponse = Field(description="designation details of the profile user")
    skills: list[ProfileSkillResponse]
    experiences: list[ProfileExperienceResponse]
    educations: list[ProfileEducationResponse]
    personal_details: ProfilePersonalDetailsResponse | None
    profile_status: ResponseEnumData | None = Field(description="profile status/ job type of the user")

    class Config:
        schema_extra = {
            "example":
                {
                    "id": "954eba99-b1ec-4c1f-b5b1-3cc9db9e59e0",
                    "email": "developer.ixorasolution@gmail.com",
                    "designation": {
                        "designation": "Software Engineer",
                        "designation_id": 1,
                        "start_date": datetime.datetime.now(timezone.utc).date(),
                        "end_date": (datetime.datetime.now(timezone.utc) + timedelta(days=1)).date(),
                        "designation_status": {
                            "id": 1,
                            "name": "active"
                        }
                    },
                    "personal_details":
                        {
                            "name": "Chelsey Adams",
                            "date_of_birth": datetime.datetime.now(timezone.utc).date() - timedelta(days=10000),
                            "gender":
                                {
                                    "id": 1,
                                    "name": "female"
                                },
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
                            },
                            "certificate_files":
                                [
                                    {
                                        "file_name": "certificate.pdf",
                                        "url": "/files/1"
                                    }
                                ]
                        }
                    ],
                    "experiences": [
                        {
                            "experience_id": 1,
                            "company_name": "X Software",
                            "job_responsibility": "Backend Development",
                            "designation": {
                                "designation_id": 1,
                                "designation": "Software Developer"
                            },
                            "start_date": (datetime.datetime.now(timezone.utc) - timedelta(days=1000)).date(),
                            "end_date": (datetime.datetime.now(timezone.utc) - timedelta(days=500)).date(),
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
                            "start_date": (datetime.datetime.now(timezone.utc) - timedelta(days=500)).date(),
                            "end_date": (datetime.datetime.now(timezone.utc) - timedelta(days=200)).date(),
                            "status": {
                                "id": 1,
                                "name": "active"
                            }
                        }
                    ],
                    "educations": [
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
                    }
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


class ProfileBasicRequest(BaseModel):
    profile_id: PydanticObjectId | None = Field(None, description="profile id of the user for update")
    email: EmailStr | None = Field(None, description="Email address of the user")
    name: str | None = Field(None, max_length=20, description="name of the user")
    date_of_birth: date | None = Field(None, description="date of birth of the user")
    gender: GenderEnum|None = Field(None, description="gender of the user")
    mobile: str | None = Field(None, description="mobile number of the user")
    address: str | None = Field(None, max_length=255, description="address of the user")
    designation_id: int | None = Field(None, description="designation id of the given designation or user")
    experience_year: int | None = Field(None, description="experience year of the user")
    about: str | None = Field(None, max_length=256, description="description of the user")

    @validator("date_of_birth", always=True)
    def validate_date_of_birth(cls, value: date | None) -> date | None:
        if value is None:
            return value
        if abs(datetime.datetime.today().date() - value).days < 5844:
            raise ValueError("input a valid date of birth. you must be at least 15 years or 5844 days old.")
        return value

    @root_validator
    def any_of(cls, v: dict[str, Any]) -> dict[str, Any]:
        profile_id = v.pop('profile_id')
        if profile_id is None:
            email = v.pop('email')
            name = v.pop('name')
            designation_id = v.pop('designation_id')
            if email is None or name is None or designation_id is None:
                raise ValueError('You must provide email, name and designation for creating a profile')
            v["email"] = email
            v["name"] = name
            v["designation_id"] = designation_id
        else:
            email = v.pop('email')
            name = v.pop('name')
            # designation_id = v.pop('designation_id')
            if email is not None or name is not None:
                raise ValueError('You should not provide email, name for updating a profile')
            # v["designation_id"] = designation_id
        v["profile_id"] = profile_id

        return v


class ProfileBasicForAdminRequest(BaseModel):
    profile_id: PydanticObjectId | None = Field(description="profile id of the user for update")
    email: EmailStr | None = Field(None, description="Email address of the user")
    name: str | None = Field(None, max_length=20, min_length=2, description="name of the user")
    date_of_birth: date | None = Field(None, description="date of birth of the user")
    gender: GenderEnum | None = Field(None, description="gender of the user")
    mobile: str | None = Field(None, description="mobile number of the user")
    address: str | None = Field(None, max_length=255, description="address of the user")
    designation_id: int | None = Field(None, description="designation id of the given designation or user")
    experience_year: int | None = Field(None, description="experience of the user in years")
    profile_status: ProfileStatusEnum | None = Field(default=None, description="""profile status of the user
    
    full_time: 1, part_time: 2, delete: 3, inactive: 4
    """)
    designation_status: DesignationStatusEnum | None = Field(default=None,
                                                             description="""designation status of user
    active: 1, inactive: 2
    """)
    about: str | None = Field(None, max_length=256, description="description of the user")

    @validator("date_of_birth", always=True)
    def validate_date_of_birth(cls, value: date | None) -> date | None:
        if value is None:
            return value
        if abs(datetime.datetime.today().date() - value).days < 5844:
            raise ValueError("input a valid date of birth. you must be at least 15 years or 5844 days old.")
        return value

    @root_validator
    def any_of(cls, v: dict[str, Any]) -> dict[str, Any]:
        profile_id = v.pop('profile_id')
        if profile_id is None:
            email = v.pop('email')
            name = v.pop('name')
            designation_id = v.pop('designation_id')
            if v.get("about") is not None:
                raise ValueError('You should not provide the "about" while creating a new profile')
            if email is None or name is None or designation_id is None:
                raise ValueError('You must provide email, name and designation for creating a new profile')
            v["email"] = email
            v["name"] = name
            v["designation_id"] = designation_id
        else:
            email = v.pop('email')
            if email is not None:
                raise ValueError('You should not provide email for updating a profile')
            v["email"] = email
        v["profile_id"] = profile_id

        return v


class ProfileUpdateByAdmin(BaseModel):
    designation: list[DesignationDataCreate] | None = Field(default=None)
    name: str | None = Field(max_length=20, min_length=2, description="name of the user")
    date_of_birth: date | None = Field(description="date of birth of the user")
    gender: GenderEnum | None = Field(description="gender of the user")
    mobile: str | None = Field(description="mobile number of the user")
    address: str | None = Field(max_length=255, description="address of the user")
    designation_id: int | None = Field(ge=1, description="designation id of the given designation or user")
    experience_year: int | None = Field(description="experience of the user in years")
    profile_status: ProfileStatusEnum | None = Field(description="""profile status of the user

        full_time: 1, part_time: 2, delete: 3, inactive: 4
        """)
    designation_status: DesignationStatusEnum | None = Field(default=DesignationStatusEnum.active, description="""designation status of user
        active: 1, inactive: 2
        """)
    about: str | None = Field(max_length=256, description="description of the user")


class ProfileUpdateByUser(BaseModel):
    designation: list[DesignationDataCreate] | None = Field(default=None)
    name: str | None = Field(max_length=20, min_length=2, description="name of the user")
    date_of_birth: date | None = Field(description="date of birth of the user")
    gender: GenderEnum | None = Field(description="gender of the user")
    mobile: str | None = Field(description="mobile number of the user")
    address: str | None = Field(max_length=255, description="address of the user")
    designation_id: int | None = Field(ge=1, description="designation id of the given designation or user")
    about: str | None = Field(max_length=256, description="description of the user")


class ProfileView(BaseModel):
    id: PydanticObjectId = Field(alias='_id')
    profile_status: ProfileStatusEnum


class ProfileSkillView(BaseModel):
    id: PydanticObjectId = Field(alias='_id')
    skills: list[ProfileSkill]
    profile_status: ProfileStatusEnum


class ProfileDesignationView(BaseModel):
    id: PydanticObjectId = Field(alias='_id')
    designation: ProfileDesignation
    profile_status: ProfileStatusEnum


class ProfileDesignationExperiencesView(BaseModel):
    id: PydanticObjectId = Field(alias='_id')
    designation: ProfileDesignation | None = Field(default=None)
    experiences: list[ProfileExperience] | None = Field(default=None)
    profile_status: ProfileStatusEnum


class ProfileEducationView(BaseModel):
    id: PydanticObjectId = Field(alias='_id')
    educations: list[ProfileEducation]
    profile_status: ProfileStatusEnum


class ProfileExperienceView(BaseModel):
    id: PydanticObjectId = Field(alias='_id')
    experiences: list[ProfileExperience]
    profile_status: ProfileStatusEnum


class ProfileProfileDetailsView(BaseModel):
    id: PydanticObjectId = Field(alias='_id')
    personal_detail: ProfilePersonalDetails
    user_id: str
    profile_status: ProfileStatusEnum
