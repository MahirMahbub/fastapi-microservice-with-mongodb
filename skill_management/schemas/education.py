from datetime import date

from pydantic import BaseModel, Field, validator

class EducationBase(BaseModel):
    degree_name: str = Field(max_length=30, description="degree name of the user education")
    school_name: str = Field(max_length=30, description="school name of the user education")
    passing_year: str = Field(max_length=4, description="passing year of the user education")
    grade: float = Field(ge=2.5, le=5.0)

    @validator("passing_year", always=True)
    def validate_passing_year(cls, value: str) -> str:
        try:
            passing_year: int = int(value)
        except ValueError as val_exec:
            raise ValueError("Not a year")
        if not 1971 <= passing_year <= date.today().year:
            raise ValueError("Not a valid year, must be between 1970 and this year")
        return value

class EducationCreateRequest(EducationBase):
    class Config:
        schema_extra = {
            "example":
                {
                    "degree_name": "B.Sc in Computer Science",
                    "school_name": "University of Dhaka",
                    "passing_year": "2019",
                    "grade": 3.80
                }
        }

class ProfileEducationResponse(EducationBase):
    education_id: int = Field(gt=0, description="autoincrement id of the user education")


class EducationCreateResponse(ProfileEducationResponse):
    class Config:
        schema_extra = {
            "example":
                {
                    "education_id": 2,
                    "degree_name": "B.Sc in Computer Science",
                    "school_name": "University of Dhaka",
                    "passing_year": "2019",
                    "grade": 3.80
                },
        }
