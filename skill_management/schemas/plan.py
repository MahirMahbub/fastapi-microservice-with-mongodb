from datetime import datetime, timedelta, timezone, date
from typing import Optional, Any

from beanie import PydanticObjectId
from pydantic import BaseModel, Field, validator, UUID4, root_validator

from skill_management.enums import PlanTypeEnum, StatusEnum, UserStatusEnum, TaskStatusEnum
from skill_management.schemas.base import ResponseEnumData


class TaskBase(BaseModel):
    description: str = Field(max_length=255, description="description of task")


class TaskCreate(TaskBase):
    task_id: int | None = Field(None, description="id of task for plan creation ")
    status: TaskStatusEnum | None = Field(None, description="""status of task
    
    1: complete, 2: incomplete, 3: delete""")
    description: str = Field(default="", max_length=255, description="description of task")
    duration: int | None = Field(None, description="duration of task in hours")
    spend_time: int | None = Field(None, description="spend time of task in hours")

    # @validator("status", always=True)
    # def validate_status(cls, value: str) -> str | None:
    #     if value not in [data.name for data in StatusEnum]:
    #         raise ValueError("status must be valid")
    #     return value


class TaskResponse(BaseModel):
    description: str | None = Field(max_length=255, description="description of task")
    id: int | None = Field(ge=1, description="autoincrement id of task")
    status: ResponseEnumData | None = Field(description="status of skill from fixed list of values")
    duration: int | None = Field(None, description="duration of task in hours")
    spend_time: int | None = Field(None, description="spend time of task in hours")


class Task(BaseModel):
    id: int = Field(ge=1, description="autoincrement id of task")
    description: str | None = Field(max_length=255, description="description of task")
    status: TaskStatusEnum = Field(TaskStatusEnum.incomplete, description="status of skill from fixed list of values")
    duration: int | None = Field(None, description="duration of task in hours")
    spend_time: int | None = Field(None, description="spend time of task in hours")


class PlanBase(BaseModel):
    plan_type: PlanTypeEnum | None = Field(None, description='''the type of the plan
    
    1: course, 2: exam''')
    notes: str | None = Field(None, max_length=2000, description="notes for plan")


class PlanCreateRequest(PlanBase):
    plan_id: PydanticObjectId|None = Field(default=None, description="id for plan")
    skill_id: int | None = Field(gt=0, description="skill_id is related to skill collection")
    task: list[TaskCreate] | None = []
    start_date: date | None = Field(None, description="start date of plan")
    end_date: date | None = Field(None, description='''end date of plan
    
    > start_date''')
    # delete_tasks: list[int] | None = Field(None, description="list of task id to delete")
    status: UserStatusEnum | None = Field(UserStatusEnum.active, description="""status of plan
    
    1: active, 3: delete""")

    @root_validator
    def any_of(cls, v: dict[str, Any]) -> dict[str, Any]:
        plan_id = v.pop('plan_id')
        if plan_id is None:
            notes = v.pop('notes')
            task = v.pop('task')
            # delete_tasks = v.pop('delete_tasks')
            if None in v.values():
                raise ValueError('You must provide skill_id, start_date, end_date, plan_type for creating a plan')
            v["notes"] = notes
            v["task"] = task
        v["plan_id"] = plan_id
        return v

    @validator("end_date", always=True)
    def validate_end_date(cls, value: date, values: dict[str, Any]) -> date | None:
        if values["start_date"] is None:
            return None
        if values["start_date"] > value:
            raise ValueError("end_date must be greater than start_date")
        return value

    # @validator("plan_type", always=True)
    # def validate_plan_type(cls, value: str) -> str | None:
    #     if value not in [data.name for data in PlanTypeEnum]:
    #         raise ValueError("status must be valid")
    #     return value


class PlanCreateAdminRequest(PlanCreateRequest):
    profile_id: PydanticObjectId = Field(description="profile_id is related to profile collection")


class PlanCreateResponse(BaseModel):
    id: UUID4 | None | str| PydanticObjectId = Field(description="id of plan of type UUID")
    skill_name: str|None = Field(description="skill name of plan")
    skill_type: ResponseEnumData|None = Field(description="skill type of plan")
    plan_type: ResponseEnumData | None = Field(description="Fixed plan type")
    notes: str | None = Field(max_length=2000, description="notes for plan")
    skill_id: int | None = Field(gt=0, description="skill_id is related to skill collection")
    # profile_id: int | None = Field(gt=0, description="profile_id is related to profile collection")
    task: list[TaskResponse] | None = Field([], description="task list for plan")
    start_date: date | None = Field(description="start date of plan")
    end_date: date | None = Field(description="end date of plan, must be none or greater than start_date")
    status: ResponseEnumData | None = Field(description="status of plan from fixed list of values")

    @validator("end_date", always=True)
    def validate_end_date(cls, value: date, values: dict[str, Any]) -> date|None:
        if values["start_date"] is None:
            return None
        if values["start_date"] > value:
            raise ValueError("end_date must be greater than start_date")
        return value

    class Config:
        schema_extra = {
            "example":
                {
                    "id": "954eba99-b1ec-4c1f-b5b1-3cc9db9e59e0",
                    "plan_type":
                        {
                            "id": 1,
                            "name": "course"
                        },
                    "notes": "It is a note for the planning",
                    "skill_id": 1,
                    "profile_id": 1,
                    "start_date": datetime.now(timezone.utc).date(),
                    "end_date": datetime.now(timezone.utc).date() + timedelta(days=1),
                    "task":
                        [
                            {
                                "id": 1,
                                "description": "It is a task for the planning",
                                "duration": 4,
                                "time_spend": 3,
                                "status":
                                    {
                                        "id": 1,
                                        "name": "incomplete"
                                    }
                            }
                        ]

                }
        }

        # id: int = Field(gt=0, description="Autoincrement id of task")
        # description: str = Field(max_length=255, description="description of task")
        # start_date: datetime = Field(description="start date of task")
        # end_date: datetime = Field(description="end date of task, must be none or greater than start_date")
        # status: StatusEnum = Field(description="status of task")


class PlanListDataResponse(BaseModel):
    plans: list[PlanCreateResponse]
