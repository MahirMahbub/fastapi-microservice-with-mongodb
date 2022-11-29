from datetime import date

from beanie import Document, Link, Indexed
from pydantic import EmailStr, Field

from skill_management.enums import ProfileStatusEnum
from skill_management.models.file import Files
from skill_management.schemas.designation import ProfileDesignation
from skill_management.schemas.education import ProfileEducation
from skill_management.schemas.experience import ProfileExperience
from skill_management.schemas.profile import ProfilePersonalDetails
from skill_management.schemas.skill import ProfileSkill


class Profiles(Document):
    user_id: Indexed(EmailStr, unique=True)  # type: ignore
    personal_detail: ProfilePersonalDetails
    profile_status: ProfileStatusEnum = Field(default=ProfileStatusEnum.inactive)
    designation: ProfileDesignation
    skills: list[ProfileSkill]
    experiences: list[ProfileExperience]
    educations: list[ProfileEducation]
    cv_files: list[Link[Files]]

    class Settings:
        use_revision = True
        use_state_management = True
        validate_on_save = True
        bson_encoders = {
          date: str
        }
