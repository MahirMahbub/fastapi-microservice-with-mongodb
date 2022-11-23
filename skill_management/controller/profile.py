from uuid import UUID

from fastapi import Query, Depends, APIRouter, Path
from fastapi.responses import ORJSONResponse
from starlette.requests import Request

from skill_management.enums import StatusEnum
from skill_management.schemas.base import ErrorMessage
from skill_management.schemas.profile import ProfileResponse, PaginatedProfileResponse
from skill_management.utils.auth_manager import JWTBearerAdmin
from skill_management.utils.logger import get_logger

profile_router: APIRouter = APIRouter(tags=["profile"])
logger = get_logger()


@profile_router.get("/admin/user-profiles",
                    response_class=ORJSONResponse,
                    response_model=PaginatedProfileResponse,
                    status_code=200,
                    responses={
                        404: {
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
                                                                         description="input skill category as string",
                                                                         alias="skill-category"),
                                      skill_name: str | None = Query(default=None,
                                                                     description="input skill name as string",
                                                                     alias="skill-name"),
                                      page_number: int = Query(default=1, description="page number of pagination",
                                                               gt=0,
                                                               alias="page-number"),
                                      page_size: int = Query(default=10, description="number of element in page", gt=0,
                                                             alias="page-size"),
                                      admin_user_id: str = Depends(JWTBearerAdmin())):
    pass


@profile_router.get("/admin/user-profiles/{profile-id}",
                    response_class=ORJSONResponse,
                    response_model=ProfileResponse,
                    status_code=200,
                    responses={
                        404: {
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
                                                                      description="input profile id of the user",
                                                                      alias="profile-id"),
                                              profile_status: int | None = Query(ge=1, le=2, alias="profile-status"),
                                              admin_user_id: str = Depends(JWTBearerAdmin())):
    pass
