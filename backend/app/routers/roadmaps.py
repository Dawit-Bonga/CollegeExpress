from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.rate_limit import limiter
from app.dependencies.auth import get_current_user
from app.repositories import roadmaps as roadmap_repository
from app.schemas.roadmap import (
    DeleteResponse,
    RoadmapDetailResponse,
    RoadmapListResponse,
    RoadmapRequest,
    RoadmapResponse,
)
from app.services.roadmap_service import generate_and_store_roadmap

router = APIRouter(tags=["roadmaps"])


@router.post("/generate", response_model=RoadmapResponse)
@limiter.limit("3/minute")
async def generate_roadmap(
    request: Request,
    payload: RoadmapRequest,
    current_user=Depends(get_current_user),
):
    return generate_and_store_roadmap(payload, str(current_user.id))


@router.get("/roadmaps", response_model=RoadmapListResponse)
async def get_roadmaps(current_user=Depends(get_current_user)):
    try:
        roadmaps = roadmap_repository.list_roadmaps(str(current_user.id))
        return RoadmapListResponse(roadmaps=roadmaps)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch roadmaps") from exc


@router.get("/roadmaps/{roadmap_id}", response_model=RoadmapDetailResponse)
async def get_roadmap(roadmap_id: str, current_user=Depends(get_current_user)):
    try:
        roadmap = roadmap_repository.get_roadmap(str(current_user.id), roadmap_id)
        if not roadmap:
            raise HTTPException(status_code=404, detail="Roadmap not found")
        return RoadmapDetailResponse(roadmap=roadmap)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch roadmap") from exc


@router.delete("/roadmaps/{roadmap_id}", response_model=DeleteResponse)
async def delete_roadmap(roadmap_id: str, current_user=Depends(get_current_user)):
    try:
        deleted = roadmap_repository.delete_roadmap(str(current_user.id), roadmap_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Roadmap not found or unauthorized")
        return DeleteResponse(message="Roadmap deleted successfully", id=roadmap_id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to delete roadmap") from exc
