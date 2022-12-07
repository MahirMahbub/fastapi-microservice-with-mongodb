from skill_management.models.file import Files
from skill_management.repositories.base_repository import TableRepository


class FileRepository(TableRepository):
    def __init__(self) -> None:
        super().__init__(entity_collection=Files)
