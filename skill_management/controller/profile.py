from uuid import UUID

from fastapi import Query, Depends, APIRouter, Path
from pydantic import EmailStr
from starlette.requests import Request

from skill_management.schemas.base import ErrorMessage
from skill_management.schemas.profile import ProfileResponse, ProfileBasicResponse
from skill_management.utils.auth_manager import JWTBearerAdmin
from skill_management.utils.logger import get_logger

profile_router: APIRouter = APIRouter(tags=["profile"])
logger = get_logger()


@profile_router.get("/admin/user-profiles",
                    response_model=ProfileBasicResponse,
                    status_code=200,
                    responses={
                        400: {
                            "model": ErrorMessage,
                            "description": "The profile basic details is not available"
                        },
                        200: {
                            "description": "The profile basic details is requested",
                        },
                    }
                    )
async def get_user_profiles_for_admin(request: Request,  # type: ignore
                                      skill_category: str | None = Query(default=None,
                                                                         description="input skill_category as string"),
                                      skill_name: str | None = Query(default=None,
                                                                     description="input skill_name as string"),
                                      admin_user_id: str = Depends(JWTBearerAdmin())):
    pass


@profile_router.get("/admin/user-profiles/{profile_id}",
                    response_model=ProfileResponse,
                    status_code=200,
                    responses={
                        400: {
                            "model": ErrorMessage,
                            "description": "The profile details is not available"
                        },
                        200: {
                            "description": "The profile details is requested",
                        },
                    }
                    )
async def get_user_profile_by_email_for_admin(request: Request,  # type: ignore
                                              profile_id: UUID = Path(...,
                                                                     description="input profile id of the user"),
                                              admin_user_id: str = Depends(JWTBearerAdmin())):
    pass
