from beanie import Document, Link
from pydantic import EmailStr, Field

from skill_management.enums import ProfileStatusEnum
from skill_management.models.file import Files
from skill_management.schemas.designation import ProfileDesignation
from skill_management.schemas.education import ProfileEducation
from skill_management.schemas.experience import ProfileExperience
from skill_management.schemas.profile import ProfilePersonalDetails
from skill_management.schemas.skill import ProfileSkill


class Profiles(Document):
    user_id: EmailStr
    personal_detail: ProfilePersonalDetails
    profile_status: ProfileStatusEnum = Field(default=ProfileStatusEnum.inactive)
    designation: list[ProfileDesignation]
    skills: list[ProfileSkill]
    experiences: list[ProfileExperience]
    education: list[ProfileEducation]
    cv_files: list[Link[Files]]

    class Settings:
        use_revision = True
        use_state_management = True
        validate_on_save = True
