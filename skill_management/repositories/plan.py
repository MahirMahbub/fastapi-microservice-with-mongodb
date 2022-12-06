from skill_management.models.plan import Plans
from skill_management.repositories.base_repository import TableRepository


class PlanRepository(TableRepository):
    def __init__(self) -> None:
        super().__init__(entity_collection=Plans)
