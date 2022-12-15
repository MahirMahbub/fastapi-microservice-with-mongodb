from typing import cast

from beanie import PydanticObjectId
from beanie.odm.operators.find.array import ElemMatch
from fastapi import HTTPException, status

from skill_management.enums import StatusEnum, ProfileStatusEnum
from skill_management.models.profile import Profiles
from skill_management.repositories.profile import ProfileRepository
from skill_management.schemas.base import ResponseEnumData
from skill_management.schemas.education import EducationCreateRequest, EducationCreateResponse, ProfileEducation, \
    EducationListDataResponse, EducationCreateAdminRequest, ProfileEducationResponse, ProfileEducationDetailsResponse
from skill_management.schemas.profile import ProfileEducationView


class EducationService:
    async def create_or_update_education_by_user(self, education_request: EducationCreateRequest,
                                                 email: str | None) -> EducationListDataResponse:
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Authentication failed")
        if education_request.education_id is not None:
            """
            It is an update operation
            """
            return await self._update_education_by_user(education_request, email)
        else:
            """
            It is a create operation
            """
            return await self._create_education_by_user(education_request, email)

    async def create_or_update_education_by_admin(self,
                                                  education_request: EducationCreateAdminRequest) -> EducationListDataResponse:

        if education_request.education_id is not None:
            """
            It is an update operation
            """
            return await self._update_education_by_admin(education_request)
        else:
            """
            It is a create operation
            """
            return await self._create_education_by_admin(education_request)

    async def _update_education_by_user(self, education_request: EducationCreateRequest,
                                        email: str) -> EducationListDataResponse:
        profile_crud_manager = ProfileRepository()
        profile_educations = cast(
            ProfileEducationView,
            await profile_crud_manager.get_by_query(
                query={
                    "user_id": email
                },
                projection_model=ProfileEducationView
            )
        )
        if profile_educations is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="You are not allowed to update the user profile")

        if not profile_educations.profile_status in [
            ProfileStatusEnum.full_time,
            ProfileStatusEnum.part_time
        ]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="You can only update education for profile that is active.")
        has_education = await Profiles.find(
            {
                "user_id": email
            },
            ElemMatch(
                Profiles.educations,
                {
                    "education_id": education_request.education_id
                }
            ),
            projection_model=ProfileEducationView).first_or_none()
        if has_education is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Must provide a valid education id to update")
        education_request_dict = education_request.dict()
        education_request_dict.pop("education_id")
        education_status = education_request_dict.pop("status")
        education_object=None
        for edu in profile_educations.educations:
            if edu.education_id == education_request.education_id:
                education_object = edu
                break

        if education_status is not None:
            education_request_dict["status"] = cast(StatusEnum, education_request.status)
        else:
            education_request_dict["status"] = education_object.status

        education_request_dict = {
            "educations.$." + str(key): val for key, val in education_request_dict.items() if val is not None
        }
        db_profile: Profiles = await profile_crud_manager.update_by_query(  # type: ignore
            query={
                "educations.education_id": education_request.education_id,
                "_id": profile_educations.id
            },
            item_dict=education_request_dict
        )
        return EducationListDataResponse(
            educations=[
                EducationCreateResponse(
                    education_id=education.education_id,
                    degree_name=education.degree_name,
                    school_name=education.school_name,
                    passing_year=education.passing_year,
                    grade=education.grade,
                    status=ResponseEnumData(
                        id=education.status,
                        name=StatusEnum(education.status).name
                    ),
                )
                for education in db_profile.educations if education.status==StatusEnum.active
            ]
        )

    async def _create_education_by_user(self, education_request: EducationCreateRequest,
                                        email: str) -> EducationListDataResponse:
        profile_crud_manager = ProfileRepository()
        profile_educations = cast(
            ProfileEducationView,
            await profile_crud_manager.get_by_query(
                query={
                    "user_id": email
                },
                projection_model=ProfileEducationView
            )
        )
        if profile_educations is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="You are not allowed to update the user profile")

        if not profile_educations.profile_status in [
            ProfileStatusEnum.full_time,
            ProfileStatusEnum.part_time
        ]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="You can only update education for profile that is active.")

        all_education_ids = [
            education.education_id for education in profile_educations.educations
        ]
        if not all_education_ids:
            new_education_id = 1

        else:
            """
            Calculate new experience id
            """
            new_education_id = max(all_education_ids) + 1
        new_education = ProfileEducation(
            education_id=new_education_id,
            degree_name=education_request.degree_name,
            grade=education_request.grade,
            passing_year=education_request.passing_year,
            school_name=education_request.school_name,
            status=cast(StatusEnum,
                        education_request.status) if education_request.status is not None else StatusEnum.active
        )
        db_profile: Profiles = cast(Profiles, await profile_crud_manager.update_by_query(
            query={
                "_id": profile_educations.id
            },
            push_item={
                "educations": new_education.dict()
            }
        )
                                    )
        return EducationListDataResponse(
            educations=[
                EducationCreateResponse(
                    education_id=education.education_id,
                    degree_name=education.degree_name,
                    school_name=education.school_name,
                    passing_year=education.passing_year,
                    grade=education.grade,
                    status=ResponseEnumData(
                        id=education.status,
                        name=StatusEnum(education.status).name
                    )
                )
                for education in db_profile.educations if education.status==StatusEnum.active
            ]
        )

    async def _update_education_by_admin(self,
                                         education_request: EducationCreateAdminRequest) -> EducationListDataResponse:
        profile_crud_manager = ProfileRepository()
        profile_educations = cast(
            ProfileEducationView,
            await profile_crud_manager.get_by_query(
                query={
                    "_id": education_request.profile_id
                },
                projection_model=ProfileEducationView
            )
        )
        if profile_educations is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="You are not allowed to update the user profile")

        if not profile_educations.profile_status in [
            ProfileStatusEnum.full_time,
            ProfileStatusEnum.part_time
        ]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="You can only update education for profile that is active.")

        has_education = await Profiles.find(
            {
                "_id": education_request.profile_id
            },
            ElemMatch(
                Profiles.educations, {
                    "education_id": education_request.education_id
                }
            ),
            projection_model=ProfileEducationView
        ).first_or_none()
        if has_education is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Must provide a valid education id to update")

        education_request_dict = education_request.dict()
        education_request_dict.pop("education_id")
        education_status = education_request_dict.pop("status")
        education_request_dict.pop("profile_id")

        education_request_dict = {
            "educations.$." + str(key): val for key, val in education_request_dict.items() if val is not None
        }

        education_object=None
        for edu in profile_educations.educations:
            if edu.education_id == education_request.education_id:
                education_object = edu
                break

        if education_status is not None:
            education_request_dict["status"] = cast(StatusEnum, education_request.status)
        else:
            education_request_dict["status"] = education_object.status

        db_profile: Profiles = await profile_crud_manager.update_by_query(
            query={
                "educations.education_id": education_request.education_id,
                "_id": profile_educations.id
            },
            item_dict=education_request_dict
        )
        return EducationListDataResponse(
            educations=[
                EducationCreateResponse(
                    education_id=education.education_id,
                    degree_name=education.degree_name,
                    school_name=education.school_name,
                    passing_year=education.passing_year,
                    grade=education.grade,
                    status=ResponseEnumData(id=education.status,
                                            name=StatusEnum(education.status).name),
                )
                for education in db_profile.educations if education.status in [StatusEnum.active, StatusEnum.cancel]
            ]
        )

    async def _create_education_by_admin(self,
                                         education_request: EducationCreateAdminRequest) -> EducationListDataResponse:
        profile_crud_manager = ProfileRepository()
        profile_educations = cast(
            ProfileEducationView,
            await profile_crud_manager.get_by_query(
                query={
                    "_id": education_request.profile_id
                },
                projection_model=ProfileEducationView
            )
        )
        if profile_educations is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="You are not allowed to update the user profile")

        if not profile_educations.profile_status in [
            ProfileStatusEnum.full_time,
            ProfileStatusEnum.part_time
        ]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="You can only update education for profile that is active.")

        all_education_ids = [
            education.education_id for education in profile_educations.educations
        ]
        if not all_education_ids:
            new_education_id = 1

        else:
            """
            Calculate new experience id
            """
            new_education_id = max(all_education_ids) + 1
        new_education = ProfileEducation(
            education_id=new_education_id,
            degree_name=education_request.degree_name,
            grade=education_request.grade,
            passing_year=education_request.passing_year,
            school_name=education_request.school_name,
            status=education_request.status if education_request.status is not None else StatusEnum.active
        )
        db_profile: Profiles = cast(Profiles, await profile_crud_manager.update_by_query(
            query={
                "_id": profile_educations.id
            },
            push_item={
                "educations": new_education.dict()
            }
        )
                                    )
        return EducationListDataResponse(
            educations=[
                EducationCreateResponse(
                    education_id=education.education_id,
                    degree_name=education.degree_name,
                    school_name=education.school_name,
                    passing_year=education.passing_year,
                    grade=education.grade,
                    status=ResponseEnumData(id=education.status,
                                            name=StatusEnum(education.status).name),
                )
                for education in db_profile.educations if education.status in [StatusEnum.active, StatusEnum.cancel]
            ]
        )

    async def get_education_details_by_admin(self, profile_id: PydanticObjectId) -> ProfileEducationDetailsResponse:
        query = {
            '_id': profile_id,
        }
        db_profiles: ProfileEducationView = cast(ProfileEducationView, await Profiles.find(
            query,
            projection_model=ProfileEducationView
        ).first_or_none())
        if db_profiles is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Must provide a valid profile id")

        return ProfileEducationDetailsResponse(
            educations=[
                ProfileEducationResponse(
                    degree_name=data.degree_name,
                    school_name=data.school_name,
                    passing_year=data.passing_year,
                    grade=data.grade,
                    education_id=data.education_id,
                    status=ResponseEnumData(
                        id=data.status,
                        name=StatusEnum(data.status).name
                    )
                ) for data in db_profiles.educations if data.status in [StatusEnum.active, StatusEnum.cancel]]
        )

    async def get_education_details_by_user(self, email: str) -> ProfileEducationDetailsResponse:
        query = {
            'user_id': email,
        }
        db_profiles: ProfileEducationView = cast(
            ProfileEducationView, await Profiles.find(
                query,
                projection_model=ProfileEducationView
            ).first_or_none())
        if db_profiles is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Must provide a valid profile id"
            )
        if db_profiles.profile_status in [ProfileStatusEnum.inactive, ProfileStatusEnum.delete]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Must be an active profile"
            )
        return ProfileEducationDetailsResponse(
            educations=[
                ProfileEducationResponse(
                    degree_name=data.degree_name,
                    school_name=data.school_name,
                    passing_year=data.passing_year,
                    grade=data.grade,
                    education_id=data.education_id,
                    status=ResponseEnumData(
                        id=data.status,
                        name=StatusEnum(data.status).name
                    )
                ) for data in db_profiles.educations if data.status == StatusEnum.active
            ]
        )
