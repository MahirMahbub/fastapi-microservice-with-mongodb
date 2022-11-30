import os
import re
from logging import Logger
from typing import Optional, Any

from anyio import to_thread
from asyncer import asyncify
from beanie import PydanticObjectId
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, InvalidPasswordException, schemas, models
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import BeanieUserDatabase, ObjectIDIDMixin
from fastapi_users.models import UserProtocol
from password_strength import PasswordPolicy

from auth_management.entities.user import User, get_user_db
from auth_management.schemas.user import UserCreate
from auth_management.utils.logger import get_logger
from auth_management.utils.tasks import send_account_verify_email, send_account_reset_password_email

logger: Logger = get_logger()


class UserManager(ObjectIDIDMixin, BaseUserManager[User, PydanticObjectId]):
    reset_password_token_secret: str = str(os.getenv("RESET_PASSWORD_TOKEN_SECRET_KEY"))
    verification_token_secret: str = str(os.getenv("VERIFY_TOKEN_SECRET_KEY"))

    policy = PasswordPolicy.from_names(
        strength=0.5  # need a password that scores at least 0.5 with its strength
    )

    async def validate_password(
            self,
            password: str,
            user: UserCreate | User | schemas.UC | models.UP,
    ) -> None:
        if len(password) < 8:
            raise InvalidPasswordException(
                reason="Password should be at least 8 characters"
            )
        if user.email in password:
            raise InvalidPasswordException(
                reason="Password should not contain e-mail"
            )
        if await asyncify(re.search)(r"\d", password) is None:
            raise InvalidPasswordException(
                reason="Password should contain at least one number"
            )
        if await asyncify(re.search)(r"[A-Z]", password) is None:
            raise InvalidPasswordException(
                reason="Password should contain at least uppercase letter"
            )
        if await asyncify(re.search)(r"[a-z]", password) is None is None:
            raise InvalidPasswordException(
                reason="Password should contain at least lowercase letter"
            )

    async def on_after_register(self, user: User, request: Optional[Request] = None) -> None:
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
            self, user: User, token: str, request: Optional[Request] = None
    ) -> None:
        logger.info(f"User {user.id} has forgot their password. Reset token: {token}")
        await to_thread.run_sync(send_account_reset_password_email.delay, user.email, token)

    async def on_after_request_verify(
            self, user: User, token: str, request: Optional[Request] = None
    ) -> None:
        print(f"Verification requested for user {user.id}. Verification token: {token}")
        await to_thread.run_sync(send_account_verify_email.delay, user.email, token)

    async def on_after_login(
            self, user: models.UP, request: Optional[Request] = None
    ) -> None:
        await request.app.state.redis_connection.hset(name=str(user.id), mapping={  # type: ignore
            "email": user.email,
            "is_admin": 1 if user.is_superuser else 0,
            "is_verified": 1 if user.is_verified else 0
        })
        await request.app.state.redis_connection.expire(name=str(user.id),  # type: ignore
                                                        time=int(os.getenv("JWT_LIFETIME", default=3600)))


async def get_user_manager(user_db: BeanieUserDatabase = Depends(get_user_db)) -> bool:  # type: ignore
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


# cookies_transport = BearerTransport(cookie_max_age=3600)


def get_jwt_strategy() -> JWTStrategy[UserProtocol[Any], None]:
    # print("get_jwt_strategy: ", config.Settings().VERIFY_TOKEN_SECRET_KEY)
    return JWTStrategy(secret=str(os.getenv("VERIFY_TOKEN_SECRET_KEY")),
                       lifetime_seconds=int(os.getenv("JWT_LIFETIME", default=3600)))


# def get_database_strategy(
#     access_token_db: AccessTokenDatabase[AccessToken] = Depends(get_access_token_db),
# ) -> DatabaseStrategy:
#     return DatabaseStrategy(access_token_db, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
# auth_backend = AuthenticationBackend(
#     name="jwt",
#     transport=cookies_transport,
#     get_strategy=get_jwt_strategy,
# )

fastapi_users = FastAPIUsers[User, PydanticObjectId](get_user_manager=get_user_manager,  # type: ignore
                                                     auth_backends=[auth_backend])

current_active_user = fastapi_users.current_user(active=True)
current_verified_active_user = fastapi_users.current_user(active=True, verified=True)
