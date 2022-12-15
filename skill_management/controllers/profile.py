import uuid
from datetime import datetime, timezone, timedelta
from typing import cast

from beanie import PydanticObjectId
from fastapi import Query, Depends, APIRouter, Path, Body
from fastapi.responses import ORJSONResponse
from starlette.requests import Request

from skill_management.enums import ProfileStatusEnum
from skill_management.schemas.base import ErrorMessage
from skill_management.schemas.profile import ProfileResponse, PaginatedProfileResponse, ProfileBasicRequest, \
    ProfileBasicForAdminRequest, ProfileDetailsResponse
from skill_management.services.profile import ProfileService
from skill_management.utils.auth_manager import JWTBearerAdmin, JWTBearer, JWTBearerInactive
from skill_management.utils.logger import get_logger
from skill_management.utils.profile_manager import get_profile_email

profile_router: APIRouter = APIRouter(tags=["profile"])
logger = get_logger()


@profile_router.get("/admin/profiles/",
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
                                      skill_ids: list[int] | None = Query(default=None,
                                                                   description="input skill id as integer",
                                                                   alias="skill-id"),
                                      employee_name: str | None = Query(default=None,
                                                                        description="input employee name as string",
                                                                        alias="employee-name"),
                                      mobile: str | None = Query(default=None,
                                                                 description="input mobile as string",
                                                                 alias="mobile"),
                                      email: str | None = Query(default=None,
                                                                description="input email as string",
                                                                alias="email"),
                                      profile_status: ProfileStatusEnum | None = Query(default=None,
                                                                                       description="profile status as enum",
                                                                                       alias="profile-status"),
                                      page_number: int = Query(default=1, description="page number of pagination",
                                                               gt=0,
                                                               alias="page-number"),
                                      page_size: int = Query(default=10, description="number of element in page", gt=0,
                                                             alias="page-size"),
                                      admin_user_id: str = Depends(JWTBearerAdmin()),
                                      service: ProfileService = Depends(),
                                      ):
    return await service.get_user_profiles_for_admin(skill_ids=skill_ids,
                                                     employee_name=employee_name,
                                                     mobile=mobile,
                                                     email=email,
                                                     profile_status=profile_status,
                                                     page_number=page_number,
                                                     page_size=page_size)


@profile_router.get("/admin/user-profiles/{profile_id}",
                    response_class=ORJSONResponse,
                    response_model=ProfileDetailsResponse,
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
async def get_user_profile_by_id_for_admin(request: Request,  # type: ignore
                                           profile_id: PydanticObjectId = Path(...,
                                                                               description="input profile id of the user"),
                                           admin_user_id: str = Depends(JWTBearerAdmin()),
                                           service: ProfileService = Depends(),
                                           ):
    return await service.get_user_profile_by_admin(profile_id)


@profile_router.get("/profile/user-profiles/",
                    response_class=ORJSONResponse,
                    response_model=ProfileDetailsResponse,
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
async def get_user_profile_by_user(request: Request,  # type: ignore
                                   user_id: str = Depends(JWTBearer()),
                                   service: ProfileService = Depends(),
                                   ):
    email = await get_profile_email(request=request, user_id=user_id)
    return await service.get_user_profile_by_user(cast(str, email))


# ProfileBasicRequest
@profile_router.post("/profile/user-profiles/",
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
async def create_user_profile_by_user(request: Request,  # type: ignore
                                      profile: ProfileBasicRequest = Body(
                                          examples={
                                              "CREATE":
                                                  {
                                                      "summary": "Create Body",
                                                      "description": "a example of body for create operation",
                                                      "value":
                                                          {
                                                              "email": "developer.ixorasolution@gmail.com",
                                                              "name": "Chelsey Adams",
                                                              "date_of_birth": datetime.now(
                                                                  timezone.utc).date() - timedelta(days=10000),
                                                              "gender": 2,
                                                              "mobile": "+01611123456",
                                                              "address": "House: X, State:Y, Z, Country",
                                                              "designation_id": 1
                                                          }
                                                  },

                                              "UPDATE":
                                                  {
                                                      "summary": "Update Body",
                                                      "description": "a example of body for update operation",
                                                      "value":
                                                          {
                                                              "profile_id": uuid.uuid4(),
                                                              "date_of_birth": datetime.now(
                                                                  timezone.utc).date() - timedelta(days=10000),
                                                              "gender": 2,
                                                              "mobile": "+01611123456",
                                                              "address": "House: X, State:Y, Z, Country"
                                                          }
                                                  }

                                          },

                                          description="input profile data"),
                                      user_id: str = Depends(JWTBearerInactive()),
                                      service: ProfileService = Depends(),
                                      ):
    """
    **Create:** Must provide *"email"*, *"name"*, *"designation_id"* except *"profile_id"*. Other attributes are optional.


    **Update:** Must provide *"profile_id"*. Should not provide *"email"*, *"name"*, *"designation_id"*. Other attributes are optional.
    """
    email = await get_profile_email(request=request, user_id=user_id)

    return await service.create_or_update_user_profile_by_user(profile, email)


@profile_router.post("/admin/user-profiles/",
                     response_class=ORJSONResponse,
                     response_model=ProfileResponse,
                     status_code=200,
                     responses={
                         404: {
                             "model": ErrorMessage,
                             "description": "The profile details is not available"
                         },
                         400: {
                             "model": ErrorMessage,
                             "description": "The profile details is not available"
                         },
                         200: {
                             "description": "The profile details is requested",
                         },
                     }
                     )
async def create_or_update_user_profile_by_admin(  # type: ignore
        request: Request,
        profile: ProfileBasicForAdminRequest = Body(
            examples={
                "CREATE":
                    {
                        "summary": "Create Body",
                        "description": "An example of body for create operation",
                        "value":
                            {
                                "email": "developer.ixorasolution@gmail.com",
                                "name": "Chelsey Adams",
                                "date_of_birth": datetime.now(
                                    timezone.utc
                                ).date() - timedelta(
                                    days=10000
                                ),
                                "gender": 2,
                                "mobile": "+01611123456",
                                "address": "House: X, State:Y, Z, Country",
                                "designation_id": 1,
                                "profile_status": 1,
                                "designation_status": 1
                            }
                    },

                "UPDATE":
                    {
                        "summary": "Update Body",
                        "description": "An example of body for update operation",
                        "value":
                            {
                                "profile_id": uuid.uuid4(),
                                "name": "Chelsey Adams",
                                "date_of_birth": datetime.now(
                                    timezone.utc
                                ).date() - timedelta(
                                    days=10000
                                ),
                                "gender": 2,
                                "mobile": "+01611123456",
                                "address": "House: X, State:Y, Z, Country",
                                "designation_id": 1,
                                "profile_status": 1,
                                "designation_status": 1
                            }
                    }

            },

            description="input profile data"
        ),
        service: ProfileService = Depends(),
        admin_user_id: str = Depends(JWTBearerAdmin())
):
    """
    **Create:** Must provide *"email"*, *"name"*, *"designation_id"* except *"profile_id"*. Other attributes are optional.


    **Update:** Must provide *"profile_id"*. Should not provide *"email"*. Other attributes are optional.
    """
    return await service.create_or_update_user_profile_by_admin(profile)
