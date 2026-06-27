from typing import Annotated, TypedDict, cast

import httpx
from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import Settings, get_settings
from app.core.exceptions import UnauthorizedError
from app.schemas.user import AuthenticatedUser

bearer_scheme = HTTPBearer(auto_error=False)


class SupabaseUserPayload(TypedDict):
    id: str
    email: str


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AuthenticatedUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError("Missing bearer token")

    async with httpx.AsyncClient(timeout=5) as client:
        response = await client.get(
            f"{settings.supabase_url}/auth/v1/user",
            headers={
                "apikey": settings.supabase_publishable_key,
                "Authorization": f"Bearer {credentials.credentials}",
            },
        )

    if response.status_code != status.HTTP_200_OK:
        raise UnauthorizedError("Invalid Supabase session")

    payload = cast(SupabaseUserPayload, response.json())

    return AuthenticatedUser(
        id=payload["id"],
        email=payload["email"],
    )
