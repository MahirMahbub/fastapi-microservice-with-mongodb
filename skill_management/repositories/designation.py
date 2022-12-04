from skill_management.models.designation import Designations
from skill_management.repositories.base_repository import TableRepository


class DesignationRepository(TableRepository):
    def __init__(self) -> None:
        super().__init__(entity_collection=Designations)
