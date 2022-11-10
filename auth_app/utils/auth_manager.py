import os
import re
from typing import Optional

from anyio import to_thread
from asyncer import asyncify
from beanie import PydanticObjectId
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, InvalidPasswordException
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import BeanieUserDatabase, ObjectIDIDMixin
from password_strength import PasswordPolicy
from auth_app.entities.user import User, get_user_db
from auth_app.schemas.user import UserCreate
from auth_app.utils.tasks import send_account_verify_email, send_account_reset_password_email


class UserManager(ObjectIDIDMixin, BaseUserManager[User, PydanticObjectId]):
    reset_password_token_secret = os.getenv("RESET_PASSWORD_TOKEN_SECRET_KEY")
    verification_token_secret = os.getenv("VERIFY_TOKEN_SECRET_KEY")

    policy = PasswordPolicy.from_names(
        strength=0.5  # need a password that scores at least 0.5 with its strength
    )

    async def validate_password(
            self,
            password: str,
            user: UserCreate | User,
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

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
            self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")
        await to_thread.run_sync(send_account_reset_password_email.delay, user.email, token)

    async def on_after_request_verify(
            self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")
        await to_thread.run_sync(send_account_verify_email.delay, user.email, token)


async def get_user_manager(user_db: BeanieUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


# cookies_transport = BearerTransport(cookie_max_age=3600)


def get_jwt_strategy() -> JWTStrategy:
    # print("get_jwt_strategy: ", config.Settings().VERIFY_TOKEN_SECRET_KEY)
    return JWTStrategy(secret=config.Settings().VERIFY_TOKEN_SECRET_KEY, lifetime_seconds=3600)


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

fastapi_users = FastAPIUsers[User, PydanticObjectId](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
current_verified_active_user = fastapi_users.current_user(active=True, verified=True)
