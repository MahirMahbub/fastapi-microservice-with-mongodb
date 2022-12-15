from typing import List

from beanie import Document

from skill_management.enums import SkillTypeEnum, SkillCategoryEnum, StatusEnum


class Skills(Document):
    id: int
    skill_name: str
    skill_type: SkillTypeEnum
    skill_categories: list[SkillCategoryEnum]

    class Settings:
        use_revision = False

