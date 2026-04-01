from typing import Optional

from app.core.clients import get_supabase_client
from app.schemas.essay import EssayRequest


def create_essay(user_id: str, payload: EssayRequest, feedback_content: str) -> str:
    result = get_supabase_client().table("essays").insert(
        {
            "user_id": user_id,
            "grade": payload.grade,
            "prompt": payload.prompt,
            "essay_text": payload.essay,
            "program": payload.program,
            "feedback": feedback_content,
        }
    ).execute()
    return result.data[0]["id"]


def list_essays(user_id: str) -> list[dict]:
    result = (
        get_supabase_client()
        .table("essays")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


def get_essay(user_id: str, essay_id: str) -> Optional[dict]:
    result = (
        get_supabase_client()
        .table("essays")
        .select("*")
        .eq("user_id", user_id)
        .eq("id", essay_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def delete_essay(user_id: str, essay_id: str) -> bool:
    result = (
        get_supabase_client()
        .table("essays")
        .delete()
        .eq("id", essay_id)
        .eq("user_id", user_id)
        .execute()
    )
    return bool(result.data)
