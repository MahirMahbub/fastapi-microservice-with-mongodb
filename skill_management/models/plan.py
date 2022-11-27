from datetime import datetime
from typing import Any

from beanie import Document, Link
from pydantic import Field, validator

from skill_management.enums import PlanTypeEnum
from skill_management.models.profile import Profiles
from skill_management.models.skill import Skills
from skill_management.schemas.plan import Task


class Plans(Document):
    skill: Link[Skills]
    profile_id: Link[Profiles]
    plan_type: PlanTypeEnum
    notes: str = Field(max_length=255, description="notes on the plan")
    start_date: datetime | None = Field(description="start date of plan")
    end_date: datetime | None = Field(description="end date of plan")
    task: list[Task]

    @validator("end_date", always=True)
    def validate_end_date(cls, value: datetime, values: dict[str, Any]) -> datetime | None:
        if values["start_date"] is None:
            return None
        if values["start_date"] > value:
            raise ValueError("end_date must be greater than start_date")
        return value

    class Settings:
        use_revision = True
        use_state_management = True
        validate_on_save = True
