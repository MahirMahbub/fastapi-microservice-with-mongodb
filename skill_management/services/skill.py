from typing import cast

from beanie import PydanticObjectId
from beanie.odm.operators.find.array import ElemMatch
from fastapi import HTTPException, status, UploadFile

from skill_management.enums import FileTypeEnum, SkillCategoryEnum, SkillTypeEnum, StatusEnum, UserStatusEnum, \
    ProfileStatusEnum
from skill_management.models.enums import Status
from skill_management.models.file import Files
from skill_management.models.profile import Profiles
from skill_management.models.skill import Skills
from skill_management.repositories.profile import ProfileRepository
from skill_management.repositories.skill import SkillRepository
from skill_management.schemas.base import ResponseEnumData
from skill_management.schemas.file import FileResponse, SkillCertificateResponse
from skill_management.schemas.profile import ProfileSkillView
from skill_management.schemas.skill import CreateSkillDataRequest, ProfileSkill, CreateSkillDataResponse, \
    CreateSkillListDataResponse, CreateSkillDataAdminRequest, ProfileSkillDetailsResponse, ProfileSkillResponse
from skill_management.services.file import FileService


class SkillService:
    @staticmethod
    async def create_or_update_skill_by_user(email: str, skill_request: CreateSkillDataRequest):
        skill_id = skill_request.skill_id
        """
        Check if the skill is valid
        """
        skill_crud_manager = SkillRepository()
        profile_crud_manager = ProfileRepository()
        skill_data: Skills | None = await skill_crud_manager.get_by_modified_id(skill_id)  # type: ignore
        if skill_data is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Must provide a valid skill")
        profile_skill: ProfileSkillView | None = await profile_crud_manager.get_by_query(
            query={"user_id": email},
            projection_model=ProfileSkillView)
        if profile_skill is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="You are not allowed to update the user profile")

        has_skill = await Profiles.find(
            {
                "user_id": email
            },
            ElemMatch(
                Profiles.skills, {"skill_id": skill_request.skill_id}
            ),
            projection_model=ProfileSkillView
        ).first_or_none()

        if has_skill is None:
            """
             It is  a create operation. 
            """
            new_skill = ProfileSkill(
                skill_id=skill_id,
                skill_type=skill_data.skill_type,
                skill_category=skill_data.skill_categories,
                skill_name=skill_data.skill_name,
                status=cast(StatusEnum, skill_request.status),
                experience_year=skill_request.experience_year,
                number_of_projects=skill_request.number_of_projects,
                level=skill_request.level, training_duration=skill_request.training_duration,
                achievements=skill_request.achievements,
                achievements_description=skill_request.achievements_description,
                certificate=skill_request.certificate,
                certificate_files=[])
            db_profile: Profiles | None = await profile_crud_manager.update(
                id_=profile_skill.id,  # type: ignore
                push_item={
                    "skills": new_skill.dict(
                        exclude_unset=True, exclude_none=True
                    )
                }
            )
            skill_list = []
            for skill_ in db_profile.skills:  # type: ignore
                certificate_files = [
                    FileResponse(
                        file_name=file,
                        url="/files/%s" % file.id
                    ) async for file in Files.find(
                        {
                            "owner": db_profile.id,  # type: ignore
                            "file_type": FileTypeEnum.certificate
                        }
                    )
                ]
                skill_status_object: Status = await Status.get(skill_.status.value)  # type: ignore
                skill_list.append(
                    CreateSkillDataResponse(
                        skill_id=skill_.skill_id,
                        skill_name=skill_.skill_name,
                        experience_year=skill_.experience_year,
                        number_of_projects=skill_.number_of_projects,
                        level=skill_.level,
                        training_duration=skill_.training_duration,
                        achievements=skill_.achievements,
                        certificate=skill_.certificate,
                        status=ResponseEnumData(
                            id=skill_status_object.id,
                            name=(StatusEnum(skill_status_object.id)).name
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
                            name=SkillTypeEnum(skill_.skill_type).name
                        ),
                        certificates_url=certificate_files
                    )

                )
            return CreateSkillListDataResponse(skills=skill_list)
        else:
            skill_request_dict = skill_request.dict(exclude_unset=True, exclude_defaults=True)
            skill_request_dict.pop('skill_id')
            skill_request_dict = {"skills.$." + str(key): val for key, val in skill_request_dict.items()}
            db_profile: Profiles | None = await profile_crud_manager.update_by_query(  # type: ignore
                query={
                    "skills.skill_id": skill_request.skill_id,
                    "_id": profile_skill.id
                },
                item_dict=skill_request_dict
            )

            skill_list = []
            for skill_ in db_profile.skills:  # type: ignore
                certificate_files = [
                    FileResponse(
                        file_name=file.file_name,
                        url="/files/%s" % file.id
                    ) async for file in Files.find(
                        {
                            "owner": db_profile.id,  # type: ignore
                            "file_type": FileTypeEnum.certificate
                        }
                    )
                ]
                skill_status_object: Status = await Status.get(skill_.status.value)  # type: ignore
                skill_list.append(
                    CreateSkillDataResponse(
                        skill_id=skill_.skill_id,
                        skill_name=skill_.skill_name,
                        experience_year=skill_.experience_year,
                        number_of_projects=skill_.number_of_projects,
                        level=skill_.level,
                        training_duration=skill_.training_duration,
                        achievements=skill_.achievements,
                        certificate=skill_.certificate,
                        status=ResponseEnumData(
                            id=skill_status_object.id,
                            name=(StatusEnum(skill_status_object.id)).name
                        ),
                        certificates_url=certificate_files,
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
                            name=SkillTypeEnum(skill_.skill_type).name
                        )
                    )

                )
            return CreateSkillListDataResponse(skills=skill_list)

    @staticmethod
    async def create_or_update_skill_by_admin(skill_request: CreateSkillDataAdminRequest):
        skill_id = skill_request.skill_id
        """
        Check if the skill is valid
        """
        skill_crud_manager = SkillRepository()
        profile_crud_manager = ProfileRepository()
        skill_data: Skills | None = await skill_crud_manager.get_by_modified_id(skill_id)  # type: ignore
        if skill_data is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Must provide a valid skill")
        profile_skill: ProfileSkillView | None = await profile_crud_manager.get_by_query(
            query={
                "_id": skill_request.profile_id
            })  # type: ignore
        # projection_model=ProfileSkillView)
        if profile_skill is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="You are not allowed to update the user profile")
        has_skill = await Profiles.find(
            {
                "_id": skill_request.profile_id
            },
            ElemMatch(Profiles.skills, {"skill_id": skill_request.skill_id})).first_or_none()

        if has_skill is None:
            """
             It is  a create operation. 
            """
            # try:
            new_skill = ProfileSkill(
                skill_id=skill_id,
                skill_type=skill_data.skill_type,
                skill_category=skill_data.skill_categories,
                skill_name=skill_data.skill_name,
                status=skill_request.status,  # type: ignore
                experience_year=skill_request.experience_year,
                number_of_projects=skill_request.number_of_projects,
                level=skill_request.level, training_duration=skill_request.training_duration,
                achievements=skill_request.achievements,  # type: ignore
                achievements_description=skill_request.achievements_description,
                certificate=skill_request.certificate,  # type: ignore
                certificate_files=[])
            # except ValueError as val_exec:
            #     raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(val_exec))
            db_profile: Profiles | None = await profile_crud_manager.update(
                id_=profile_skill.id,  # type: ignore
                push_item={
                    "skills": new_skill.dict(
                        exclude_unset=True, exclude_none=True
                    )
                }
            )
            skill_list = []
            for skill_ in db_profile.skills:  # type: ignore
                certificate_files = [
                    FileResponse(
                        file_name=file,
                        url="/files/%s" % file.id
                    ) async for file in Files.find(
                        {
                            "owner": db_profile.id,  # type: ignore
                            "file_type": FileTypeEnum.certificate
                        }
                    )
                ]
                skill_status_object: Status = await Status.get(skill_.status.value)  # type: ignore
                skill_list.append(
                    CreateSkillDataResponse(
                        skill_id=skill_.skill_id,
                        skill_name=skill_.skill_name,
                        experience_year=skill_.experience_year,
                        number_of_projects=skill_.number_of_projects,
                        level=skill_.level,
                        training_duration=skill_.training_duration,
                        achievements=skill_.achievements,
                        certificate=skill_.certificate,
                        status=ResponseEnumData(
                            id=skill_status_object.id,
                            name=(StatusEnum(skill_status_object.id)).name
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
                            name=SkillTypeEnum(skill_.skill_type).name
                        )
                    )

                )
            return CreateSkillListDataResponse(skills=skill_list)
        else:
            skill_request_dict = skill_request.dict(exclude_unset=True, exclude_defaults=True)
            skill_request_dict.pop("profile_id")
            skill_request_dict = {"skills.$." + str(key): val for key, val in skill_request_dict.items()}
            db_profile: Profiles | None = await profile_crud_manager.update_by_query(  # type: ignore
                query={
                    "skills.skill_id": skill_request.skill_id,
                    "_id": profile_skill.id
                },  # type: ignore
                item_dict=skill_request_dict
            )

            skill_list = []
            for skill_ in db_profile.skills:  # type: ignore
                certificate_files = [
                    FileResponse(
                        file_name=file,
                        url="/files/%s" % file.id
                    ) async for file in Files.find(
                        {
                            "owner": db_profile.id,  # type: ignore
                            "file_type": FileTypeEnum.certificate
                        }
                    )
                ]
                skill_status_object: Status = await Status.get(skill_.status.value)  # type: ignore
                skill_list.append(
                    CreateSkillDataResponse(
                        skill_id=skill_.skill_id,
                        skill_name=skill_.skill_name,
                        experience_year=skill_.experience_year,
                        number_of_projects=skill_.number_of_projects,
                        level=skill_.level,
                        training_duration=skill_.training_duration,
                        achievements=skill_.achievements,
                        certificate=skill_.certificate,
                        status=ResponseEnumData(
                            id=skill_status_object.id,
                            name=(StatusEnum(skill_status_object.id)).name
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
                            name=SkillTypeEnum(skill_.skill_type).name
                        )
                    )

                )
            return CreateSkillListDataResponse(skills=skill_list)

    async def upload_certificate(self, skill_id: int,
                                 files: list[UploadFile],
                                 email: str):
        """
        Create a certificate for a skill
        """
        skill_crud_manager = SkillRepository()
        skill_data: Skills | None = await skill_crud_manager.get_by_query({"_id": skill_id})
        if skill_data is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Must provide a valid skill id")
        file_service = FileService()
        successful_files = []
        failed_files = []
        for file in files:
            file_response = await file_service.create_certificate(
                file=file,
                skill_id=skill_id,
                email=email,
                file_status=cast(UserStatusEnum, StatusEnum.active))

            if file_response is None:
                failed_files.append(file.filename)
            else:
                successful_files.append(file.filename)
        return SkillCertificateResponse(succeed_upload_list=successful_files, failed_upload_list=failed_files)

    async def get_skill_details_by_admin(self, profile_id: PydanticObjectId) -> ProfileSkillDetailsResponse:
        query = {
            '_id': profile_id,
        }
        db_profiles = await Profiles.find(
            query,
            projection_model=ProfileSkillView
        ).first_or_none()
        if db_profiles is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Must provide a valid profile id")
        certificate_files = await Files.find(
            {
                "file_type": FileTypeEnum.certificate,
                "owner": profile_id,
                "status": {"$in": [StatusEnum.active, StatusEnum.cancel]}
            }
        ).to_list()

        return ProfileSkillDetailsResponse(
            skills=[
                ProfileSkillResponse(
                    skill_id=data.skill_id,
                    skill_type=ResponseEnumData(
                        id=data.skill_type,
                        name=SkillTypeEnum(data.skill_type).name
                    ),
                    skill_category=[
                        ResponseEnumData(
                            id=category_data,
                            name=SkillTypeEnum(category_data).name
                        ) for category_data in data.skill_category
                    ],
                    skill_name=data.skill_name,
                    status=ResponseEnumData(
                        id=data.status,
                        name=StatusEnum(data.status).name
                    ),
                    certificate_files=[
                        FileResponse(
                            file_name=file_data.file_name,
                            url="/admin/files/response/" + str(file_data.id),
                            status=ResponseEnumData(
                                id=file_data.status,
                                name=StatusEnum(file_data.status).name
                            )
                        ) for file_data in certificate_files
                    ],
                    experience_year=data.experience_year,
                    number_of_projects=data.number_of_projects,
                    level=data.level,
                    training_duration=data.training_duration,
                    achievements=data.achievements,
                    achievements_description=data.achievements_description, certificate=data.certificate
                )
                for data in db_profiles.skills if data.status in [
                    StatusEnum.active, StatusEnum.cancel
                ]
            ]
        )

    async def get_skill_details_by_user(self, email: str) -> ProfileSkillDetailsResponse:
        query = {
            'user_id': email,
        }
        db_profiles: ProfileSkillView = cast(
            ProfileSkillView, await Profiles.find(
                query,
                projection_model=ProfileSkillView
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
        certificate_files = await Files.find(
            {
                "file_type": FileTypeEnum.certificate,
                "owner": db_profiles.id,
                "status": StatusEnum.active
            }
        ).to_list()

        return ProfileSkillDetailsResponse(
            skills=[
                ProfileSkillResponse(
                    skill_id=data.skill_id,
                    skill_type=ResponseEnumData(
                        id=data.skill_type,
                        name=SkillTypeEnum(data.skill_type).name
                    ),
                    skill_category=[
                        ResponseEnumData(
                            id=category_data,
                            name=SkillTypeEnum(category_data).name
                        ) for category_data in data.skill_category
                    ],
                    skill_name=data.skill_name,
                    status=ResponseEnumData(
                        id=data.status,
                        name=StatusEnum(data.status).name
                    ),
                    certificate_files=[
                        FileResponse(
                            file_name=file_data.file_name,
                            url="/profile/files/response/" + str(file_data.id),
                            status=ResponseEnumData(
                                id=file_data.status,
                                name=StatusEnum(file_data.status).name
                            )
                        ) for file_data in certificate_files
                    ],
                    experience_year=data.experience_year,
                    number_of_projects=data.number_of_projects,
                    level=data.level,
                    training_duration=data.training_duration,
                    achievements=data.achievements,
                    achievements_description=data.achievements_description, certificate=data.certificate
                )
                for data in db_profiles.skills if data.status == StatusEnum.active
            ]
        )
