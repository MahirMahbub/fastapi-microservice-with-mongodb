from beanie.odm.operators.find.array import ElemMatch
from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError

from skill_management.enums import FileTypeEnum, DesignationStatusEnum, StatusEnum, GenderEnum, ProfileStatusEnum, \
    SkillCategoryEnum, SkillTypeEnum
from skill_management.models.designation import Designations
from skill_management.models.enums import ProfileStatus, DesignationStatus, Gender, Status
from skill_management.models.file import Files
from skill_management.models.profile import Profiles
from skill_management.repositories.profile import ProfileRepository
from skill_management.schemas.base import ResponseEnumData
from skill_management.schemas.designation import ProfileDesignation, ProfileDesignationResponse, DesignationDataResponse
from skill_management.schemas.education import ProfileEducationResponse
from skill_management.schemas.experience import ProfileExperience, ExperienceDesignation, ProfileExperienceResponse, \
    ProfileExperienceDesignationResponse
from skill_management.schemas.file import FileResponse
from skill_management.schemas.profile import ProfileBasicForAdminRequest, ProfilePersonalDetails, ProfileResponse, \
    ProfilePersonalDetailsResponse, ProfileUpdateByAdmin, ProfileBasicRequest, ProfileUpdateByUser, \
    ProfileBasicResponse, PaginatedProfileResponse
from skill_management.schemas.skill import ProfileSkillResponse, ProfileSkillDataResponse


