from typing import Any, Optional

from pydantic import BaseModel, Field


class EssayRequest(BaseModel):
    grade: str = Field(..., min_length=1, max_length=100)
    prompt: str = Field(..., min_length=1, max_length=3000)
    essay: str = Field(..., min_length=1, max_length=25000)
    program: str = Field(..., min_length=1, max_length=500)
    word_limit: Optional[int] = Field(default=None, ge=1, le=10000)


class EssayResponse(BaseModel):
    feedback: dict[str, Any]
    id: Optional[str] = None
    warning: Optional[str] = None


class EssayListResponse(BaseModel):
    essays: list[dict[str, Any]]


class EssayDetailResponse(BaseModel):
    essay: dict[str, Any]
