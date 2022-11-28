from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError

from skill_management.models.designation import Designations
from skill_management.models.enums import ProfileStatus, DesignationStatus, Gender
from skill_management.models.profile import Profiles
from skill_management.schemas.base import ResponseEnumData
from skill_management.schemas.designation import ProfileDesignation, ProfileDesignationResponse
from skill_management.schemas.profile import ProfileBasicForAdminRequest, ProfilePersonalDetails, ProfileResponse, \
    ProfilePersonalDetailsResponse


class ProfileService:
    # pass
    async def create_user_profile_by_admin(self, profile: ProfileBasicForAdminRequest):

        if profile.profile_id is None:
            """ 
            It is  a create operation. 
            """
            if profile.email is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Must provide email address")
            if profile.name is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Must provide name of the profile")
            if profile.designation_id is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Must provide designation of the profile")

            designation: Designations | None = await Designations.get(profile.designation_id)  # type: ignore
            if designation is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Invalid designation of the profile")

            gender_data = await Gender.get(profile.gender)  # type: ignore
            if gender_data is None:
                raise

            profile_status_object: ProfileStatus = await ProfileStatus.get(profile.profile_status.value)  # type: ignore

            personal_detail = ProfilePersonalDetails(name=profile.name,
                                                     date_of_birth=profile.date_of_birth,
                                                     gender=profile.gender,
                                                     mobile=profile.mobile,
                                                     about=None,
                                                     address=None,
                                                     experience_year=None
                                                     )

            db_profile = Profiles(user_id=profile.email,
                                  personal_detail=personal_detail,
                                  profile_status=profile.profile_status,
                                  designation=[ProfileDesignation(
                                      designation_id=designation.id,
                                      designation=designation.designation,
                                      start_date=None, end_date=None,
                                      designation_status=profile.designation_status,
                                  )],
                                  skills=[],
                                  experiences=[],
                                  education=[],
                                  cv_files=[]
                                  )
            try:
                await db_profile.insert()
            except DuplicateKeyError as duplicate_key_exec:
                duplicate_values = duplicate_key_exec.details["keyValue"].values()
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Duplicate Value is not allowed. " + ", ".join(
                                        duplicate_values) + " already exists")
            # return db_profile
            personal_detail_response = ProfilePersonalDetailsResponse(name=profile.name,
                                                                      date_of_birth=profile.date_of_birth,
                                                                      gender=ResponseEnumData(id=gender_data.id,
                                                                                              name=gender_data.name),
                                                                      mobile=profile.mobile,
                                                                      about=None,
                                                                      address=None,
                                                                      experience_year=None)
            response = ProfileResponse(id=db_profile.id,
                                       email=db_profile.user_id,
                                       designation=[ProfileDesignationResponse(
                                           designation_id=designation.id,
                                           designation=designation.designation,
                                           start_date=None, end_date=None,
                                           designation_status=ResponseEnumData(id=designation.id,
                                                                               name=designation.designation),
                                       )],
                                       skills=[],
                                       experience=[],
                                       education=[],
                                       personal_details=personal_detail_response,
                                       profile_status=ResponseEnumData(id=profile_status_object.id,
                                                                       name=profile_status_object.name))
            return response
