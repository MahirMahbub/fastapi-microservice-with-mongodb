import os
import time
from logging import Logger
from typing import Any

from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# import jwt
from jose import jwt, JWTError
from pydantic import validate_arguments

from skill_management.utils.logger import get_logger

JWT_SECRET = os.getenv("VERIFY_TOKEN_SECRET_KEY")
JWT_ALGORITHM = os.getenv("ENCRYPTION_ALGORITHM")
logger: Logger = get_logger()


class CredentialChecker(object):
    async def is_payload(self, payload: dict[str, Any] | None) -> bool:
        return payload is not None

    async def is_bearer(self, credentials: HTTPAuthorizationCredentials | None) -> bool:
        if credentials is None:
            return False
        return credentials.scheme.lower() == "bearer"


class DecodeToken(object):
    @staticmethod
    @validate_arguments
    async def decode_jwt(token: str) -> dict[str, Any]:
        try:
            decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], audience='fastapi-users:auth')
            """
            Write logic for checking is_active for user
            """

            return decoded_token if decoded_token["exp"] >= time.time() else None
        except JWTError as e:
            raise e

    @staticmethod
    @validate_arguments
    async def decode_jwt_admin(token: str) -> dict[str, Any]:
        try:
            decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], audience='fastapi-users:auth')
            """
            Write logic for checking is_admin and is_active for user
            """

            return decoded_token if decoded_token["exp"] >= time.time() else None
        except JWTError as e:
            raise e


class JWTBearer(HTTPBearer, CredentialChecker):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> str | None:  # type: ignore
        credentials: HTTPAuthorizationCredentials | None = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not await self.is_bearer(credentials):
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            payload: dict[str, Any] | None = await self.verify_jwt(credentials.credentials)
            if not await self.is_payload(payload):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            user_auth_data = await request.app.state.redis_connection.hgetall(payload["user_id"])
            if user_auth_data["is_verified"]=="0":
                raise HTTPException(status_code=403, detail="User is not verified.")
            return payload["user_id"]  # type: ignore
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    @staticmethod
    async def verify_jwt(jwt_token: str) -> dict[str, Any] | None:
        payload: dict[str, Any] | None
        try:
            payload = await DecodeToken.decode_jwt(jwt_token)
        except JWTError as e:
            payload = None
        return payload

class JWTBearerInactive(HTTPBearer, CredentialChecker):
    def __init__(self, auto_error: bool = True):
        super(JWTBearerInactive, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> str | None:  # type: ignore
        credentials: HTTPAuthorizationCredentials | None = await super(JWTBearerInactive, self).__call__(request)
        if credentials:
            if not await self.is_bearer(credentials):
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            payload: dict[str, Any] | None = await self.verify_jwt(credentials.credentials)
            if not await self.is_payload(payload):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return payload["user_id"]  # type: ignore
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    @staticmethod
    async def verify_jwt(jwt_token: str) -> dict[str, Any] | None:
        payload: dict[str, Any] | None
        try:
            payload = await DecodeToken.decode_jwt(jwt_token)
        except JWTError as e:
            payload = None
        return payload


class JWTBearerAdmin(HTTPBearer, CredentialChecker):
    def __init__(self, auto_error: bool = True):
        super(JWTBearerAdmin, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> str | None:  # type: ignore
        credentials: HTTPAuthorizationCredentials | None = await super(JWTBearerAdmin, self).__call__(request)
        if credentials:
            if not await self.is_bearer(credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            payload: dict[str, Any] | None = await self.verify_jwt(credentials.credentials)
            if not await self.is_payload(payload):
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            user_auth_data = await request.app.state.redis_connection.hgetall(payload["user_id"])
            if user_auth_data["is_admin"]=="0":
                raise HTTPException(status_code=403, detail="User is not admin.")
            return payload["user_id"]  # type: ignore
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    @staticmethod
    async def verify_jwt(jwt_token: str) -> dict[str, Any] | None:
        payload: dict[str, Any] | None
        try:
            payload = await DecodeToken.decode_jwt_admin(jwt_token)
        except JWTError as e:
            payload = None
        return payload
