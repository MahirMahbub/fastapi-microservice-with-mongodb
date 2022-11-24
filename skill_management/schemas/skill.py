from pydantic import BaseModel, Field, FilePath, validator

from skill_management.enums import StatusEnum, UserStatusEnum
from skill_management.schemas.base import ResponseEnumData


class SkillCreate(BaseModel):
    skill_id: int = Field(description="id of skill")


class SkillExtraDataBase(BaseModel):
    experience_year: int = Field(le=45, description="experience of the indicated skill")
    number_of_projects: int = Field(le=80, description="number of projects on that skill")
    level: int = Field(le=10, ge=1, description="level of proficiency on the skill")
    training_duration: int = Field(le=100, description="training duration in months")
    achievements: str = Field(max_length=1, description='''marker for having the achievements
    
    0 or 1''')
    achievements_description: str = Field(max_length=255, description="description of the achievement")
    certificate: str = Field(max_length=1, description='''marker for having the certificate
    
    0 or 1''')

    @validator("achievements", always=True)
    def validate_achievements(cls, value: str) -> str | None:
        try:
            ascii_value = ord(value)
        except TypeError as type_exec:
            raise ValueError("not a valid value, not a valid number marker")
        if ascii_value > 49 or ascii_value < 48:
            """
            Ascii_value of "0" is 48 and "1" is 49.
            """
            raise ValueError("not a valid value, out of ascii value range")
        return value

    @validator("certificate", always=True)
    def validate_certificate(cls, value: str) -> str | None:
        try:
            ascii_value = ord(value)
        except TypeError as type_exec:
            raise ValueError("not a valid value, not a valid number marker")
        if ascii_value > 49 or ascii_value < 48:
            """
            Ascii_value of "0" is 48 and "1" is 49.
            """
            raise ValueError("not a valid value, out of ascii value range")
        return value


class SkillDataCreate(SkillExtraDataBase, SkillCreate):
    file_location: FilePath = Field(description="location of the certificate file")
    status: str = Field(max_length=10, description="status of task")

    @validator("status", always=True)
    def validate_status(cls, value: str) -> str | None:
        if value not in [data.name for data in StatusEnum]:
            raise ValueError("status must be valid")
        return value


class CreateSkillDataRequest(SkillCreate):
    experience_year: int | None = Field(None, le=45, description="experience of the indicated skill")
    number_of_projects: int | None = Field(None, le=80, description="number of projects on that skill")
    level: int | None = Field(None, le=10, ge=1, description="level of proficiency on the skill")
    training_duration: int | None = Field(None, le=100, description="training duration in months")
    achievements: str | None = Field(None, max_length=1, description='''marker for having the achievements

    0 or 1''')
    achievements_description: str | None = Field(None, max_length=255, description="description of the achievement")
    certificate: str | None = Field(None, max_length=1, description='''marker for having the certificate

    0 or 1''')
    status: UserStatusEnum | None = Field(UserStatusEnum.active,
                                          description="""skill data validity status 

    1: active, 3: delete""")

    @validator("achievements", always=True)
    def validate_achievements(cls, value: str) -> str | None:
        try:
            ascii_value = ord(value)
        except TypeError as type_exec:
            raise ValueError("not a valid value, not a valid number marker")
        if ascii_value > 49 or ascii_value < 48:
            """
            Ascii_value of "0" is 48 and "1" is 49.
            """
            raise ValueError("not a valid value, out of ascii value range")
        return value

    @validator("certificate", always=True)
    def validate_certificate(cls, value: str) -> str | None:
        try:
            ascii_value = ord(value)
        except TypeError as type_exec:
            raise ValueError("not a valid value, not a valid number marker")
        if ascii_value > 49 or ascii_value < 48:
            """
            Ascii_value of "0" is 48 and "1" is 49.
            """
            raise ValueError("not a valid value, out of ascii value range")
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
                    "skill_id": 1,
                    "experience_year": 4,
                    "number_of_projects": 4,
                    "level": 5,
                    "training_duration": 2,
                    "achievements": "1",
                    "achievements_description": "It is the achievement's description",
                    "certificate": "1",
                    "status": 1
                }
        }


