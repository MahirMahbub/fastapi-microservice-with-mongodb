import os
import time
from logging import Logger
from typing import Any, Optional

from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# import jwt
from jose import jwt, JWTError
from pydantic import validate_arguments

from skill_management.utils.logger import get_logger

JWT_SECRET = os.getenv("VERIFY_TOKEN_SECRET_KEY")
JWT_ALGORITHM = os.getenv("ENCRYPTION_ALGORITHM")
logger: Logger = get_logger()


@validate_arguments
def decode_jwt(token: str) -> dict[str, Any]:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], audience='fastapi-users:auth')

        return decoded_token if decoded_token["exp"] >= time.time() else None
    except JWTError as e:
        raise e


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:  # type: ignore
        credentials: HTTPAuthorizationCredentials | None = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            payload: dict[str, Any] = self.verify_jwt(credentials.credentials)
            if not payload:
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return payload["user_id"]
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    @staticmethod
    def verify_jwt(jwt_token: str) ->Optional[dict[str, Any]]:
        try:
            payload = decode_jwt(jwt_token)
        except JWTError as e:
            payload = None
        return payload
