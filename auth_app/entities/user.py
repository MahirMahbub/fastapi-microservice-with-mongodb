from beanie import Document, PydanticObjectId
from fastapi.security import HTTPBasicCredentials
from fastapi_users.db import BeanieBaseUser, BeanieUserDatabase
from pydantic import BaseModel, EmailStr, SecretStr


class User(BeanieBaseUser[PydanticObjectId]):
    pass


async def get_user_db():
    yield BeanieUserDatabase(User)
# class User(Document):
#     first_name: str
#     last_name: str
#     position: str
#     email: EmailStr
#     password: str
#
#     class Collection:
#         name = "user"
#
#     class Config:
#         schema_extra = {
#             "example": {
#                 "first_name": "John",
#                 "last_name": "Doe",
#                 "email": "john.dow@x.com",
#                 "password": "3xt3m#"
#             }
#         }
#
#
# class UserData(BaseModel):
#     first_name: str
#     last_name: str
#     email: EmailStr
#
#     class Config:
#         schema_extra = {
#             "example": {
#                 "first_name": "John",
#                 "last_name": "Doe",
#                 "email": "john.dow@x.com",
#             }
#         }
#
#
# class UserSignIn(HTTPBasicCredentials):
#     class Config:
#         schema_extra = {
#             "example": {
#                 "username": "abdul@youngest.dev",
#                 "password": "3xt3m#"
#             }
#         }
#
#
# class AdminData(BaseModel):
#     fullname: str
#     email: EmailStr
#
#     class Config:
#         schema_extra = {
#             "example": {
#                 "fullname": "Abdulazeez Abdulazeez Adeshina",
#                 "email": "abdul@youngest.dev",
#             }
#         }
