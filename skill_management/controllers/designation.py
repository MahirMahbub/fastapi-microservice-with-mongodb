import uuid
from typing import cast

from beanie import PydanticObjectId
from fastapi import APIRouter, Request, Depends, Path, Query, Body
from fastapi.responses import ORJSONResponse

from skill_management.schemas.base import ErrorMessage
from skill_management.schemas.designation import DesignationDataResponse, ProfileDesignationResponse, \
    DesignationCreateRequest, DesignationCreateAdminRequest, ProfileDesignationDetailsResponse
from skill_management.services.designation import DesignationService
from skill_management.utils.auth_manager import JWTBearer, JWTBearerAdmin
from skill_management.utils.logger import get_logger
from skill_management.utils.profile_manager import get_profile_email

designation_router: APIRouter = APIRouter(tags=["designation"])
logger = get_logger()


@designation_router.get("/designations/{designation-id}",
                        response_class=ORJSONResponse,
                        response_model=DesignationDataResponse,
                        status_code=200,
                        responses={
                            404: {
                                "model": ErrorMessage,
                                "description": "The designation details is not available"
                            },
                            200: {
                                "description": "The designation requested by id",
                            },
                        })
async def get_designation(request: Request,  # type: ignore
                          designation_id: int = Path(..., description="provide skill id to get skill information",
                                                     alias="designation-id"),
                          user_id: str = Depends(JWTBearer())):
    pass


@designation_router.get("/designations",
                        response_class=ORJSONResponse,
                        response_model=list[DesignationDataResponse],
                        status_code=200,
                        responses={
                            404: {
                                "model": ErrorMessage,
                                "description": "The designation list is not available"
                            },
                            200: {
                                "description": "The designation list requested",
                            },
                        }
                        )
async def get_designation_list(request: Request,
                               designation_name: str | None = Query(default=None,
                                                                    description="input designation name as string",
                                                                    alias="designation-name"),
                               user_id: str = Depends(JWTBearer()),
                               service: DesignationService = Depends()):
    return await service.get_master_designation_list(designation_name)


@designation_router.post("/profile/designations",
                         response_class=ORJSONResponse,
                         response_model=ProfileDesignationResponse,
                         status_code=201,
                         responses={
                             404: {
                                 "model": ErrorMessage,
                                 "description": "The designation is not created"
                             },
                             201: {
                                 "description": "The designation is created successfully",
                             },
                         }
                         )
async def create_or_update_designation(request: Request,  # type: ignore
                                       designation_request: DesignationCreateRequest = Body(..., examples={
                                           # "CREATE": {
                                           #     "summary": "Create Body",
                                           #     "description": "a example of body for create operation",
                                           #     "value":
                                           #         {
                                           #             "designation_id": 1,
                                           #             "start_date": "2019-08-24T14:15:22Z",
                                           #             "end_date": "2020-08-24T14:15:22Z",
                                           #         },
                                           # },

                                           "UPDATE":
                                               {
                                                   "summary": "Update Body",
                                                   "description": "a example of body for update operation",
                                                   "value":
                                                       {
                                                           "start_date": "2019-08-24T14:15:22Z",
                                                           "end_date": "2020-12-24T14:15:22Z",
                                                           # "status": 2
                                                       },
                                               }

                                       }, ),
                                       user_id: str = Depends(JWTBearer()),
                                       service: DesignationService = Depends()):
    """
    **Update:** For update purposes provide *"start_date"* and *"end_date"*.
    """
    email = await get_profile_email(user_id=user_id, request=request)
    return await service.update_designation_by_user(designation_request=designation_request,
                                                    email=cast(str, email))


@designation_router.post("/admin/profile/designations",
                         response_class=ORJSONResponse,
                         response_model=ProfileDesignationResponse,
                         status_code=201,
                         responses={
                             404: {
                                 "model": ErrorMessage,
                                 "description": "The designation is not created"
                             },
                             201: {
                                 "description": "The designation is created successfully",
                             },
                         }
                         )
async def update_designation_by_admin(request: Request,  # type: ignore
                                      designation_request: DesignationCreateAdminRequest = Body(..., examples={
                                          # "CREATE": {
                                          #     "summary": "Create Body",
                                          #     "description": "a example of body for create operation",
                                          #     "value":
                                          #         {
                                          #             "designation_id": 1,
                                          #             "start_date": "2019-08-24T14:15:22Z",
                                          #             "end_date": "2020-08-24T14:15:22Z",
                                          #         },
                                          # },

                                          "UPDATE":
                                              {
                                                  "summary": "Update Body",
                                                  "description": "a example of body for update operation",
                                                  "value":
                                                      {
                                                          "profile_id": uuid.uuid4(),
                                                          "start_date": "2019-08-24T14:15:22Z",
                                                          "end_date": "2020-12-24T14:15:22Z",
                                                          "designation_status": 2
                                                      },
                                              }

                                      }, ),
                                      admin_user_id: str = Depends(JWTBearerAdmin()),
                                      service: DesignationService = Depends()):
    """
    **Update:** For update purposes provide *"start_date"* and *"end_date"*.
    """
    return await service.update_designation_by_admin(designation_request=designation_request)


@designation_router.get("/profile/admin/user-profiles/{profile_id}/designation",
                        response_class=ORJSONResponse,
                        response_model=ProfileDesignationDetailsResponse,
                        status_code=200,
                        responses={
                            404: {
                                "model": ErrorMessage,
                                "description": "The designation details is not available"
                            },
                            200: {
                                "description": "The designation requested by profile id",
                            },
                        })
async def get_profile_designation_by_admin(request: Request,  # type: ignore
                                           user_id: str = Depends(JWTBearerAdmin()),
                                           profile_id: PydanticObjectId = Path(...,
                                                                               description="input profile id of the user",
                                                                               alias="profile_id"),
                                           service: DesignationService = Depends()):
    return await service.get_designation_details_by_admin(profile_id=profile_id)


@designation_router.get("/profile/user-profiles/designation",
                        response_class=ORJSONResponse,
                        response_model=ProfileDesignationDetailsResponse,
                        status_code=200,
                        responses={
                            404: {
                                "model": ErrorMessage,
                                "description": "The designation details is not available"
                            },
                            200: {
                                "description": "The designation requested by profile id",
                            },
                        })
async def get_profile_designation_by_user(request: Request,  # type: ignore
                                          user_id: str = Depends(JWTBearer()),
                                          service: DesignationService = Depends()):
    email = await get_profile_email(user_id=user_id, request=request)
    return await service.get_designation_details_by_user(email=email)
