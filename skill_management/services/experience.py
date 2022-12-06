from typing import cast

from beanie.odm.operators.find.array import ElemMatch
from fastapi import HTTPException, status

from skill_management.enums import StatusEnum
from skill_management.models.profile import Profiles
from skill_management.repositories.profile import ProfileRepository
from skill_management.schemas.base import ResponseEnumData
from skill_management.schemas.education import EducationListDataResponse, ProfileEducation
from skill_management.schemas.experience import ExperienceCreateRequest, ExperienceListDataResponse, \
    ExperienceCreateAdminRequest, ExperienceCreateResponse, ProfileExperienceDesignationResponse, ProfileExperience, \
    ExperienceDesignation
from skill_management.schemas.profile import ProfileExperienceView


class ExperienceService:
    async def create_or_update_experience_by_user(self, experience_request: ExperienceCreateRequest,
                                                  email: str | None) -> ExperienceListDataResponse:
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Authentication failed")
        if experience_request.experience_id is not None:
            """
            It is an update operation
            """
            return await self._update_experience_by_user(experience_request, email)
        else:
            """
            It is a create operation
            """
            return await self._create_experience_by_user(experience_request, email)

    async def create_or_update_experience_by_admin(self,
                                                   experience_request: ExperienceCreateAdminRequest) -> ExperienceListDataResponse:

        if experience_request.experience_id is not None:
            """
            It is an update operation
            """
            return await self._update_experience_by_admin(experience_request)
        else:
            """
            It is a create operation
            """
            return await self._create_experience_by_admin(experience_request)

    async def _update_experience_by_user(self, experience_request: ExperienceCreateRequest,
                                         email: str) -> ExperienceListDataResponse:
        profile_crud_manager = ProfileRepository()
        profile_experiences = cast(
            ProfileExperienceView,
            await profile_crud_manager.get_by_query(
                query={
                    "user_id": email
                },
                projection_model=ProfileExperienceView
            )
        )
        if profile_experiences is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="You are not allowed to update the user profile")
        has_experience = await Profiles.find(
            {
                "user_id": email
            },
            ElemMatch(Profiles.experiences, {"experience_id": experience_request.experience_id}),
            projection_model=ProfileExperienceView).first_or_none()
        if has_experience is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Must provide a valid experience id to update")
        experience_request_dict = experience_request.dict(exclude_unset=True, exclude_defaults=True)
        experience_request_dict.pop("experience_id")
        experience_request_dict = {
            "experiences.$." + str(key): val for key, val in experience_request_dict.items()
        }
        db_profile: Profiles = await profile_crud_manager.update_by_query(  # type: ignore
            query={
                "experiences.experience_id": experience_request.experience_id,
                "_id": profile_experiences.id
            },
            item_dict=experience_request_dict
        )
        return ExperienceListDataResponse(
            experiences=[
                ExperienceCreateResponse(
                    experience_id=experience.experience_id,
                    company_name=experience.company_name,
                    job_responsibility=experience.job_responsibility,
                    designation=ProfileExperienceDesignationResponse(
                        designation=experience.designation.designation,
                        designation_id=experience.designation_id
                    ),
                    start_date=experience.start_date,
                    end_date=experience.end_date,
                    status=ResponseEnumData(id=experience.status,
                                            name=StatusEnum(experience.status).name)
                )
                for experience in db_profile.experiences
            ]
        )

    async def _create_experience_by_user(self, experience_request: ExperienceCreateRequest,
                                         email: str) -> ExperienceListDataResponse:
        profile_crud_manager = ProfileRepository()
        profile_experiences = cast(
            ProfileExperienceView,
            await profile_crud_manager.get_by_query(
                query={
                    "user_id": email
                },
                projection_model=ProfileExperienceView
            )
        )
        if profile_experiences is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="You are not allowed to update the user profile")

        all_experience_ids = [
            experience.experience_id for experience in profile_experiences.experiences
        ]
        if not all_experience_ids:
            new_experience_id = 1

        else:
            """
            Calculate new experience id
            """
            new_experience_id = max(all_experience_ids) + 1

        new_experience = ProfileExperience(
            experience_id=new_experience_id,
            designation_id=None,
            company_name=cast(str, experience_request.company_name),
            designation=ExperienceDesignation(
                designation=experience_request.designation,
                designation_id=None
            ),
            start_date=experience_request.start_date,
            end_date=experience_request.end_date,
            job_responsibility=experience_request.job_responsibility,
            status=cast(StatusEnum, experience_request.status)
        )
        db_profile: Profiles = cast(Profiles, await profile_crud_manager.update_by_query(
            query={
                "_id": profile_experiences.id
            },
            push_item={
                "experiences": new_experience.dict(
                    exclude_unset=True, exclude_none=True
                )
            }
        )
                                    )
        return ExperienceListDataResponse(
            experiences=[
                ExperienceCreateResponse(
                    experience_id=experience.experience_id,
                    company_name=experience.company_name,
                    job_responsibility=experience.job_responsibility,
                    designation=ProfileExperienceDesignationResponse(
                        designation=experience.designation.designation,
                        designation_id=experience.designation_id
                    ),
                    start_date=experience.start_date,
                    end_date=experience.end_date,
                    status=ResponseEnumData(id=experience.status,
                                            name=StatusEnum(experience.status).name)
                )
                for experience in db_profile.experiences
            ]
        )

    async def _update_experience_by_admin(self, experience_request: ExperienceCreateAdminRequest) -> ExperienceListDataResponse:
        profile_crud_manager = ProfileRepository()
        profile_experiences = await profile_crud_manager.get_by_query(
                query={
                    "_id": experience_request.profile_id
                },
                projection_model=ProfileExperienceView
            )
        if profile_experiences is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="You are not allowed to update the user profile")
        has_experience = await Profiles.find(
            {
                "_id": experience_request.profile_id
            },
            ElemMatch(Profiles.experiences, {"experience_id": experience_request.experience_id}),
            projection_model=ProfileExperienceView).first_or_none()
        if has_experience is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Must provide a valid experience id to update")
        experience_request_dict = experience_request.dict(exclude_unset=True, exclude_defaults=True)
        experience_request_dict.pop("experience_id")
        designation = experience_request_dict.pop("designation")
        if designation is not None:
        experience_request_dict = {
            "experiences.$." + str(key): val for key, val in experience_request_dict.items()
        }
        db_profile: Profiles = await profile_crud_manager.update_by_query(  # type: ignore
            query={
                "experiences.experience_id": experience_request.experience_id,
                "_id": profile_experiences.id
            },
            item_dict=experience_request_dict
        )
        return ExperienceListDataResponse(
            experiences=[
                ExperienceCreateResponse(
                    experience_id=experience.experience_id,
                    company_name=experience.company_name,
                    job_responsibility=experience.job_responsibility,
                    designation=ProfileExperienceDesignationResponse(
                        designation=experience.designation.designation,
                        designation_id=experience.designation_id
                    ),
                    start_date=experience.start_date,
                    end_date=experience.end_date,
                    status=ResponseEnumData(id=experience.status,
                                            name=StatusEnum(experience.status).name)
                )
                for experience in db_profile.experiences
            ]
        )

    async def _create_experience_by_admin(self, experience_request: ExperienceCreateAdminRequest) -> ExperienceListDataResponse:
        profile_crud_manager = ProfileRepository()
        profile_experiences = cast(
            ProfileExperienceView,
            await profile_crud_manager.get_by_query(
                query={
                    "_id": experience_request.profile_id
                },
                projection_model=ProfileExperienceView
            )
        )
        if profile_experiences is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="You are not allowed to update the user profile")

        all_experience_ids = [
            experience.experience_id for experience in profile_experiences.experiences
        ]
        if not all_experience_ids:
            new_experience_id = 1

        else:
            """
            Calculate new experience id
            """
            new_experience_id = max(all_experience_ids) + 1
        new_experience = ProfileExperience(
            experience_id=new_experience_id,
            designation_id=None,
            company_name=cast(str, experience_request.company_name),
            designation=ExperienceDesignation(
                designation=experience_request.designation,
                designation_id=None
            ),
            start_date=experience_request.start_date,
            end_date=experience_request.end_date,
            job_responsibility=experience_request.job_responsibility,
            status=cast(StatusEnum, experience_request.status)
        )
        db_profile: Profiles = cast(Profiles, await profile_crud_manager.update_by_query(
            query={
                "_id": profile_experiences.id
            },
            push_item={
                "experiences": new_experience.dict(
                    exclude_unset=True, exclude_none=True
                )
            }
        )
                                    )
        return ExperienceListDataResponse(
            experiences=[
                ExperienceCreateResponse(
                    experience_id=experience.experience_id,
                    company_name=experience.company_name,
                    job_responsibility=experience.job_responsibility,
                    designation=ProfileExperienceDesignationResponse(
                        designation=experience.designation.designation,
                        designation_id=experience.designation_id
                    ),
                    start_date=experience.start_date,
                    end_date=experience.end_date,
                    status=ResponseEnumData(id=experience.status,
                                            name=StatusEnum(experience.status).name)
                )
                for experience in db_profile.experiences
            ]
        )
