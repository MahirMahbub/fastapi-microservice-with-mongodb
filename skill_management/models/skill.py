from typing import List

from beanie import Document

from skill_management.enums import SkillTypeEnum, SkillCategoryEnum


class Skill(Document):
    id: int
    skill_name: str
    skill_type: SkillTypeEnum
    skill_categories: List[SkillCategoryEnum]