class ProfileService:
    # pass
    async def create_or_update_user_profile_by_user(self, profile_request: ProfileBasicRequest,
                                                    email: str | None) -> ProfileResponse:

        if profile_request.profile_id is not None:
            """
            Checking if the user profile is the owner of the profile request to update or create the profile
            """
            profile_data = await ProfileRepository().get_by_query({"user_id": email})
            if not profile_data.id == profile_request.profile_id:  # type: ignore
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail="You are not allowed to update the user profile")
        if profile_request.profile_id is None:
            """ 
            It is  a create operation. 
            """
            response = await self._create_user_profile_by_user(profile_request, email)
        else:
            """ 
            It is  a update operation. 
            """
            response = await self._update_user_profile_by_user(profile_request)

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
    async def _update_user_profile_by_admin(profile_request: ProfileBasicForAdminRequest) -> ProfileResponse:
        profile_crud_manager = ProfileRepository()
        old_profile: Profiles = await profile_crud_manager.get(id_=profile_request.profile_id)  # type: ignore
        db_profile: Profiles

        if old_profile is None:
            """
            Check if the profile exists in the database
            """
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You should provide a existing profile id of the user"
            )
        if profile_request.email is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address can not be edited"
            )
        update_item = ProfileUpdateByAdmin(
            name=profile_request.name,
            date_of_birth=profile_request.date_of_birth,
            gender=profile_request.gender,
            mobile=profile_request.mobile,
            address=profile_request.address,
            designation_id=profile_request.designation_id,
            profile_status=profile_request.designation_status,  # type: ignore
            designation_status=profile_request.designation_status,
            about=profile_request.about
        )
        item_dict = update_item.dict(
            exclude_unset=True,
            exclude_none=True
        )
        if item_dict.get("designation_status") is not None:
            item_dict.pop("designation_status")
        if item_dict.get("designation_id") is not None:
            item_dict.pop("designation_id")

        old_profile_details = old_profile.personal_detail.dict()
        for key, value in item_dict.items():
            if key in old_profile_details:
                old_profile_details[key] = value

        if profile_request.designation_id is None:
            db_profile = await profile_crud_manager.update(  # type: ignore
                id_=profile_request.profile_id,  # type: ignore
                item_dict={
                    "personal_detail": old_profile_details
                }
            )
        elif profile_request.designation_id is not None:
            if profile_request.designation_status == DesignationStatusEnum.active:
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
                Get Designation Data
                """
                designation: Designations = await Designations.get(profile_request.designation_id)  # type: ignore

                """
                Create new experience from the designation id provided
                """
                new_experience = ProfileExperience(
                    experience_id=new_experience_id,
                    company_name="iXora Solution Ltd.",
                    designation=ExperienceDesignation(
                        designation=designation.designation,
                        designation_id=profile_request.designation_id),
                    start_date=None,
                    end_date=None,
                    job_responsibility=None,
                    status=StatusEnum.active  # type: ignore
                )

                """
                Update the profile in the database
                """

                db_profile = await profile_crud_manager.update(  # type: ignore
                    id_=profile_request.profile_id,  # type: ignore
                    item_dict={
                        "personal_detail": old_profile_details,
                        "designation": {
                            'designation_id': designation.id,
                            'designation': designation.designation,
                            'start_date': None, 'end_date': None,
                            'designation_status': profile_request.designation_status,
                        }
                    },
                    push_item={
                        "experiences": new_experience.dict(
                            exclude_unset=True, exclude_none=True
                        )
                    }
                )
            elif profile_request.designation_status == DesignationStatusEnum.inactive:
                designation: Designations = await Designations.get(profile_request.designation_id)  # type: ignore
                db_profile = await profile_crud_manager.update(  # type: ignore
                    id_=profile_request.profile_id,  # type: ignore
                    item_dict={
                        "personal_detail": old_profile_details,
                        "designation": {
                            'designation_id': designation.id,
                            'designation': designation.designation,
                            'designation_status': profile_request.designation_status,
                        }
                    }
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
                        name=StatusEnum(skill_status_object.id).name
                    ),
                    achievements_description=skill_.achievements_description,
                    skill_category=[
                        ResponseEnumData(
                            id=skill_category_id,
                            name=SkillCategoryEnum(skill_category_id).name
                        )
                        for skill_category_id in skill_.skill_category
                    ],
                    skill_type=ResponseEnumData(
                        id=skill_.skill_type,
                        name=SkillTypeEnum(skill_.skill_type).name)

                )
            )

        """
        Create personal detail for response
        """
        personal_detail_response = ProfilePersonalDetailsResponse(
            name=db_profile.personal_detail.name,
            date_of_birth=db_profile.personal_detail.date_of_birth,
            gender=ResponseEnumData(
                id=db_profile.personal_detail.gender,
                name=GenderEnum(db_profile.personal_detail.gender.value).name
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
                    name=DesignationStatusEnum(
                        db_profile.designation.designation_status
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
                        name=StatusEnum(experience.status).name
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
                name=ProfileStatusEnum(db_profile.profile_status).name
            )
        )
        return response

    @staticmethod
    async def _update_user_profile_by_user(profile_request: ProfileBasicRequest) -> ProfileResponse:
        profile_crud_manager = ProfileRepository()
        old_profile: Profiles = await profile_crud_manager.get(id_=profile_request.profile_id)  # type: ignore

        if old_profile is None:
            """
            Check if the profile exists in the database
            """
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You should provide a existing profile id of the user"
            )
        raise_http_exec = False
        try:
            email = profile_request.email
            raise_http_exec = True
        except AttributeError as attr_exec:
            pass

        if raise_http_exec:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address can not be edited"
            )
        try:
            profile_name = profile_request.name
        except AttributeError as attr_exec:
            profile_name = None

        try:
            designation_id = profile_request.designation_id
        except AttributeError as attr_exec:
            designation_id = None

        update_item = ProfileUpdateByUser(
            name=profile_name,
            date_of_birth=profile_request.date_of_birth,
            gender=profile_request.gender,
            mobile=profile_request.mobile,
            address=profile_request.address,
            designation_id=designation_id,
            about=profile_request.about)

        item_dict = update_item.dict(
            exclude_unset=True,
            exclude_none=True
        )
        if item_dict.get("designation_status") is not None:
            item_dict.pop("designation_status")
        if item_dict.get("designation_id") is not None:
            item_dict.pop("designation_id")
        old_profile_details = old_profile.personal_detail.dict()

        for key, value in item_dict.items():
            if key in old_profile_details:
                old_profile_details[key] = value
        if profile_request.designation_id is not None:
            designation: Designations = await Designations.get(profile_request.designation_id)
            db_profile: Profiles = await profile_crud_manager.update(  # type: ignore
                id_=profile_request.profile_id,  # type: ignore
                item_dict={
                    "personal_detail": old_profile_details,
                    "designation": {
                        'designation_id': designation.id,
                        'designation': designation.designation,
                        'designation_status': DesignationStatusEnum.inactive,
                        "end_date": None,
                        "start_date": None
                    }
                }
            )
        else:
            db_profile: Profiles = await profile_crud_manager.update(  # type: ignore
                id_=profile_request.profile_id,  # type: ignore
                item_dict={
                    "personal_detail": old_profile_details
                }
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
                        id=skill_.status,
                        name=StatusEnum(skill_.status).name
                    ),
                    achievements_description=skill_.achievements_description,
                    skill_category=[
                        ResponseEnumData(
                            id=skill_category_id,
                            name=SkillCategoryEnum(skill_category_id.value).name
                        )
                        for skill_category_id in skill_.skill_category
                    ],
                    skill_type=ResponseEnumData(
                        id=skill_.skill_type,
                        name=SkillTypeEnum(skill_.skill_type.value).name
                    )

                )
            )

            """
            Create personal detail for response
            """
        personal_detail_response = ProfilePersonalDetailsResponse(
            name=db_profile.personal_detail.name,
            date_of_birth=db_profile.personal_detail.date_of_birth,
            gender=ResponseEnumData(
                id=db_profile.personal_detail.gender,
                name=GenderEnum(db_profile.personal_detail.gender.value).name
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
                    name=DesignationStatusEnum(db_profile.designation.designation_status.value).name
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
                        name=StatusEnum(experience.status.value).name
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
                name=ProfileStatusEnum(db_profile.profile_status).name
            )
        )

        return response

    @staticmethod
    async def _create_user_profile_by_admin(profile_request: ProfileBasicForAdminRequest) -> ProfileResponse:
        if profile_request.email is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide email address"
            )
        if profile_request.name is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide name of the profile"
            )
        if profile_request.designation_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide designation of the profile"
            )

        designation: Designations = await Designations.get(profile_request.designation_id)  # type: ignore
        profile_status_object: ProfileStatus = await ProfileStatus.get(
            profile_request.profile_status.value)  # type: ignore
        personal_detail = ProfilePersonalDetails(
            name=profile_request.name,
            date_of_birth=profile_request.date_of_birth,
            gender=profile_request.gender,
            mobile=profile_request.mobile,
            about=None,
            address=None,
            experience_year=None
        )
        designation_status_object: DesignationStatus = await DesignationStatus.get(
            profile_request.designation_status.value  # type: ignore
        )

        gender_data: Gender = await Gender.get(profile_request.gender)  # type: ignore

        """
        Create profile experience based on the designation status
        """

        new_experience = []
        if profile_request.designation_status == DesignationStatusEnum.active:
            new_experience = [
                ProfileExperience(
                    experience_id=1,
                    company_name="iXora Solution Ltd.",
                    designation=ExperienceDesignation(designation=designation.designation,
                                                      designation_id=1),
                    start_date=None,
                    end_date=None,
                    job_responsibility=None
                )
            ]
        """
        Create profile object to insert into the database
        """

        db_profile = Profiles(
            user_id=profile_request.email,
            personal_detail=personal_detail,
            profile_status=profile_request.profile_status,
            designation=ProfileDesignation(
                designation_id=designation.id,
                designation=designation.designation,
                start_date=None, end_date=None,
                designation_status=profile_request.designation_status,
            ),
            skills=[],
            experiences=new_experience,
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
            name=profile_request.name,
            date_of_birth=profile_request.date_of_birth,
            gender=ResponseEnumData(
                id=gender_data.id,
                name=gender_data.name),
            mobile=profile_request.mobile,
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
            ] if new_experience else [],
            educations=[],
            personal_details=personal_detail_response,
            profile_status=ResponseEnumData(
                id=profile_status_object.id,
                name=profile_status_object.name
            )
        )
        return response

    @staticmethod
    async def _create_user_profile_by_user(profile_request: ProfileBasicRequest,
                                           email: str) -> ProfileResponse:
        if not email == profile_request.email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="You are not allowed to create/update other profiles")
        if profile_request.email is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide email address"
            )
        if profile_request.name is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide name of the profile"
            )
        if profile_request.designation_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide designation of the profile"
            )

        designation: Designations = await Designations.get(profile_request.designation_id)  # type: ignore

        personal_detail = ProfilePersonalDetails(
            name=profile_request.name,
            date_of_birth=profile_request.date_of_birth,
            gender=profile_request.gender,
            mobile=profile_request.mobile,
            about=None,
            address=None,
            experience_year=None
        )

        gender_data: Gender = await Gender.get(profile_request.gender)  # type: ignore

        """
        Create profile object to insert into the database
        # """
        db_profile = Profiles(
            user_id=profile_request.email,
            personal_detail=personal_detail,
            designation=ProfileDesignation(
                designation_id=designation.id,
                designation=designation.designation,
                start_date=None, end_date=None,
                designation_status=DesignationStatusEnum.inactive,
            ),
            skills=[],
            experiences=[],
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
            name=profile_request.name,
            date_of_birth=profile_request.date_of_birth,
            gender=ResponseEnumData(
                id=gender_data.id,
                name=gender_data.name),
            mobile=profile_request.mobile,
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
                    id=db_profile.designation.designation_status,
                    name=DesignationStatusEnum(db_profile.designation.designation_status).name
                ),
            ),
            skills=[],
            experiences=[],
            educations=[],
            personal_details=personal_detail_response,
            profile_status=ResponseEnumData(
                id=db_profile.profile_status,
                name=ProfileStatusEnum(db_profile.profile_status).name
            )
        )
        return response

    async def get_user_profiles_for_admin(self, *,
                                          skill_id=None,
                                          employee_name=None,
                                          mobile=None,
                                          email=None,
                                          profile_status=None,
                                          page_number,
                                          page_size):
        query = {}

        if skill_id is not None:
            query = ElemMatch(
                Profiles.skills,
                {
                    "skill_id": skill_id
                }
            )
        elif employee_name is not None:
            query = {
                "personal_detail.name":
                    {
                        '$regex': employee_name, '$options': 'i'
                    }
            }

        elif mobile is not None:
            query = {
                "personal_detail.mobile":
                    {
                        '$regex': mobile, '$options': 'i'
                    }
            }
        elif email is not None:
            query = {
                "user_id":
                    {
                        '$regex': email, '$options': 'i'
                    }
            }
        if profile_status is not None:
            query["profile_status"] = profile_status

        db_profiles = await Profiles.find(query).skip((page_number - 1) * page_size).limit(page_size).to_list()
        count = await (Profiles.find(query).count())
        response = [
            ProfileBasicResponse(
                id=db_profile.id,
                email=db_profile.user_id,
                designation=DesignationDataResponse(
                    designation_id=db_profile.designation.designation_id,
                    designation=db_profile.designation.designation
                ),
                skills=[
                    ProfileSkillDataResponse(
                        skill_id=skill.skill_id,
                        experience_year=skill.experience_year,
                        level=skill.level,
                        skill_name=skill.skill_name
                    ) for skill in db_profile.skills if skill.status == StatusEnum.active
                                                        or skill.status == StatusEnum.cancel
                ],
                mobile=db_profile.personal_detail.mobile,
                name=db_profile.personal_detail.name,
                url=f"/admin/user-profiles/%s" % (str(db_profile.id))
            ) for db_profile in db_profiles]
        return PaginatedProfileResponse(

            previous_page=page_number - 1 if page_number > 1 else None,
            next_page=page_number + 1 if page_number * page_size < count else None,
            has_previous=page_number > 1,
            has_next=page_number * page_size < count,
            total_items=count,
            pages=(count // page_size + 1) if count % page_size > 0 else count // page_size,
            items=response)
