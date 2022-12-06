from typing import cast

from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError

from skill_management.enums import PlanTypeEnum, StatusEnum
from skill_management.models.plan import Plans
from skill_management.models.skill import Skills
from skill_management.repositories.plan import PlanRepository
from skill_management.repositories.profile import ProfileRepository
from skill_management.repositories.skill import SkillRepository
from skill_management.schemas.base import ResponseEnumData
from skill_management.schemas.plan import PlanCreateRequest, PlanCreateResponse, Task, TaskResponse


class PlanService:
    async def create_or_update_plan_by_user(self, plan_request: PlanCreateRequest,
                                            email: str | None) -> PlanCreateResponse:
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Authentication failed")
        if plan_request.plan_id is not None:
            """
            It is an update operation
            """
            return await self._update_plan_by_user(plan_request, email)
        else:
            """
            It is a create operation
            """
            return await self._create_plan_by_user(plan_request, email)

    async def _update_plan_by_user(self, plan_request: PlanCreateRequest, email: str):
        profile_crud_manager = ProfileRepository()
        old_profile = await profile_crud_manager.get_by_query(
            query={
                "user_id": email
            }
        )

        if old_profile is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="You are not allowed to update the user profile")
        plan_crud_manager = PlanRepository()
        old_plan = cast(Plans, await plan_crud_manager.get_by_query({"_id": plan_request.plan_id}))
        skill: Skills = cast(Skills, old_plan.skill)
        if plan_request.skill_id is not None:
            skill_crud_manager = SkillRepository()
            skill = cast(Skills, await skill_crud_manager.get_by_query({"_id": plan_request.skill_id}))
            if skill is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail="Must provide a valid skill id")
        tasks: list[Task] = old_plan.task
        if plan_request.task is not None or not plan_request.task == []:

            all_task_ids = [
                task.id for task in old_plan.task
            ]
            if not all_task_ids:
                new_start_task_id = 1
            else:
                new_start_task_id = max(all_task_ids) + 1
            new_task_list = []
            for data in plan_request.task:
                new_task_list.append(
                    Task(
                        id=new_start_task_id,
                        description=data.description,
                        status=data.status
                    )
                )
                new_start_task_id += 1
            tasks += new_task_list
        if plan_request.delete_tasks:
            for task_id in plan_request.delete_tasks:
                for index in range(len(tasks)):
                    if tasks[index].id == task_id:
                        tasks[index].status = StatusEnum.delete
        item_dict = plan_request.dict(exclude_unset=True, exclude_none=True)
        item_dict.pop("plan_id")
        item_dict.pop("delete_tasks")
        item_dict["task"] = tasks
        item_dict["skill"] = skill
        item_dict["profile"] = old_profile

        db_plan = cast(
            Plans, await plan_crud_manager.update_by_query(
                query={
                    "_id": old_plan.id
                },
                item_dict=item_dict
            )
        )
        plan_type = cast(PlanTypeEnum | None, db_plan.plan_type)
        plan_response = PlanCreateResponse(
            id=str(db_plan.id),
            plan_type=ResponseEnumData(id=plan_type, name=PlanTypeEnum(plan_type).name),
            notes=db_plan.notes,
            skill_id=db_plan.skill.id,
            task=[
                TaskResponse(
                    id=data.id,
                    description=data.description,
                    status=ResponseEnumData(
                        id=data.status,
                        name=StatusEnum(data.status).name
                    )
                ) for data in db_plan.task],
            start_date=db_plan.start_date,
            end_date=db_plan.end_date,
            status=ResponseEnumData(id=db_plan.status,
                                    name=StatusEnum(db_plan.status).name)
        )
        return plan_response

    async def _create_plan_by_user(self, plan_request: PlanCreateRequest, email: str):
        profile_crud_manager = ProfileRepository()
        profile_plans = await profile_crud_manager.get_by_query(
            query={
                "user_id": email
            }
        )

        if profile_plans is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="You are not allowed to update the user profile")
        skill_crud_manager = SkillRepository()
        skill = await skill_crud_manager.get_by_query({"_id": plan_request.skill_id})
        plan = Plans(
            profile=profile_plans,
            plan_type=plan_request.plan_type,
            notes=plan_request.notes,
            start_date=plan_request.start_date,
            end_date=plan_request.end_date,
            skill=skill,
            status=plan_request.status,
            task=[
                Task(
                    id=indx + 1,
                    description=data.description,
                    status=data.status
                ) for indx, data in enumerate(plan_request.task)
            ]
        )
        plan_crud_manager = PlanRepository()
        try:
            db_plan = cast(Plans, await plan_crud_manager.insert(plan))
        except DuplicateKeyError as duplicate_key_exec:
            duplicate_values = duplicate_key_exec.details["keyValue"].values()  # type: ignore
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Duplicate Value is not allowed. " + ", ".join(
                                    duplicate_values) + " already exists")
        plan_type = cast(PlanTypeEnum | None, db_plan.plan_type)
        plan_response = PlanCreateResponse(
            id=str(db_plan.id),
            plan_type=ResponseEnumData(id=plan_type, name=PlanTypeEnum(plan_type).name),
            notes=db_plan.notes,
            skill_id=db_plan.skill.id,
            task=[
                TaskResponse(
                    id=data.id,
                    description=data.description,
                    status=ResponseEnumData(
                        id=data.status,
                        name=StatusEnum(data.status).name
                    )
                ) for data in db_plan.task],
            start_date=db_plan.start_date,
            end_date=db_plan.end_date,
            status=ResponseEnumData(id=db_plan.status,
                                    name=StatusEnum(db_plan.status).name)
        )
        return plan_response
