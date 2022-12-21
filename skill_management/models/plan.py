from datetime import datetime, date
from typing import Any

from beanie import Document, Link
from pydantic import Field, validator

from skill_management.enums import PlanTypeEnum, StatusEnum
from skill_management.models.profile import Profiles
from skill_management.models.skill import Skills
from skill_management.schemas.plan import Task


class Plans(Document):
    skill: Link[Skills]
    profile: Link[Profiles]
    plan_type: PlanTypeEnum = Field(PlanTypeEnum.course, description="the type of the plan")
    notes: str|None = Field(max_length=255, description="notes on the plan")
    start_date: date | None = Field(description="start date of plan")
    end_date: date | None = Field(description="end date of plan")
    task: list[Task]|None
    status: StatusEnum = Field(StatusEnum.active, description="status of skill from fixed list of values")

    @validator("end_date", always=True)
    def validate_end_date(cls, value: date, values: dict[str, Any]) -> date | None:
        if values["start_date"] is None:
            return None
        if values["start_date"] > value:
            raise ValueError("end_date must be greater than start_date")
        return value

    class Settings:
        use_revision = True
        use_state_management = True
        validate_on_save = True
