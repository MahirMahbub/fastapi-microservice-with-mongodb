from typing import List

from beanie import Document

from skill_management.enums import SkillTypeEnum, SkillCategoryEnum


class Skills(Document):
    id: int
    skill_name: str
    skill_type: SkillTypeEnum
    skill_categories: List[SkillCategoryEnum]

    class Settings:
        use_revision = False

