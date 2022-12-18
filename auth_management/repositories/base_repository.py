from typing import Optional, Type, Any, Sequence

from beanie import PydanticObjectId, Document
from beanie.odm.operators.update.general import Set
from beanie.odm.queries.find import FindMany
from beanie.odm.queries.update import UpdateMany
from pydantic import BaseModel
from pymongo.results import DeleteResult


# T = TypeVar('T', bound=Type[Document])


class TableRepository:
    __slots__ = ["entity_collection"]

    # entity: Generic[T] | None = None

    def __init__(self, entity_collection: Type[Document]):
        self.entity_collection: Type[Document] = entity_collection

    async def insert(self, item: BaseModel) -> Document:
        item_dict: dict[str, Any] = item.dict(exclude_unset=True)
        data_object = self.entity_collection(**item_dict)
        return await data_object.insert()

    async def get(self, id_: str) -> Document | None:
        return await self.entity_collection.get(PydanticObjectId(id_))

    async def gets(self) -> Sequence[Document | None]:
        return await self.entity_collection.find().to_list()

    async def get_paginated(self, page_size: int = 10, page_number: int = 1) -> Sequence[Document | None]:
        skips = page_size * (page_number - 1)
        return await self.entity_collection.find().skip(skips).limit(page_size).to_list()

    async def delete(self, id_: PydanticObjectId) -> Optional[DeleteResult]:
        document_object: Document | None = await self.entity_collection.get(id_)
        if document_object is None:
            return None
        return await document_object.delete()

    async def delete_by_query(self, attr: str, value: Any) -> DeleteResult | None:
        document_object: FindMany[Document] = self.entity_collection.find(
            getattr(self.entity_collection, attr) == value)
        if document_object is None:
            return None
        return await document_object.delete()

    async def update(self, id_: PydanticObjectId, item: BaseModel) -> Optional[Document]:
        item_dict = item.dict(exclude_unset=True)
        document_object: Document | None = await self.entity_collection.get(id_)
        if document_object is None:
            return None
        await document_object.update(Set(item_dict))
        return document_object

    async def update_by_query(self, attr: str, value: Any, item: BaseModel) -> Optional[UpdateMany]:
        item_dict = item.dict(exclude_unset=True)
        document_object = self.entity_collection.find(
            getattr(self.entity_collection, attr) == value)
        if document_object is None:
            return None
        return await document_object.update(Set(item_dict))

    async def upsert(self, attr: str, value: Any, item: BaseModel) -> UpdateMany:
        item_dict = item.dict(exclude_unset=True)
        return await self.entity_collection.find_one(
            getattr(self.entity_collection, attr) == value).upsert(Set(item_dict),
                                                                   on_insert=self.entity_collection(
                                                                       **item_dict))
