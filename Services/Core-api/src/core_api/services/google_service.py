from fastapi import HTTPException, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from core_api.config import settings


def verify_google_id_token(raw_token: str) -> dict:
    """
    Returns the decoded claims dict on success. Raises 401 on failure.
    The claims we care about: sub (Google user id), email, email_verified,
    name, picture.
    """
    try:
        info = google_id_token.verify_oauth2_token(
            raw_token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except ValueError as exc:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, f"Invalid Google token: {exc}"
        )
    return info
