from types import SimpleNamespace

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.clients import get_supabase_client
from app.core.config import get_settings

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    settings = get_settings()

    if settings.dev_mode and token == "dev-token-bypass":
        return SimpleNamespace(id="dev-user-123", email="dev@test.com")

    try:
        user_response = get_supabase_client().auth.get_user(token)
        return user_response.user
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        ) from exc
