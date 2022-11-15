from fastapi import APIRouter

from auth_app.controller import test
from auth_app.schemas.user import UserRead, UserCreate, UserUpdate, UserReadVerify
from auth_app.utils.auth_manager import fastapi_users, auth_backend

api_router: APIRouter = APIRouter()
api_router.include_router(test.test_router)
api_router.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/jwt", tags=["auth"]
)
api_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),  # type: ignore
    tags=["auth"],
)
api_router.include_router(
    fastapi_users.get_reset_password_router(),
    tags=["auth"],
)
api_router.include_router(
    fastapi_users.get_verify_router(UserReadVerify),  # type: ignore
    tags=["auth"],
)
api_router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
