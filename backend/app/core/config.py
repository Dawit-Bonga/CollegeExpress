import os
from dataclasses import dataclass
from functools import lru_cache
from typing import List, Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    groq_api_key: Optional[str]
    supabase_url: Optional[str]
    supabase_service_key: Optional[str]
    dev_mode: bool
    cors_origins: List[str]


def _parse_cors_origins(raw_value: Optional[str]) -> List[str]:
    if not raw_value:
        return ["*"]
    return [origin.strip() for origin in raw_value.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_service_key=os.getenv("SUPABASE_SERVICE_KEY"),
        dev_mode=os.getenv("DEV_MODE", "false").lower() == "true",
        cors_origins=_parse_cors_origins(os.getenv("CORS_ORIGINS")),
    )
