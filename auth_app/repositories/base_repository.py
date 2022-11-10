from typing import TypeVar, Generic, Optional

from beanie import PydanticObjectId, Document
from beanie.odm.operators.update.general import Set
from pydantic import BaseModel
from pymongo.results import DeleteResult

T = TypeVar('T')


class TableRepository:
    __slots__ = ["entity_collection"]
    entity: Generic[T] = None

    def __init__(self, entity_collection: Generic[T]):
        self.entity_collection: Generic[T] = entity_collection

    async def insert(self, item: BaseModel) -> Document:
        item_dict: dict = item.dict(exclude_unset=True)
        data_object = await self.entity_collection(**item_dict)
        return await data_object.insert()

    async def get(self, id_: int | PydanticObjectId) -> Document | None:
        return await self.entity_collection.get(id_)

    async def gets(self) -> list[Document | None]:
        return await self.entity_collection.find().to_list()

    async def get_paginated(self, page_size: int = 10, page_number: int = 1) -> list[Document | None]:
        skips = page_size * (page_number - 1)
        return self.entity_collection.find().skip(skips).limit(page_size).to_list()

    async def delete(self, id_: int | PydanticObjectId) -> Optional[DeleteResult]:
        return await self.entity_collection.get(id_).delete()

    async def update(self, id_: int | PydanticObjectId, item: BaseModel):
        item_dict = item.dict(exclude_unset=True)
        return self.entity_collection.get(id_).update(Set(item_dict))

    async def upsert(self, id_: int | PydanticObjectId, item: BaseModel):
        item_dict = item.dict(exclude_unset=True)
        return self.entity_collection.get(id_).upsert(Set(item_dict), on_insert=self.entity_collection(**item_dict))
