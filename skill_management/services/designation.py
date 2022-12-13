from typing import cast

from fastapi import HTTPException, status

from skill_management.enums import DesignationStatusEnum, StatusEnum, ProfileStatusEnum
from skill_management.models.designation import Designations
from skill_management.models.profile import Profiles
from skill_management.repositories.designation import DesignationRepository
from skill_management.repositories.profile import ProfileRepository
from skill_management.schemas.base import ResponseEnumData
from skill_management.schemas.designation import DesignationCreateRequest, ProfileDesignationResponse, \
    DesignationCreateAdminRequest, DesignationDataResponse, ProfileDesignationDetailsResponse
from skill_management.schemas.experience import ProfileExperience, ExperienceDesignation
from skill_management.schemas.profile import ProfileDesignationExperiencesView, ProfileDesignationView


class DesignationService:
    @staticmethod
    async def update_designation_by_user(designation_request: DesignationCreateRequest,
                                         email: str) -> ProfileDesignationResponse:
        profile_crud_manager = ProfileRepository()
        profile_designation_experiences: ProfileDesignationExperiencesView | None = await profile_crud_manager.get_by_query(
            # type: ignore
            query={"user_id": email}, projection_model=ProfileDesignationExperiencesView)

        if not profile_designation_experiences.profile_status in [
            ProfileStatusEnum.full_time,
            ProfileStatusEnum.part_time
        ]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="You can only update designation for profile that is active.")
        if profile_designation_experiences is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="You are not allowed to update the user profile")
        if profile_designation_experiences.designation is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Must provide a valid designation to update")
        # designation_id: int = profile_designation.designation.designation_id
        item_dict = designation_request.dict(exclude_unset=True, exclude_none=True)
        old_designation_data = profile_designation_experiences.designation.dict()

        old_designation_data["designation_status"] = DesignationStatusEnum.inactive

        for key, value in item_dict.items():
            if key in old_designation_data:
                old_designation_data[key] = value

        exist_experience: ProfileExperience | None = None
        for data in profile_designation_experiences.experiences:
            if data.designation.designation_id == profile_designation_experiences.designation.designation_id:
                exist_experience = data
                break
        if exist_experience:
            experience_dict = exist_experience.dict()
            designation = experience_dict.pop("designation")
            for key, value in item_dict.items():
                if key in experience_dict:
                    experience_dict[key] = value
            # Set existing experience related to designation is cancel so that admin can active the designation request.
            experience_dict["status"] = StatusEnum.cancel
            experience_dict.pop("experience_id")
            experience_request_dict = {"experiences.$." + str(key): val for key, val in experience_dict.items()}

            experience_request_dict["experiences.$.designation.designation"] = designation["designation"]
            experience_request_dict["experiences.$.designation.designation_id"] = designation["designation_id"]
            db_profile: Profiles = await profile_crud_manager.update_by_query(  # type: ignore
                query={
                    "experiences.experience_id": exist_experience.experience_id,
                    "_id": profile_designation_experiences.id
                },
                item_dict=experience_request_dict
            )
        old_designation_data["designation_status"] = DesignationStatusEnum.inactive

        db_profile = cast(
            Profiles, await profile_crud_manager.update_by_query(
                query={
                    "user_id": email
                },
                item_dict={
                    "designation": old_designation_data
                }
            )
        )
        return ProfileDesignationResponse(
            designation=db_profile.designation.designation,
            designation_id=db_profile.designation.designation_id,
            designation_status=ResponseEnumData(
                id=db_profile.designation.designation_status,
                name=DesignationStatusEnum(db_profile.designation.designation_status).name
            ),
            end_date=db_profile.designation.end_date,
            start_date=db_profile.designation.start_date,
        )

    @staticmethod
    async def update_designation_by_admin(
            designation_request: DesignationCreateAdminRequest) -> ProfileDesignationResponse:
        profile_crud_manager = ProfileRepository()
        old_profile: Profiles = await profile_crud_manager.get(id_=designation_request.profile_id)  # type: ignore
        profile_designation_experiences = cast(
            ProfileDesignationExperiencesView,
            await profile_crud_manager.get_by_query(
                query={
                    "_id": designation_request.profile_id
                }, projection_model=ProfileDesignationExperiencesView
            )
        )

        if profile_designation_experiences is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="You are not allowed to update the user profile")

        if not profile_designation_experiences.profile_status in [
            ProfileStatusEnum.full_time,
            ProfileStatusEnum.part_time
        ]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="You can only update designation for profile that is active.")

        if profile_designation_experiences.designation is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Must provide a valid designation to update")

        if designation_request.designation_status == DesignationStatusEnum.inactive:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="You can only activate designation that is waiting for approval")

        # designation_id: int = profile_designation.designation.designation_id
        item_dict = designation_request.dict(exclude_unset=True, exclude_none=True)
        item_dict.pop("profile_id")
        # request_designation_id = item_dict.pop("designation_id")
        old_designation_data = profile_designation_experiences.designation.dict()

        for key, value in item_dict.items():
            if key in old_designation_data:
                old_designation_data[key] = value
        if designation_request.designation_status == DesignationStatusEnum.active:
            """
            Active the designation by admin
            """
            exist_experience: ProfileExperience | None = None
            for data in profile_designation_experiences.experiences:
                if data.designation.designation_id == profile_designation_experiences.designation.designation_id:
                    exist_experience = data
                    break
            if exist_experience:
                experience_dict = exist_experience.dict()
                designation = experience_dict.pop("designation")
                for key, value in item_dict.items():
                    if key in experience_dict:
                        experience_dict[key] = value
                experience_dict["status"] = StatusEnum.active
                experience_dict.pop("experience_id")
                experience_request_dict = {"experiences.$." + str(key): val for key, val in experience_dict.items()}
                experience_request_dict["experiences.$.designation.designation"] = designation["designation"]
                experience_request_dict["experiences.$.designation.designation_id"] = designation["designation_id"]
                await profile_crud_manager.update_by_query(
                    query={
                        "experiences.experience_id": exist_experience.experience_id,
                        "_id": designation_request.profile_id
                    },
                    item_dict=experience_request_dict
                )
                db_profile = cast(Profiles, await profile_crud_manager.update_by_query(
                    query={
                        "_id": designation_request.profile_id
                    },
                    item_dict={
                        "designation": old_designation_data
                    },
                )
                                  )
            else:
                all_experience_id = [
                    experience.experience_id for experience in profile_designation_experiences.experiences
                ]

                if not all_experience_id:
                    new_experience_id = 1

                else:
                    """
                    Calculate new experience id
                    """
                    new_experience_id = max(all_experience_id) + 1

                """
                Create new experience from the designation id provided
                """
                new_experience = ProfileExperience(
                    experience_id=new_experience_id,
                    company_name="iXora Solution Ltd.",
                    designation=ExperienceDesignation(
                        designation=profile_designation_experiences.designation.designation,
                        designation_id=profile_designation_experiences.designation.designation_id),
                    start_date=profile_designation_experiences.designation.start_date,
                    end_date=profile_designation_experiences.designation.end_date,
                    job_responsibility="",
                    status=StatusEnum.active
                )
                db_profile: Profiles = await profile_crud_manager.update_by_query(  # type: ignore
                    query={
                        "_id": designation_request.profile_id
                    },
                    item_dict={
                        "designation": old_designation_data
                    },
                    push_item={
                        "experiences": new_experience.dict(
                            exclude_unset=True,
                        )
                    }
                )
        else:
            exist_experience = None
            for data in profile_designation_experiences.experiences:
                if data.designation.designation_id == profile_designation_experiences.designation.designation_id:
                    exist_experience = data
                    break
            if exist_experience:
                experience_dict = exist_experience.dict()
                experience_dict.pop("experience_id")
                for key, value in item_dict.items():
                    if key in experience_dict:
                        experience_dict[key] = value
                experience_dict["status"] = StatusEnum.cancel
                designation = experience_dict.pop("designation")
                experience_request_dict = {"experiences.$." + str(key): val for key, val in experience_dict.items()}

                # experience_request_dict = {
                #     "experiences.$." + str(key): val for key, val in experience_request_dict.items()
                # }
                experience_request_dict["experiences.$.designation.designation"] = designation["designation"]
                experience_request_dict["experiences.$.designation.designation_id"] = designation["designation_id"]
                db_profile = cast(
                    Profiles, await profile_crud_manager.update_by_query(
                        query={
                            "experiences.experience_id": exist_experience.experience_id,
                            "_id": designation_request.profile_id
                        },
                        item_dict=experience_request_dict
                    )
                )
            old_designation_data["designation_status"] = DesignationStatusEnum.inactive
            db_profile: Profiles = await profile_crud_manager.update_by_query(  # type: ignore
                query={
                    "_id": designation_request.profile_id
                },
                item_dict={
                    "designation": old_designation_data
                },
            )
        return ProfileDesignationResponse(
            designation=db_profile.designation.designation,
            designation_id=db_profile.designation.designation_id,
            designation_status=ResponseEnumData(
                id=db_profile.designation.designation_status,
                name=DesignationStatusEnum(db_profile.designation.designation_status).name
            ),
            end_date=db_profile.designation.end_date,
            start_date=db_profile.designation.start_date,
        )

    async def get_master_designation_list(self, designation_name):
        query = {}
        if designation_name is not None:
            query = {
                "designation":
                    {
                        '$regex': designation_name, '$options': 'i'
                    }
            }

        designation_crud_manager = DesignationRepository()
        designation_list = cast(list[Designations], await designation_crud_manager.gets(query))
        response = [DesignationDataResponse(designation_id=data.id,
                                            designation=data.designation) for data in designation_list]
        return response

    # def get_master_designation_detail(self, designation_id):
    #     designation_crud_manager = DesignationRepository()
    #     designation_list = cast(list[Designations], designation_crud_manager.gets(query))
    #     return response
    async def get_designation_details_by_admin(self, profile_id) -> ProfileDesignationDetailsResponse:
        query = {
            '_id': profile_id,
        }
        db_profiles: ProfileDesignationView = cast(ProfileDesignationView, await Profiles.find(
            query,
            projection_model=ProfileDesignationView
        ).first_or_none())
        if db_profiles is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Must provide a valid profile id")
        return ProfileDesignationDetailsResponse(
            designation=ProfileDesignationResponse(
                designation_id=db_profiles.designation.designation_id,
                designation=db_profiles.designation.designation,
                start_date=db_profiles.designation.start_date,
                end_date=db_profiles.designation.end_date,
                designation_status=ResponseEnumData(
                    id=db_profiles.designation.designation_status,
                    name=DesignationStatusEnum(db_profiles.designation.designation_status).name
                )
            )
        )

    async def get_designation_details_by_user(self, email) -> ProfileDesignationDetailsResponse:
        query = {
            'user_id': email,
        }
        db_profiles: ProfileDesignationView = cast(
            ProfileDesignationView, await Profiles.find(
                query,
                projection_model=ProfileDesignationView
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
        return ProfileDesignationDetailsResponse(
            designation=ProfileDesignationResponse(
                designation_id=db_profiles.designation.designation_id,
                designation=db_profiles.designation.designation,
                start_date=db_profiles.designation.start_date,
                end_date=db_profiles.designation.end_date,
                designation_status=ResponseEnumData(
                    id=db_profiles.designation.designation_status,
                    name=DesignationStatusEnum(db_profiles.designation.designation_status).name
                )
            )
        )
