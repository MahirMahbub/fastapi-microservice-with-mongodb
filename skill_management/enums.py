import enum


class PlanEnum(enum.IntEnum):
    course: int = 1
    exam: int = 2


class StatusEnum(enum.IntEnum):
    active: int = 1
    cancel: int = 2
    delete: int = 3
