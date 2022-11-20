import os
import time
from logging import Logger
from typing import Any
import jwt
# from jose import jwt
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from skill_management.utils.logger import get_logger

JWT_SECRET = os.getenv("VERIFY_TOKEN_SECRET_KEY")
JWT_ALGORITHM = os.getenv("ENCRYPTION_ALGORITHM")
logger: Logger = get_logger()


def decode_jwt(token: str) -> dict[str, Any]:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], audience='fastapi-users:auth')

        return decoded_token if decoded_token["exp"] >= time.time() else None
    except Exception as e:
        raise e


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = decode_jwt(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True
        return isTokenValid
