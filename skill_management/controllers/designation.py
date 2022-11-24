from fastapi import APIRouter, Request, Depends, Path, Query, Body
from fastapi.responses import ORJSONResponse

from skill_management.schemas.base import ErrorMessage
from skill_management.schemas.designation import DesignationDataResponse, ProfileDesignationResponse, \
    DesignationCreateRequest
from skill_management.utils.auth_manager import JWTBearer
from skill_management.utils.logger import get_logger

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
async def get_designation_list(request: Request,  # type: ignore
                               designation_name: str | None = Query(default=None,
                                                                    description="input designation name as string",
                                                                    alias="designation-name"),
                               user_id: str = Depends(JWTBearer())):
    pass


@designation_router.post("profile/designations",  # type: ignore
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
async def create_designation(request: Request,  # type: ignore
                             designation: DesignationCreateRequest = Body(..., examples={
                                 "CREATE": {
                                     "summary": "Create Body",
                                     "description": "a example of body for create operation",
                                     "value":
                                         {
                                             "designation_id": 1,
                                             "start_date": "2019-08-24T14:15:22Z",
                                             "end_date": "2020-08-24T14:15:22Z",
                                         },
                                 },

                                 "UPDATE":
                                     {
                                         "summary": "Update Body",
                                         "description": "a example of body for update operation",
                                         "value":
                                             {
                                                 "designation_id": 1,
                                                 "start_date": "2019-08-24T14:15:22Z",
                                                 "end_date": "2020-12-24T14:15:22Z",
                                                 "status": 2
                                             },
                                     }

                             }, ),
                             user_id: str = Depends(JWTBearer())):
    """
    **Create:** Must provide all the data for creating a new designation.


    **Update:** For update purposes provide designation id. Other attributes are optional
    """
    pass