class CreateSkillDataResponse(BaseModel):
    skill_id: int | None = Field(description="id of skill")
    skill_type: ResponseEnumData | None = Field(description="type of skill from fixed list of values")
    skill_category: list[ResponseEnumData] | None = Field(max_items=7,
                                                          description="category of skill from fixed list of items")
    skill_name: str | None = Field(max_length=20, description="name of skill from fixed list of values")
    status: ResponseEnumData | None = Field(description="status of skill from fixed list of values")
    experience_year: int | None = Field(le=45, description="experience of the indicated skill")
    number_of_projects: int | None = Field(le=80, description="number of projects on that skill")
    level: int | None = Field(le=10, ge=1, description="level of proficiency on the skill")
    training_duration: int | None = Field(le=100, description="training duration in months")
    achievements: str | None = Field(max_length=1, description='''marker for having the achievements

    0 or 1''')
    achievements_description: str | None = Field(max_length=255, description="description of the achievement")
    certificate: str | None = Field(max_length=1, description='''marker for having the certificate

    0 or 1''')

    @validator("achievements", always=True)
    def validate_achievements(cls, value: str) -> str | None:
        try:
            ascii_value = ord(value)
        except TypeError as type_exec:
            raise ValueError("not a valid value, not a valid number marker")
        if ascii_value > 49 or ascii_value < 48:
            """
            Ascii_value of "0" is 48 and "1" is 49.
            """
            raise ValueError("not a valid value, out of ascii value range")
        return value

    @validator("certificate", always=True)
    def validate_certificate(cls, value: str) -> str | None:
        try:
            ascii_value = ord(value)
        except TypeError as type_exec:
            raise ValueError("not a valid value, not a valid number marker")
        if ascii_value > 49 or ascii_value < 48:
            """
            Ascii_value of "0" is 48 and "1" is 49.
            """
            raise ValueError("not a valid value, out of ascii value range")
        return value

    class Config:
        schema_extra = {
            "example":
                {
                    "skill_id": 1,
                    "skill_name": "react",
                    "skill_type":
                        {
                            "id": 1,
                            "name": "core_skill"
                        },
                    "skill_category":
                        [
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
                    "status":
                        {
                            "id": 1,
                            "name": "active"
                        }
                }
        }


class GetSkillDataResponse(BaseModel):
    skill_id: int | None = Field(description="id of skill")
    skill_type: ResponseEnumData | None = Field(description="type of skill from fixed list of values")
    skill_category: list[ResponseEnumData] | None = Field(max_items=7,
                                                          description="category of skill from fixed list of items")
    skill_name: str | None = Field(max_length=20, description="name of skill from fixed list of values")

    class Config:
        schema_extra = {
            "example":
                {
                    "id": 1,
                    "skill_name": "react",
                    "skill_type":
                        {
                            "id": 1,
                            "name": "core_skill"
                        }
                    ,
                    "skill_category":
                        [
                            {
                                "id": 1,
                                "name": "frontend"
                            },
                            {
                                "id": 2,
                                "name": "backend"
                            }
                        ]
                }
        }


class GetSkillDataResponseList(BaseModel):
    skills: list[GetSkillDataResponse]|None

    class Config:
        schema_extra = {
            "example":
                {
                    "skills": [
                        {
                            "id": 1,
                            "skill_name": "react",
                            "skill_type":
                                {
                                    "id": 1,
                                    "name": "core_skill"
                                }
                            ,
                            "skill_category":
                                [
                                    {
                                        "id": 1,
                                        "name": "frontend"
                                    },
                                    {
                                        "id": 2,
                                        "name": "backend"
                                    }
                                ]
                        },
                        {
                            "id": 2,
                            "skill_name": "django",
                            "skill_type":
                                {
                                    "id": 1,
                                    "name": "core_skill"
                                }
                            ,
                            "skill_category":
                                [
                                    {
                                        "id": 2,
                                        "name": "backend"
                                    }
                                ]
                        }
                    ]
                }
        }


class ProfileSkillDataResponse(BaseModel):
    skill_id: int | None = Field(description="id of skill")
    experience_year: int | None = Field(le=45, description="experience of the indicated skill")
    level: int | None = Field(le=10, ge=1, description="level of proficiency on the skill")
    skill_name: str | None = Field(max_length=20, description="name of skill from fixed list of values")

    class Config:
        schema_extra = {
            "example": {
                "experience_year": 4,
                "level": 6,
                "skill_name": "react",
                "skill_id": 1
            }
        }


class ProfileSkillResponse(BaseModel):
    skill_id: int | None = Field(description="id of skill")
    skill_type: ResponseEnumData | None = Field(description="type of skill from fixed list of values")
    skill_category: list[ResponseEnumData] | None = Field(max_items=7,
                                                          description="category of skill from fixed list of items")
    skill_name: str | None = Field(max_length=20, description="name of skill from fixed list of values")
    status: ResponseEnumData | None = Field(description="status of skill from fixed list of values")
    _filename_url: str | None = Field(max_length=255, description="file response api url of user profile picture")
    experience_year: int | None = Field(le=45, description="experience of the indicated skill")
    number_of_projects: int | None = Field(le=80, description="number of projects on that skill")
    level: int | None = Field(le=10, ge=1, description="level of proficiency on the skill")
    training_duration: int | None = Field(le=100, description="training duration in months")
    achievements: str | None = Field(max_length=1, description='''marker for having the achievements

    0 or 1''')
    achievements_description: str | None = Field(max_length=255, description="description of the achievement")
    certificate: str | None = Field(max_length=1, description='''marker for having the certificate

    0 or 1''')

    @validator("achievements", always=True)
    def validate_achievements(cls, value: str) -> str | None:
        try:
            ascii_value = ord(value)
        except TypeError as type_exec:
            raise ValueError("not a valid value, not a valid number marker")
        if ascii_value > 49 or ascii_value < 48:
            """
            Ascii_value of "0" is 48 and "1" is 49.
            """
            raise ValueError("not a valid value, out of ascii value range")
        return value

    @validator("certificate", always=True)
    def validate_certificate(cls, value: str) -> str | None:
        try:
            ascii_value = ord(value)
        except TypeError as type_exec:
            raise ValueError("not a valid value, not a valid number marker")
        if ascii_value > 49 or ascii_value < 48:
            """
            Ascii_value of "0" is 48 and "1" is 49.
            """
            raise ValueError("not a valid value, out of ascii value range")
        return value
