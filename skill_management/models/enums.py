from beanie import Document
from pydantic import BaseModel


class EnumInitializer(Document):
    is_uploaded: bool = False


class EnumType(BaseModel):
    id: int
    name: str


class PlanType(EnumType, Document):
    pass


class Status(EnumType, Document):
    pass


class UserStatus(EnumType, Document):
    pass


class SkillCategory(EnumType, Document):
    pass


class SkillType(EnumType, Document):
    pass


class DesignationStatus(EnumType, Document):
    pass


class Gender(EnumType, Document):
    pass


class FileType(EnumType, Document):
    pass


class ProfileStatus(EnumType, Document):
    pass
