import uuid
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from healthcare_api.core.config import get_settings
from healthcare_api.db.session import get_db as _get_db

settings = get_settings()

# Re-exported so feature routers only need to import from `api.deps`.
get_db = _get_db
DbSession = Annotated[AsyncSession, Depends(get_db)]


def get_actor_id(
    x_user_id: Annotated[uuid.UUID | None, Header(alias=settings.default_actor_header)] = None,
) -> uuid.UUID:
    """Resolve the id of the actor making the request.

    For this development implementation the actor id is supplied directly
    via the `X-User-Id` header. In production this should be replaced by an
    authenticated identity resolved from OAuth2/OIDC or the organization's
    identity provider.
    """
    if x_user_id is None:
        raise HTTPException(
            status_code=422,
            detail=f"Missing required '{settings.default_actor_header}' header.",
        )
    return x_user_id


ActorId = Annotated[uuid.UUID, Depends(get_actor_id)]


@dataclass(frozen=True)
class Pagination:
    limit: int
    offset: int


def get_pagination(
    limit: Annotated[int, Query(ge=1, le=settings.max_page_limit)] = settings.default_page_limit,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Pagination:
    return Pagination(limit=limit, offset=offset)


PaginationParams = Annotated[Pagination, Depends(get_pagination)]
