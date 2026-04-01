from typing import Any, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class RoadmapRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    gpa: float = Field(..., ge=0, le=5)
    grade: str = Field(..., min_length=1, max_length=100)
    interests: str = Field(..., min_length=1, max_length=2000)
    activities: Optional[str] = Field(default=None, max_length=2000)
    demographic: Optional[str] = Field(
        default=None,
        max_length=1000,
        validation_alias=AliasChoices("demographic", "demographics"),
    )
    testing: Optional[str] = Field(default=None, max_length=1000)
    college_goals: Optional[str] = Field(
        default=None,
        max_length=1000,
        validation_alias=AliasChoices("collegeGoals", "college_goals"),
    )
    classes: Optional[str] = Field(default=None, max_length=2000)
    location: Optional[str] = Field(default=None, max_length=500)


class RoadmapResponse(BaseModel):
    roadmap: dict[str, Any]
    id: Optional[str] = None
    warning: Optional[str] = None


class RoadmapListResponse(BaseModel):
    roadmaps: list[dict[str, Any]]


class RoadmapDetailResponse(BaseModel):
    roadmap: dict[str, Any]


class DeleteResponse(BaseModel):
    message: str
    id: str
