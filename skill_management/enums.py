import enum


class PlanEnum(enum.IntEnum):
    course: int = 1
    exam: int = 2


class StatusEnum(enum.IntEnum):
    active: int = 1
    cancel: int = 2
    delete: int = 3


class SkillCategoryEnum(enum.IntEnum):
    frontend: int = 1
    backend: int = 2
    devops: int = 3
    qa: int = 4
    database: int = 5
    network: int = 6
    fullstack: int = 7


class SkillTypeEnum(enum.IntEnum):
    core_skill: int = 1
    soft_skill: int = 2


class DesignationStatusEnum(enum.IntEnum):
    active: int = 1
    inactive: int = 2


class GenderEnum(enum.IntEnum):
    male: int = 1
    female: int = 2
    others: int = 3


class FileTypeEnum(enum.IntEnum):
    picture: int = 1
    resume: int = 2
    letter: int = 3
    certificate: int = 4
