from pydantic import BaseModel, Field


class candidate(BaseModel):
    name: str = Field(description="Name of the candidate")
    age: int = Field(description="Age of the candidate")
    city: str = Field(description="City where the candidate lives")
    experience_years: int = Field(description="Years of professional experience")
    skills: list[str] = Field(description="List of candidate's skills")