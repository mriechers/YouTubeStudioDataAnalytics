"""Auth status and refresh endpoints."""

from pathlib import Path

from fastapi import APIRouter

from api.config import TOKEN_PATH
from api.schemas import AuthStatusResponse

router = APIRouter()


@router.get("/auth/status", response_model=AuthStatusResponse)
def auth_status():
    """Check if OAuth token exists and is potentially valid."""
    token_exists = TOKEN_PATH.exists()

    expires_at = None
    if token_exists:
        try:
            import json
            with open(TOKEN_PATH) as f:
                token_data = json.load(f)
            expires_at = token_data.get("expiry")
        except Exception:
            pass

    return AuthStatusResponse(
        authenticated=token_exists,
        expires_at=expires_at,
    )


@router.post("/auth/refresh")
def auth_refresh():
    """Attempt to refresh the OAuth token."""
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
        from youtube_api.auth import get_credentials
        get_credentials()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
