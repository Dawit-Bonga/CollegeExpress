from functools import lru_cache

from groq import Groq
from supabase import Client, create_client

from app.core.config import get_settings


@lru_cache
def get_groq_client() -> Groq:
    settings = get_settings()
    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY is not set")
    return Groq(api_key=settings.groq_api_key)


@lru_cache
def get_supabase_client() -> Client:
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_key:
        raise RuntimeError("Supabase credentials are not fully configured")
    return create_client(settings.supabase_url, settings.supabase_service_key)
