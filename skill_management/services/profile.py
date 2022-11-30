from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError

from skill_management.enums import FileTypeEnum, DesignationStatusEnum, StatusEnum
from skill_management.models.designation import Designations
from skill_management.models.enums import ProfileStatus, DesignationStatus, Gender, Status
from skill_management.models.file import Files
from skill_management.models.profile import Profiles
from skill_management.repositories.profile import ProfileRepository
from skill_management.schemas.base import ResponseEnumData
from skill_management.schemas.designation import ProfileDesignation, ProfileDesignationResponse
from skill_management.schemas.education import ProfileEducationResponse
from skill_management.schemas.experience import ProfileExperience, ExperienceDesignation, ProfileExperienceResponse, \
    ProfileExperienceDesignationResponse
from skill_management.schemas.file import FileResponse
from skill_management.schemas.profile import ProfileBasicForAdminRequest, ProfilePersonalDetails, ProfileResponse, \
    ProfilePersonalDetailsResponse, ProfileUpdateByAdmin, ProfileBasicRequest, ProfileUpdateByUser
from skill_management.schemas.skill import ProfileSkillResponse


class ProfileService:
    # pass
    async def create_or_update_user_profile_by_user(self, profile: ProfileBasicRequest,
                                                    profile_data: Profiles | None) -> ProfileResponse:

        if profile_data is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Can not find user profile that matches current user")
        if profile.profile_id is not None:
            """
            Checking if the user profile is the owner of the profile request to update or create the profile
            """
            if not profile_data.id == profile.profile_id:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail="You are not allowed to update the user profile")
        if profile.profile_id is None:
            """ 
            It is  a create operation. 
            """
            response = await self._create_user_profile_by_user(profile)
        else:
            """ 
            It is  a update operation. 
            """
            response = await self._update_user_profile_by_user(profile)

        return response

    async def create_or_update_user_profile_by_admin(self, profile: ProfileBasicForAdminRequest) -> ProfileResponse:
        if profile.profile_id is None:
            """ 
            It is  a create operation. 
            """
            response = await self._create_user_profile_by_admin(profile)
        else:
            """ 
            It is  a update operation. 
            """
            response = await self._update_user_profile_by_admin(profile)

        return response

    @staticmethod
    async def _update_user_profile_by_admin(profile: ProfileBasicForAdminRequest) -> ProfileResponse:
        profile_crud_manager = ProfileRepository()
        old_profile: Profiles = await profile_crud_manager.get(id_=profile.profile_id)  # type: ignore

        if old_profile is None:
            """
            Check if the profile exists in the database
            """
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You should provide a existing profile id of the user"
            )
        if profile.email is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address can not be edited"
            )
        update_item = ProfileUpdateByAdmin(
            name=profile.name,
            date_of_birth=profile.date_of_birth,
            gender=profile.gender,
            mobile=profile.mobile,
            address=profile.address,
            designation_id=profile.designation_id,
            profile_status=profile.designation_status,  # type: ignore
            designation_status=profile.designation_status,
            about=profile.about)
        item_dict = update_item.dict(
            exclude_unset=True,
            exclude_none=True
        )

        if profile.designation_id is None:
            db_profile: Profiles = await profile_crud_manager.update(  # type: ignore
                id_=profile.profile_id,  # type: ignore
                item_dict={
                    "personal_detail": item_dict
                }
            )
        else:
            all_experience_id = [
                experience.experience_id for experience in old_profile.experiences
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
                    designation=(
                        await Designations.get(
                            profile.designation_id  # type: ignore
                        )
                    ).designation,

                    designation_id=profile.designation_id),
                start_date=None,
                end_date=None,
                job_responsibility=None,
                status=profile.designation_status  # type: ignore
            )

            """
            Update the profile in the database
            """
            db_profile = Profiles(
                await profile_crud_manager.update(
                    id_=profile.profile_id,  # type: ignore
                    item_dict={
                        "personal_detail": item_dict
                    },
                    push_item={
                        "experiences": new_experience.dict(
                            exclude_unset=True, exclude_none=True
                        )
                    }
                )
            )

        """
        Create skill list for the response
        """
        skill_list = []
        for skill_ in db_profile.skills:
            certificate_files = [
                FileResponse(
                    file_name=file,
                    url="/files/%s" % file.id
                ) async for file in Files.find(
                    {
                        "owner": db_profile.id,
                        "file_type": FileTypeEnum.certificate
                    }
                )
            ]
            skill_status_object: Status = await Status.get(skill_.status.value)  # type: ignore
            skill_list.append(
                ProfileSkillResponse(
                    skill_id=skill_.skill_id,
                    skill_name=skill_.skill_name,
                    experience_year=skill_.experience_year,
                    number_of_projects=skill_.number_of_projects,
                    level=skill_.level,
                    training_duration=skill_.training_duration,
                    achievements=skill_.achievements,
                    certificate=skill_.certificate,
                    certificate_files=certificate_files,
                    status=ResponseEnumData(
                        id=skill_status_object.id,
                        name=(
                            await Status.get(
                                skill_.status.value  # type: ignore
                            )
                        ).name
                    ),
                    achievements_description=skill_.achievements_description,
                    skill_category=[
                        ResponseEnumData(
                            id=skill_category_id,
                            name=(await Status.get(skill_category_id.value)).name  # type: ignore
                        )
                        for skill_category_id in skill_.skill_category
                    ],
                    skill_type=ResponseEnumData(
                        id=skill_.skill_type,
                        name=(await Status.get(skill_.skill_typ.value))).name)  # type: ignore

            )

        """
        Create personal detail for response
        """
        personal_detail_response = ProfilePersonalDetailsResponse(
            name=db_profile.personal_detail.name,
            date_of_birth=db_profile.personal_detail.date_of_birth,
            gender=ResponseEnumData(
                id=db_profile.personal_detail.gender,
                name=(
                    await Gender.get(
                        db_profile.personal_detail.gender.value  # type: ignore
                    )
                ).name
            ),
            mobile=db_profile.personal_detail.mobile,
            about=db_profile.personal_detail.about,
            address=db_profile.personal_detail.address,
            experience_year=db_profile.personal_detail.experience_year
        )

        """
        The final response for the profile update
        """
        response = ProfileResponse(
            id=db_profile.id,
            email=db_profile.user_id,
            designation=ProfileDesignationResponse(
                designation_id=db_profile.designation.designation_id,
                designation=db_profile.designation.designation,
                start_date=db_profile.designation.start_date,
                end_date=db_profile.designation.end_date,
                designation_status=ResponseEnumData(
                    id=db_profile.designation.designation_status,
                    name=(
                        await DesignationStatus.get(
                            db_profile.designation.designation_status.value  # type: ignore
                        )
                    ).name
                ),
            ),
            skills=skill_list,
            experiences=[
                ProfileExperienceResponse(
                    experience_id=experience.experience_id,
                    company_name=experience.company_name,
                    job_responsibility=experience.job_responsibility,
                    designation=ProfileExperienceDesignationResponse(
                        designation_id=experience.designation.designation_id,
                        designation=experience.designation.designation
                    ),
                    start_date=experience.start_date,
                    end_date=experience.end_date,
                    status=ResponseEnumData(
                        id=experience.status,
                        name=(await Status.get(experience.status.value)).name  # type: ignore
                    )
                )
                for experience in db_profile.experiences
            ],
            educations=[
                ProfileEducationResponse(
                    education_id=education.education_id,
                    degree_name=education.degree_name,
                    grade=education.grade,
                    passing_year=education.passing_year,
                    school_name=education.school_name
                ) for education in db_profile.educations
            ],
            personal_details=personal_detail_response,
            profile_status=ResponseEnumData(
                id=db_profile.profile_status,
                name=(
                    await ProfileStatus.get(
                        db_profile.profile_status.value  # type: ignore
                    )
                ).name
            )
        )
        return response

    @staticmethod
    async def _update_user_profile_by_user(profile: ProfileBasicRequest) -> ProfileResponse:
        profile_crud_manager = ProfileRepository()
        old_profile: Profiles = await profile_crud_manager.get(id_=profile.profile_id)  # type: ignore

        if old_profile is None:
            """
            Check if the profile exists in the database
            """
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You should provide a existing profile id of the user"
            )
        if profile.email is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address can not be edited"
            )
        update_item = ProfileUpdateByUser(
            name=profile.name,
            date_of_birth=profile.date_of_birth,
            gender=profile.gender,
            mobile=profile.mobile,
            address=profile.address,
            designation_id=profile.designation_id,
            about=profile.about)

        item_dict = update_item.dict(
            exclude_unset=True,
            exclude_none=True
        )

        if profile.designation_id is None:
            db_profile: Profiles = await profile_crud_manager.update(  # type: ignore
                id_=profile.profile_id,  # type: ignore
                item_dict={
                    "personal_detail": item_dict
                }
            )
        else:
            all_experience_id = [
                experience.experience_id for experience in old_profile.experiences
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
                    designation=(
                        await Designations.get(
                            profile.designation_id  # type: ignore
                        )
                    ).designation,

                    designation_id=profile.designation_id),
                start_date=None,
                end_date=None,
                job_responsibility=None,
                status=StatusEnum.active
            )

            """
            Update the profile in the database
            """
            db_profile = Profiles(
                await profile_crud_manager.update(
                    id_=profile.profile_id,  # type: ignore
                    item_dict={
                        "personal_detail": item_dict
                    },
                    push_item={
                        "experiences": new_experience.dict(
                            exclude_unset=True, exclude_none=True
                        )
                    }
                )
            )

        """
        Create skill list for the response
        """
        skill_list = []
        for skill_ in db_profile.skills:
            certificate_files = [
                FileResponse(
                    file_name=file,
                    url="/files/%s" % file.id
                ) async for file in Files.find(
                    {
                        "owner": db_profile.id,
                        "file_type": FileTypeEnum.certificate
                    }
                )
            ]
            skill_status_object: Status = await Status.get(skill_.status.value)  # type: ignore
            skill_list.append(
                ProfileSkillResponse(
                    skill_id=skill_.skill_id,
                    skill_name=skill_.skill_name,
                    experience_year=skill_.experience_year,
                    number_of_projects=skill_.number_of_projects,
                    level=skill_.level,
                    training_duration=skill_.training_duration,
                    achievements=skill_.achievements,
                    certificate=skill_.certificate,
                    certificate_files=certificate_files,
                    status=ResponseEnumData(
                        id=skill_status_object.id,
                        name=(
                            await Status.get(
                                skill_.status.value  # type: ignore
                            )
                        ).name
                    ),
                    achievements_description=skill_.achievements_description,
                    skill_category=[
                        ResponseEnumData(
                            id=skill_category_id,
                            name=(await Status.get(skill_category_id.value)).name  # type: ignore
                        )
                        for skill_category_id in skill_.skill_category
                    ],
                    skill_type=ResponseEnumData(
                        id=skill_.skill_type,
                        name=(await Status.get(skill_.skill_typ.value))).name)  # type: ignore

            )

        """
        Create personal detail for response
        """
        personal_detail_response = ProfilePersonalDetailsResponse(
            name=db_profile.personal_detail.name,
            date_of_birth=db_profile.personal_detail.date_of_birth,
            gender=ResponseEnumData(
                id=db_profile.personal_detail.gender,
                name=(
                    await Gender.get(
                        db_profile.personal_detail.gender.value  # type: ignore
                    )
                ).name
            ),
            mobile=db_profile.personal_detail.mobile,
            about=db_profile.personal_detail.about,
            address=db_profile.personal_detail.address,
            experience_year=db_profile.personal_detail.experience_year,
        )

        """
        The final response for the profile update
        """
        response = ProfileResponse(
            id=db_profile.id,
            email=db_profile.user_id,
            designation=ProfileDesignationResponse(
                designation_id=db_profile.designation.designation_id,
                designation=db_profile.designation.designation,
                start_date=db_profile.designation.start_date,
                end_date=db_profile.designation.end_date,
                designation_status=ResponseEnumData(
                    id=db_profile.designation.designation_status,
                    name=(
                        await DesignationStatus.get(
                            db_profile.designation.designation_status.value  # type: ignore
                        )
                    ).name
                ),
            ),
            skills=skill_list,
            experiences=[
                ProfileExperienceResponse(
                    experience_id=experience.experience_id,
                    company_name=experience.company_name,
                    job_responsibility=experience.job_responsibility,
                    designation=ProfileExperienceDesignationResponse(
                        designation_id=experience.designation.designation_id,
                        designation=experience.designation.designation
                    ),
                    start_date=experience.start_date,
                    end_date=experience.end_date,
                    status=ResponseEnumData(
                        id=experience.status,
                        name=(await Status.get(experience.status.value)).name  # type: ignore
                    )
                )
                for experience in db_profile.experiences
            ],
            educations=[
                ProfileEducationResponse(
                    education_id=education.education_id,
                    degree_name=education.degree_name,
                    grade=education.grade,
                    passing_year=education.passing_year,
                    school_name=education.school_name
                ) for education in db_profile.educations
            ],
            personal_details=personal_detail_response,
            profile_status=ResponseEnumData(
                id=db_profile.profile_status,
                name=(
                    await ProfileStatus.get(
                        db_profile.profile_status.value  # type: ignore
                    )
                ).name
            )
        )
        return response

    @staticmethod
    async def _create_user_profile_by_admin(profile: ProfileBasicForAdminRequest) -> ProfileResponse:
        if profile.email is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide email address"
            )
        if profile.name is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide name of the profile"
            )
        if profile.designation_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide designation of the profile"
            )

        designation: Designations = await Designations.get(profile.designation_id)  # type: ignore
        profile_status_object: ProfileStatus = await ProfileStatus.get(profile.profile_status.value)  # type: ignore
        personal_detail = ProfilePersonalDetails(
            name=profile.name,
            date_of_birth=profile.date_of_birth,
            gender=profile.gender,
            mobile=profile.mobile,
            about=None,
            address=None,
            experience_year=None
        )
        designation_status_object: DesignationStatus = await DesignationStatus.get(
            profile.designation_status.value  # type: ignore
        )

        gender_data: Gender = await Gender.get(profile.gender)  # type: ignore

        """
        Create profile object to insert into the database
        """
        db_profile = Profiles(
            user_id=profile.email,
            personal_detail=personal_detail,
            profile_status=profile.profile_status,
            designation=ProfileDesignation(
                designation_id=designation.id,
                designation=designation.designation,
                start_date=None, end_date=None,
                designation_status=profile.designation_status,
            ),
            skills=[],
            experiences=[
                ProfileExperience(
                    experience_id=1,
                    company_name="iXora Solution Ltd.",
                    designation=ExperienceDesignation(designation=designation.designation,
                                                      designation_id=1),
                    start_date=None,
                    end_date=None,
                    job_responsibility=None
                )
            ],
            educations=[],
            cv_files=[]
        )
        """
        Insert profile into database
        """
        try:
            await db_profile.insert()
        except DuplicateKeyError as duplicate_key_exec:
            duplicate_values = duplicate_key_exec.details["keyValue"].values()  # type: ignore
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Duplicate Value is not allowed. " + ", ".join(
                                    duplicate_values) + " already exists")
        """
        Create personal detail for response
        """
        personal_detail_response: ProfilePersonalDetailsResponse = ProfilePersonalDetailsResponse(
            name=profile.name,
            date_of_birth=profile.date_of_birth,
            gender=ResponseEnumData(
                id=gender_data.id,
                name=gender_data.name),
            mobile=profile.mobile,
            about=None,
            address=None,
            experience_year=None
        )

        """
        The final response for the profile create
        """
        response = ProfileResponse(
            id=db_profile.id,
            email=db_profile.user_id,
            designation=ProfileDesignationResponse(
                designation_id=designation.id,
                designation=designation.designation,
                start_date=None, end_date=None,
                designation_status=ResponseEnumData(
                    id=designation_status_object.id,
                    name=designation_status_object.name
                ),
            ),
            skills=[],
            experiences=[
                ProfileExperienceResponse(
                    experience_id=1,
                    company_name="iXora Solution Ltd.",
                    designation=ProfileExperienceDesignationResponse(
                        designation=designation.designation,
                        designation_id=1
                    ),
                    start_date=None,
                    end_date=None,
                    job_responsibility=None,
                    status=ResponseEnumData(
                        id=designation.id,
                        name=designation.designation
                    )
                )
            ],
            educations=[],
            personal_details=personal_detail_response,
            profile_status=ResponseEnumData(
                id=profile_status_object.id,
                name=profile_status_object.name
            )
        )
        return response

    @staticmethod
    async def _create_user_profile_by_user(profile: ProfileBasicRequest) -> ProfileResponse:
        if profile.email is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide email address"
            )
        if profile.name is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide name of the profile"
            )
        if profile.designation_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide designation of the profile"
            )

        designation: Designations = await Designations.get(profile.designation_id)  # type: ignore
        profile_status_object: ProfileStatus = await ProfileStatus.get(profile.profile_status.value)  # type: ignore
        personal_detail = ProfilePersonalDetails(
            name=profile.name,
            date_of_birth=profile.date_of_birth,
            gender=profile.gender,
            mobile=profile.mobile,
            about=None,
            address=None,
            experience_year=None
        )
        designation_status_object: DesignationStatus = await DesignationStatus.get(
            profile.designation_status.value  # type: ignore
        )

        gender_data: Gender = await Gender.get(profile.gender)  # type: ignore

        """
        Create profile object to insert into the database
        """
        db_profile = Profiles(
            user_id=profile.email,
            personal_detail=personal_detail,
            designation=ProfileDesignation(
                designation_id=designation.id,
                designation=designation.designation,
                start_date=None, end_date=None,
                designation_status=DesignationStatusEnum.inactive,
            ),
            skills=[],
            experiences=[
                ProfileExperience(
                    experience_id=1,
                    company_name="iXora Solution Ltd.",
                    designation=ExperienceDesignation(designation=designation.designation,
                                                      designation_id=1),
                    start_date=None,
                    end_date=None,
                    job_responsibility=None,
                    status=StatusEnum.active,
                )
            ],
            educations=[],
            cv_files=[]
        )
        """
        Insert profile into database
        """
        try:
            await db_profile.insert()
        except DuplicateKeyError as duplicate_key_exec:
            duplicate_values = duplicate_key_exec.details["keyValue"].values()  # type: ignore
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Duplicate Value is not allowed. " + ", ".join(
                                    duplicate_values) + " already exists")
        """
        Create personal detail for response
        """
        personal_detail_response: ProfilePersonalDetailsResponse = ProfilePersonalDetailsResponse(
            name=profile.name,
            date_of_birth=profile.date_of_birth,
            gender=ResponseEnumData(
                id=gender_data.id,
                name=gender_data.name),
            mobile=profile.mobile,
            about=None,
            address=None,
            experience_year=None
        )

        """
        The final response for the profile create
        """
        response = ProfileResponse(
            id=db_profile.id,
            email=db_profile.user_id,
            designation=ProfileDesignationResponse(
                designation_id=designation.id,
                designation=designation.designation,
                start_date=None, end_date=None,
                designation_status=ResponseEnumData(
                    id=designation_status_object.id,
                    name=designation_status_object.name
                ),
            ),
            skills=[],
            experiences=[
                ProfileExperienceResponse(
                    experience_id=1,
                    company_name="iXora Solution Ltd.",
                    designation=ProfileExperienceDesignationResponse(
                        designation=designation.designation,
                        designation_id=1
                    ),
                    start_date=None,
                    end_date=None,
                    job_responsibility=None,
                    status=ResponseEnumData(
                        id=designation.id,
                        name=designation.designation
                    )
                )
            ],
            educations=[],
            personal_details=personal_detail_response,
            profile_status=ResponseEnumData(
                id=profile_status_object.id,
                name=profile_status_object.name
            )
        )
        return response
