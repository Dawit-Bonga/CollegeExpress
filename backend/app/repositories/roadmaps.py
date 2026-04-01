from typing import Optional

from app.core.clients import get_supabase_client
from app.schemas.roadmap import RoadmapRequest


def create_roadmap(user_id: str, payload: RoadmapRequest, roadmap_content: str) -> str:
    result = get_supabase_client().table("roadmaps").insert(
        {
            "user_id": user_id,
            "gpa": payload.gpa,
            "grade": payload.grade,
            "interests": payload.interests,
            "activities": payload.activities,
            "demographics": payload.demographic,
            "testing": payload.testing,
            "college_goals": payload.college_goals,
            "location": payload.location,
            "classes": payload.classes,
            "roadmap_content": roadmap_content,
        }
    ).execute()
    return result.data[0]["id"]


def list_roadmaps(user_id: str) -> list[dict]:
    result = (
        get_supabase_client()
        .table("roadmaps")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


def get_roadmap(user_id: str, roadmap_id: str) -> Optional[dict]:
    result = (
        get_supabase_client()
        .table("roadmaps")
        .select("*")
        .eq("user_id", user_id)
        .eq("id", roadmap_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def delete_roadmap(user_id: str, roadmap_id: str) -> bool:
    result = (
        get_supabase_client()
        .table("roadmaps")
        .delete()
        .eq("id", roadmap_id)
        .eq("user_id", user_id)
        .execute()
    )
    return bool(result.data)
