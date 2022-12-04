from fastapi import HTTPException, status

from skill_management.enums import FileTypeEnum, SkillCategoryEnum, SkillTypeEnum, StatusEnum
from skill_management.models.enums import Status
from skill_management.models.file import Files
from skill_management.models.profile import Profiles
from skill_management.models.skill import Skills
from skill_management.repositories.profile import ProfileRepository
from skill_management.repositories.skill import SkillRepository
from skill_management.schemas.base import ResponseEnumData
from skill_management.schemas.file import FileResponse
from skill_management.schemas.profile import ProfileSkillView
from skill_management.schemas.skill import CreateSkillDataRequest, ProfileSkill, CreateSkillDataResponse, \
    CreateSkillListDataResponse


class SkillService:
    async def create_or_update_skill_by_user(self, email: str, skill_request: CreateSkillDataRequest):
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
            query={"user_id": email})  # type: ignore
        # projection_model=ProfileSkillView)
        if profile_skill is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="You are not allowed to update the user profile")

        if profile_skill.skills is None or profile_skill.skills == []:
            """
             It is  a create operation. 
            """
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
            skill_request_dict = {"skills.$." + str(key): val for key, val in skill_request_dict.items()}
            db_profile: Profiles | None = await profile_crud_manager.update_by_query(  # type: ignore
                query={"skills.skill_id": skill_request.skill_id,
                       "_id": profile_skill.id},  # type: ignore
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


