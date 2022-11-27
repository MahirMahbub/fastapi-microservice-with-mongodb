from beanie import Document, PydanticObjectId, Link
from pydantic import BaseModel

from skill_management.enums import ProfileStatusEnum
from skill_management.models.file import Files
from skill_management.schemas.designation import ProfileDesignation
from skill_management.schemas.education import ProfileEducation
from skill_management.schemas.experience import ProfileExperienceResponse, ProfileExperience
from skill_management.schemas.profile import ProfilePersonalDetails
from skill_management.schemas.skill import ProfileSkill


class Profile(Document):
    user_id: PydanticObjectId
    personal_detail: ProfilePersonalDetails
    profile_status: ProfileStatusEnum = ProfileStatusEnum.inactive
    designation: list[ProfileDesignation]
    skills: list[ProfileSkill]
    experiences: list[ProfileExperience]
    education:list[ProfileEducation]
    cv_files: list[Link[Files]]
