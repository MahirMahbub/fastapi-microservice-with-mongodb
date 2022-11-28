import uuid
from datetime import datetime, timezone, timedelta
from uuid import UUID

from fastapi import Query, Depends, APIRouter, Path, Body
from fastapi.responses import ORJSONResponse
from starlette.requests import Request

from skill_management.schemas.base import ErrorMessage
from skill_management.schemas.profile import ProfileResponse, PaginatedProfileResponse, ProfileBasicRequest, \
    ProfileBasicForAdminRequest
from skill_management.services.profile import ProfileService
from skill_management.utils.auth_manager import JWTBearerAdmin, JWTBearer
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
async def get_user_profile_by_id_for_admin(request: Request,  # type: ignore
                                           profile_id: UUID = Path(...,
                                                                   description="input profile id of the user",
                                                                   alias="profile-id"),
                                           profile_status: int | None = Query(..., ge=1, le=2, alias="profile-status"),
                                           admin_user_id: str = Depends(JWTBearerAdmin())):
    pass


# ProfileBasicRequest
@profile_router.post("/user-profiles/",
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
                                      user_id: str = Depends(JWTBearer())):
    """
    **Create:** Must provide *"email"*, *"name"*, *"designation_id"* except *"profile_id"*. Other attributes are optional.


    **Update:** Must provide *"profile_id"*. Should not provide *"email"*, *"name"*, *"designation_id"*. Other attributes are optional.
    """
    pass


@profile_router.post("/admin/user-profiles/",
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
async def create_user_profile_by_admin(request: Request,  # type: ignore
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
                                                                   timezone.utc).date() - timedelta(days=10000),
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
                                                                   timezone.utc).date() - timedelta(days=10000),
                                                               "gender": 2,
                                                               "mobile": "+01611123456",
                                                               "address": "House: X, State:Y, Z, Country",
                                                               "designation_id": 1,
                                                               "profile_status": 1,
                                                               "designation_status": 1
                                                           }
                                                   }

                                           },

                                           description="input profile data"),
                                       service: ProfileService = Depends(),
                                       # admin_user_id: str = Depends(JWTBearerAdmin())
                                       ):
    """
    **Create:** Must provide *"email"*, *"name"*, *"designation_id"* except *"profile_id"*. Other attributes are optional.


    **Update:** Must provide *"profile_id"*. Should not provide *"email"*. Other attributes are optional.
    """
    return await service.create_user_profile_by_admin(profile)
    # pass
