from skill_management.models.profile import Profiles
from skill_management.repositories.base_repository import TableRepository


class ProfileRepository(TableRepository):
    def __init__(self) -> None:
        super().__init__(entity_collection=Profiles)
