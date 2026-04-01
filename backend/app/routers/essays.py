from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.rate_limit import limiter
from app.dependencies.auth import get_current_user
from app.repositories import essays as essay_repository
from app.schemas.essay import (
    EssayDetailResponse,
    EssayListResponse,
    EssayRequest,
    EssayResponse,
)
from app.schemas.roadmap import DeleteResponse
from app.services.essay_service import generate_and_store_essay_feedback

router = APIRouter(tags=["essays"])


@router.post("/essay", response_model=EssayResponse)
@limiter.limit("5/hour")
async def grade_essay(
    request: Request,
    payload: EssayRequest,
    current_user=Depends(get_current_user),
):
    return generate_and_store_essay_feedback(payload, str(current_user.id))


@router.get("/essays", response_model=EssayListResponse)
async def get_essays(current_user=Depends(get_current_user)):
    try:
        essays = essay_repository.list_essays(str(current_user.id))
        return EssayListResponse(essays=essays)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch essays") from exc


@router.get("/essays/{essay_id}", response_model=EssayDetailResponse)
async def get_essay(essay_id: str, current_user=Depends(get_current_user)):
    try:
        essay = essay_repository.get_essay(str(current_user.id), essay_id)
        if not essay:
            raise HTTPException(status_code=404, detail="Essay not found")
        return EssayDetailResponse(essay=essay)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch essay") from exc


@router.delete("/essays/{essay_id}", response_model=DeleteResponse)
async def delete_essay(essay_id: str, current_user=Depends(get_current_user)):
    try:
        deleted = essay_repository.delete_essay(str(current_user.id), essay_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Essay not found or unauthorized")
        return DeleteResponse(message="Essay deleted successfully", id=essay_id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to delete essay") from exc
