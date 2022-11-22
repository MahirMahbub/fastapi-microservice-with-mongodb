import math
from typing import Any

from beanie.odm.queries.find import FindMany
from pydantic import BaseModel


class Page(object):

    def __init__(self, items: list[BaseModel], page: int, page_size: int, total: int)-> None:
        self.items = items
        self.previous_page = None
        self.next_page = None
        self.has_previous = page > 1
        if self.has_previous:
            self.previous_page = page - 1
        previous_items = (page - 1) * page_size
        self.has_next = previous_items + len(items) < total
        if self.has_next:
            self.next_page = page + 1
        self.total = total
        self.pages = int(math.ceil(total / float(page_size)))


async def paginate(query: FindMany, page_number: int, page_size: int)-> Page:  # type: ignore
    if page_number <= 0:
        raise AttributeError('page needs to be >= 1')
    if page_size <= 0:
        raise AttributeError('page_size needs to be >= 1')
    total = await query.count()
    items = await query.skip((page_number - 1) * page_size).limit(page_size).to_list()
    return Page(items, page_number, page_size, total)