from skill_management.models.skill import Skills
from skill_management.repositories.base_repository import TableRepository


class SkillRepository(TableRepository):
    def __init__(self) -> None:
        super().__init__(entity_collection=Skills)