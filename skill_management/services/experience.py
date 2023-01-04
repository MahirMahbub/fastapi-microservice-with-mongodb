from typing import cast

from beanie import PydanticObjectId
from beanie.odm.operators.find.array import ElemMatch
from fastapi import HTTPException, status

from skill_management.enums import StatusEnum, ProfileStatusEnum, DesignationStatusEnum
from skill_management.models.designation import Designations
from skill_management.models.profile import Profiles
from skill_management.repositories.profile import ProfileRepository
from skill_management.schemas.base import ResponseEnumData
from skill_management.schemas.designation import DesignationDataResponse, ProfileDesignation
from skill_management.schemas.experience import ExperienceCreateRequest, ExperienceListDataResponse, \
    ExperienceCreateAdminRequest, ExperienceCreateResponse, ProfileExperienceDesignationResponse, ProfileExperience, \
    ExperienceDesignation, ProfileExperienceDetailsResponse, ProfileExperienceResponse
from skill_management.schemas.profile import ProfileExperienceView, ProfileDesignationExperiencesView


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

    async def create_or_update_experience_by_admin(self, experience_request: ExperienceCreateAdminRequest) \
            -> ExperienceListDataResponse:

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

    @staticmethod
    async def _update_experience_by_user(experience_request: ExperienceCreateRequest,
                                         email: str) -> ExperienceListDataResponse:
        profile_crud_manager = ProfileRepository()
        profile_experiences = cast(
            ProfileDesignationExperiencesView,
            await profile_crud_manager.get_by_query(
                query={
                    "user_id": email
                },
                projection_model=ProfileDesignationExperiencesView
            )
        )
        if profile_experiences is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="You are not allowed to update the user profile")

        if not profile_experiences.profile_status in [
            ProfileStatusEnum.full_time,
            ProfileStatusEnum.part_time
        ]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="You can only update experience for profile that is active.")

        db_profile_experience = await Profiles.find(
            {
                "user_id": email
            },
            ElemMatch(
                Profiles.experiences,
                {
                    "experience_id": experience_request.experience_id
                }
            ),
            projection_model=ProfileDesignationExperiencesView).first_or_none()
        if db_profile_experience is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Must provide a valid experience id to update")
        experience_request_dict = experience_request.dict()
        experience_request_dict.pop("experience_id")
        experience_status = experience_request_dict.pop("status")

        designation_name = experience_request_dict.pop("designation")

        is_db_designation = False
        experience_object: ProfileExperience | None = None
        for exp in cast(list[ProfileExperience], db_profile_experience.experiences):
            if exp.experience_id == experience_request.experience_id:
                experience_object = exp
                is_db_designation = True if exp.designation.designation_id is not None else False
                break
        if experience_status is not None:
            experience_request_dict["status"] = experience_status
        else:
            experience_request_dict["status"] = cast(ProfileExperience, experience_object).status

        if is_db_designation:
            db_designation = await Designations.find(
                {
                    "designation": cast(ProfileExperience, experience_object).designation.designation
                }
            ).first_or_none()
            if db_designation is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Must provide a designation that is predetermined in this company,"
                                           "This experience is created from profile designation")
            designation = DesignationDataResponse(
                designation_id=db_designation.id,
                designation=db_designation.designation
            )
        else:
            designation = DesignationDataResponse(
                designation_id=None,
                designation=designation_name
            )
        experience_request_dict = {
            "experiences.$." + str(key): val for key, val in experience_request_dict.items() if val is not None
        }
        experience_request_dict["experiences.$.designation.designation"] = designation.designation
        experience_request_dict["experiences.$.designation.designation_id"] = designation.designation_id
        db_profile: Profiles = cast(
            Profiles, await profile_crud_manager.update_by_query(
                query={
                    "experiences.experience_id": experience_request.experience_id,
                    "_id": profile_experiences.id
                },
                item_dict=experience_request_dict
            )
        )
        if designation.designation_id is not None:
            old_designation: ProfileDesignation = cast(ProfileDesignation, profile_experiences.designation)
            old_designation.designation_status = DesignationStatusEnum.inactive
            old_designation.designation_id = designation.designation_id
            old_designation.designation = cast(str, designation.designation)
            old_designation_dict = old_designation.dict()
            experience_request_dict = {
                "designation." + str(key): val for key, val in old_designation_dict.items() if val is not None
            }
            await profile_crud_manager.update_by_query(query={"_id": profile_experiences.id},
                                                       item_dict=experience_request_dict)
        return ExperienceListDataResponse(
            experiences=[
                ExperienceCreateResponse(
                    experience_id=experience.experience_id,
                    company_name=experience.company_name,
                    job_responsibility=experience.job_responsibility,
                    designation=ProfileExperienceDesignationResponse(
                        designation=experience.designation.designation,
                        designation_id=experience.designation.designation_id
                    ),
                    start_date=experience.start_date,
                    end_date=experience.end_date,
                    status=ResponseEnumData(id=experience.status,
                                            name=StatusEnum(experience.status).name)
                )
                for experience in db_profile.experiences if experience.status == StatusEnum.active
            ]
        )

    @staticmethod
    async def _create_experience_by_user(experience_request: ExperienceCreateRequest,
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

        if not profile_experiences.profile_status in [
            ProfileStatusEnum.full_time,
            ProfileStatusEnum.part_time
        ]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="You can only update education for profile that is active.")

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
            company_name=cast(str, experience_request.company_name),
            designation=ExperienceDesignation(
                designation=experience_request.designation,
                designation_id=None
            ),
            start_date=experience_request.start_date,
            end_date=experience_request.end_date,
            job_responsibility=experience_request.job_responsibility,
            status=cast(StatusEnum,
                        experience_request.status) if experience_request.status is not None else StatusEnum.active
        )
        db_profile: Profiles = cast(Profiles, await profile_crud_manager.update_by_query(
            query={
                "_id": profile_experiences.id
            },
            push_item={
                "experiences": new_experience.dict()
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
                        designation_id=experience.designation.designation_id
                    ),
                    start_date=experience.start_date,
                    end_date=experience.end_date,
                    status=ResponseEnumData(
                        id=experience.status,
                        name=StatusEnum(experience.status).name
                    )
                )
                for experience in db_profile.experiences if experience.status == StatusEnum.active
            ]
        )

    @staticmethod
    async def _update_experience_by_admin(
            experience_request: ExperienceCreateAdminRequest) -> ExperienceListDataResponse:
        profile_crud_manager = ProfileRepository()
        profile_experiences = cast(
            ProfileDesignationExperiencesView,
            await profile_crud_manager.get_by_query(
                query={
                    "_id": experience_request.profile_id
                },
                projection_model=ProfileDesignationExperiencesView
            )
        )
        if profile_experiences is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="You are not allowed to update the user profile")

        if profile_experiences.profile_status not in [
            ProfileStatusEnum.full_time,
            ProfileStatusEnum.part_time
        ]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="You can only update education for profile that is active.")

        db_experience_profile = await Profiles.find(
            {
                "_id": experience_request.profile_id
            },
            ElemMatch(
                Profiles.experiences, {
                    "experience_id": experience_request.experience_id
                }
            ),
            projection_model=ProfileDesignationExperiencesView
        ).first_or_none()
        if db_experience_profile is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Must provide a valid experience id to update")

        experience_request_dict = experience_request.dict()
        experience_request_dict.pop("experience_id")
        experience_status = experience_request_dict.pop("status")
        experience_request_dict.pop("profile_id")
        ##
        designation_name = experience_request_dict.pop("designation")

        is_db_designation = False
        experience_object = None
        for exp in cast(list[ProfileExperience], db_experience_profile.experiences):
            if exp.experience_id == experience_request.experience_id:
                experience_object = exp
                is_db_designation = True if exp.designation.designation_id is not None else False
                break

        if experience_status is not None:
            experience_request_dict["status"] = experience_request.status
        else:
            experience_request_dict["status"] = cast(ProfileExperience, experience_object).status

        if is_db_designation:
            db_designation = await Designations.find(
                {
                    "designation": designation_name
                }
            ).first_or_none()
            if db_designation is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Must provide a designation that is predetermined in this company,"
                                           "This experience is created from profile designation")
            designation = DesignationDataResponse(
                designation_id=db_designation.id,
                designation=db_designation.designation
            )
        else:
            designation = DesignationDataResponse(
                designation_id=None,
                designation=designation_name
            )
        experience_request_dict = {
            "experiences.$." + str(key): val for key, val in experience_request_dict.items() if val is not None
        }
        experience_request_dict["experiences.$.designation.designation"] = designation.designation
        experience_request_dict["experiences.$.designation.designation_id"] = designation.designation_id
        db_profile: Profiles = cast(
            Profiles, await profile_crud_manager.update_by_query(
                query={
                    "experiences.experience_id": experience_request.experience_id,
                    "_id": profile_experiences.id
                },
                item_dict=experience_request_dict
            )
        )
        if designation.designation_id is not None:
            old_designation: ProfileDesignation = cast(ProfileDesignation, profile_experiences.designation)
            old_designation.designation_status = DesignationStatusEnum.inactive
            old_designation.designation_id = designation.designation_id
            old_designation.designation = cast(str, designation.designation)
            old_designation_dict = old_designation.dict()
            experience_request_dict = {
                "designation." + str(key): val for key, val in old_designation_dict.items() if val is not None
            }
            await profile_crud_manager.update_by_query(query={"_id": profile_experiences.id},
                                                       item_dict=experience_request_dict)
        return ExperienceListDataResponse(
            experiences=[
                ExperienceCreateResponse(
                    experience_id=experience.experience_id,
                    company_name=experience.company_name,
                    job_responsibility=experience.job_responsibility,
                    designation=ProfileExperienceDesignationResponse(
                        designation=experience.designation.designation,
                        designation_id=experience.designation.designation_id
                    ),
                    start_date=experience.start_date,
                    end_date=experience.end_date,
                    status=ResponseEnumData(id=experience.status,
                                            name=StatusEnum(experience.status).name)
                )
                for experience in db_profile.experiences if experience.status in [StatusEnum.active, StatusEnum.cancel]
            ]
        )

    @staticmethod
    async def _create_experience_by_admin(
            experience_request: ExperienceCreateAdminRequest) -> ExperienceListDataResponse:
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

        if not profile_experiences.profile_status in [
            ProfileStatusEnum.full_time,
            ProfileStatusEnum.part_time
        ]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="You can only update education for profile that is active.")

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
            company_name=cast(str, experience_request.company_name),
            designation=ExperienceDesignation(
                designation=experience_request.designation,
                designation_id=None
            ),
            start_date=experience_request.start_date,
            end_date=experience_request.end_date,
            job_responsibility=experience_request.job_responsibility,
            status=cast(StatusEnum,
                        experience_request.status) if experience_request.status is not None else StatusEnum.active,
        )
        db_profile: Profiles = cast(Profiles, await profile_crud_manager.update_by_query(
            query={
                "_id": profile_experiences.id
            },
            push_item={
                "experiences": new_experience.dict()
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
                        designation_id=experience.designation.designation_id
                    ),
                    start_date=experience.start_date,
                    end_date=experience.end_date,
                    status=ResponseEnumData(id=experience.status,
                                            name=StatusEnum(experience.status).name)
                )
                for experience in db_profile.experiences if experience.status in [StatusEnum.active, StatusEnum.cancel]
            ]
        )

    @staticmethod
    async def get_experiences_details_by_admin(profile_id: PydanticObjectId) -> ProfileExperienceDetailsResponse:
        query = {
            '_id': profile_id,
        }
        db_profiles: ProfileExperienceView = cast(ProfileExperienceView, await Profiles.find(
            query,
            projection_model=ProfileExperienceView
        ).first_or_none())
        if db_profiles is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Must provide a valid profile id")

        return ProfileExperienceDetailsResponse(
            experiences=[
                ProfileExperienceResponse(experience_id=data.experience_id,
                                          company_name=data.company_name,
                                          job_responsibility=data.job_responsibility,
                                          designation=ProfileExperienceDesignationResponse(
                                              designation=data.designation.designation,
                                              designation_id=data.designation.designation_id),
                                          start_date=data.start_date,
                                          end_date=data.end_date,
                                          status=ResponseEnumData(
                                              id=data.status,
                                              name=StatusEnum(data.status).name)
                                          )
                for data in db_profiles.experiences if
                data.status in [StatusEnum.active, StatusEnum.cancel]
            ]
        )

    @staticmethod
    async def get_experiences_details_by_user(email: str) -> ProfileExperienceDetailsResponse:
        query = {
            'user_id': email,
        }
        db_profiles: ProfileExperienceView = cast(
            ProfileExperienceView, await Profiles.find(
                query,
                projection_model=ProfileExperienceView
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
        return ProfileExperienceDetailsResponse(
            experiences=[
                ProfileExperienceResponse(experience_id=data.experience_id,
                                          company_name=data.company_name,
                                          job_responsibility=data.job_responsibility,
                                          designation=ProfileExperienceDesignationResponse(
                                              designation=data.designation.designation,
                                              designation_id=data.designation.designation_id),
                                          start_date=data.start_date,
                                          end_date=data.end_date,
                                          status=ResponseEnumData(
                                              id=data.status,
                                              name=StatusEnum(data.status).name)
                                          ) for data in db_profiles.experiences if data.status == StatusEnum.active
            ]
        )
