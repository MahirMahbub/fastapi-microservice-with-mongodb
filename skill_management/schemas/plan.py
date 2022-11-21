import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Any

from pydantic import BaseModel, Field, validator, UUID4

from skill_management.enums import PlanEnum, StatusEnum
from skill_management.schemas.base import EnumData


class TaskBase(BaseModel):
    description: str = Field(max_length=255, description="description of task")
    start_date: datetime = Field(description="start date of task")
    end_date: datetime = Field(description="end date of task, must be none or greater than start_date")

    @validator("end_date", always=True)
    def validate_end_date(cls, value: datetime, values: dict[str, Any]) -> Optional[datetime]:
        if values["start_date"] is None:
            return None
        if values["start_date"] > value:
            raise ValueError("end_date must be greater than start_date")
        return value


class TaskCreate(TaskBase):
    status: str = Field(max_length=10, description="status of task")

    @validator("status", always=True)
    def validate_status(cls, value: str) -> Optional[str]:
        if value not in [data.name for data in StatusEnum]:
            raise ValueError("status must be valid")
        return value


class TaskResponse(TaskBase):
    id: int = Field(gt=0, description="Autoincrement id of task")
    status: EnumData = Field(description="status of skill from fixed list of values")


class PlanBase(BaseModel):
    plan_type: PlanEnum = Field(description="Fixed plan type in int-enum")
    notes: Optional[str] = Field(max_length=255, description="notes for plan")


class PlanRequest(PlanBase):
    skill_id: int = Field(gt=0, description="skill_id is related to skill collection")
    profile_id: int = Field(gt=0, description="profile_id is related to profile collection")
    task: list[TaskCreate] = []

    class Config:
        # validate_assignment = True
        schema_extra = {
            "example": {
                "plan_type": 1,
                "notes": "It is a note for the planning",
                "skill_id": 1,
                "profile_id": 1,
                "task": [
                    {
                        "description": "It is a task for the planning",
                        "start_date": datetime.now(timezone.utc),
                        "end_date": datetime.now(timezone.utc) + timedelta(days=1),
                        "status": "active"
                    }
                ]
            }
        }

    # @validator("task")
    # def set_task(cls, tasks: None | list[TaskBase]) -> Sequence[Optional[TaskBase]]:
    #     return tasks or []


class PlanResponse(BaseModel):
    id: UUID4
    plan_type: EnumData = Field(description="Fixed plan type")
    notes: Optional[str] = Field(max_length=255, description="notes for plan")
    skill_id: int = Field(gt=0, description="skill_id is related to skill collection")
    profile_id: int = Field(gt=0, description="profile_id is related to profile collection")
    task: list[TaskResponse] = Field([], description="task list for plan")

    class Config:
        schema_extra = {
            "example": {
                "id": uuid.uuid4(),
                "plan_type": {
                    "id": 1,
                    "name": "course"
                },
                "notes": "It is a note for the planning",
                "skill_id": 1,
                "profile_id": 1,
                "task": [
                    {
                        "id": 1,
                        "description": "It is a task for the planning",
                        "start_date": datetime.now(timezone.utc),
                        "end_date": datetime.now(timezone.utc) + timedelta(days=1),
                        "status": {
                            "id": 1,
                            "name": "active"
                        }
                    }
                ]

            }
        }

        id: int = Field(gt=0, description="Autoincrement id of task")
        description: str = Field(max_length=255, description="description of task")
        start_date: datetime = Field(description="start date of task")
        end_date: datetime = Field(description="end date of task, must be none or greater than start_date")
        status: StatusEnum = Field(description="status of task")
