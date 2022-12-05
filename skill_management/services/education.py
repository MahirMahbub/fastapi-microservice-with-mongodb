from typing import cast

from beanie.odm.operators.find.array import ElemMatch
from fastapi import HTTPException, status

from skill_management.enums import StatusEnum
from skill_management.models.profile import Profiles
from skill_management.repositories.profile import ProfileRepository
from skill_management.schemas.education import EducationCreateRequest, EducationCreateResponse, ProfileEducation, \
    EducationListDataResponse
from skill_management.schemas.profile import ProfileEducationView


class EducationService:
    async def create_or_update_education_by_user(self, education_request: EducationCreateRequest,
                                                 email: str| None) -> EducationListDataResponse:
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
        has_education = await Profiles.find(
            {
                "user_id": email
            },
            ElemMatch(Profiles.educations, {"education_id": education_request.education_id}),
            projection_model=ProfileEducationView).first_or_none()
        if has_education is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Must provide a valid education id to update")
        education_request_dict = education_request.dict(exclude_unset=True, exclude_defaults=True)
        education_request_dict.pop("education_id")
        education_request_dict = {
            "educations.$." + str(key): val for key, val in education_request_dict.items()
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
                    grade=education.grade
                )
                for education in db_profile.educations
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
            status=cast(StatusEnum, education_request.status)
        )
        db_profile: Profiles = await profile_crud_manager.update_by_query(
            query={
                "_id": profile_educations.id
            },
            push_item={
                "educations": new_education.dict(
                    exclude_unset=True, exclude_none=True
                )
            }
        )
        return EducationListDataResponse(
            educations=[
                EducationCreateResponse(
                    education_id=education.education_id,
                    degree_name=education.degree_name,
                    school_name=education.school_name,
                    passing_year=education.passing_year,
                    grade=education.grade
                )
                for education in db_profile.educations
            ]
        )
