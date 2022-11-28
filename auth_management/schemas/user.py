from beanie import PydanticObjectId
from fastapi_users import schemas
from fastapi_users.schemas import CreateUpdateDictModel
from pydantic import EmailStr


class UserRead(schemas.BaseUser[PydanticObjectId]):
    class Config:
        schema_extra = {
            "example": {
                "id": "<uuid id>",
                "email": "developer.ixorasolution@gmail.com",
                # "password": "<provided password>",
                "is_active": True,
                "is_superuser": False,
                "is_verified": False
            }
        }


class UserReadVerify(CreateUpdateDictModel):
    email: EmailStr
    is_active: bool
    is_superuser: bool
    is_verified: bool

    class Config:
        schema_extra = {
            "example": {
                # "id": "<uuid id>",
                "email": "developer.ixorasolution@gmail.com",
                # "password": "<provided password>",
                "is_active": True,
                "is_superuser": False,
                "is_verified": False
            }
        }


class UserCreate(CreateUpdateDictModel):
    email: EmailStr
    password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "developer.ixorasolution@gmail.com",
                "password": "<provided password>"
            }
        }


class UserUpdate(schemas.BaseUserUpdate):
    # pass
    class Config:
        schema_extra = {
            "example": {
                "email": "developer.ixorasolution@gmail.com",
                "password": "<provided password>"
            }
        }
