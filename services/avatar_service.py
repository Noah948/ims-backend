import mimetypes
import time
from datetime import datetime
from urllib.parse import urlsplit
from uuid import uuid4

import httpx
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from core.config import settings
from models.user_model import User


MAX_AVATAR_BYTES = 2 * 1024 * 1024  # matches the bucket's 2MB limit

# SVG is excluded: it can carry scripts.
BLOCKED_TYPES = {"image/svg+xml"}

DOH_URL = "https://cloudflare-dns.com/dns-query"

# host -> (ip, expires_at)
_dns_cache: dict[str, tuple[str, float]] = {}


def _not_configured() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Avatar storage is not configured",
    )


def _supabase_url() -> str:
    """
    Explicit SUPABASE_URL, otherwise the project ref from DATABASE_URL:
    pooler user "postgres.<ref>" or direct host "db.<ref>.supabase.co".
    """

    if settings.SUPABASE_URL:
        return settings.SUPABASE_URL.rstrip("/")

    parts = urlsplit(settings.DATABASE_URL)
    username = parts.username or ""
    host = parts.hostname or ""

    if username.startswith("postgres."):
        ref = username.split(".", 1)[1]
    elif host.startswith("db.") and host.endswith(".supabase.co"):
        ref = host.split(".")[1]
    else:
        raise _not_configured()

    return f"https://{ref}.supabase.co"


def _headers() -> dict:
    key = settings.SUPABASE_SERVICE_ROLE_KEY
    headers = {"apikey": key}

    # Legacy service_role keys are JWTs and also go in Authorization;
    # new sb_secret_ keys are not JWTs and belong only in apikey.
    if key.startswith("eyJ"):
        headers["Authorization"] = f"Bearer {key}"

    return headers


async def _resolve_over_https(client: httpx.AsyncClient, host: str) -> str:
    """
    Look up host's IPv4 address via DNS-over-HTTPS. Some ISPs (e.g. ACT
    Fibernet in India) hijack plain DNS for *.supabase.co, so this is
    used only when SUPABASE_DNS_OVER_HTTPS is enabled.
    """

    cached = _dns_cache.get(host)
    if cached and cached[1] > time.monotonic():
        return cached[0]

    response = await client.get(
        DOH_URL,
        params={"name": host, "type": "A"},
        headers={"accept": "application/dns-json"},
    )
    response.raise_for_status()

    for answer in response.json().get("Answer", []):
        if answer.get("type") == 1:  # A record
            ttl = max(int(answer.get("TTL", 60)), 60)
            _dns_cache[host] = (answer["data"], time.monotonic() + ttl)
            return answer["data"]

    raise httpx.ConnectError(f"No A record for {host}")


async def _storage_request(
    method: str,
    path: str = "",
    timeout: float = 30,
    **kwargs,
) -> httpx.Response:
    """Call the Supabase Storage object API for the avatar bucket."""

    if not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise _not_configured()

    url = f"{_supabase_url()}/storage/v1/object/{settings.SUPABASE_AVATAR_BUCKET}/{path}".rstrip("/")
    headers = {**_headers(), **kwargs.pop("headers", {})}

    async with httpx.AsyncClient(timeout=timeout) as client:

        if not settings.SUPABASE_DNS_OVER_HTTPS:
            return await client.request(method, url, headers=headers, **kwargs)

        # Connect to the real IP, but keep the hostname for TLS (SNI +
        # certificate check) and the Host header.
        host = urlsplit(url).hostname
        ip = await _resolve_over_https(client, host)

        return await client.request(
            method,
            url.replace(f"://{host}", f"://{ip}", 1),
            headers={**headers, "Host": host},
            extensions={"sni_hostname": host},
            **kwargs,
        )


async def _remove_object(path: str) -> None:
    """Best-effort delete; a leftover file must not fail the request."""
    try:
        await _storage_request(
            "DELETE",
            timeout=10,
            json={"prefixes": [path]},
        )
    except httpx.HTTPError:
        pass


async def _read_image(file: UploadFile) -> tuple[bytes, str]:
    content_type = (file.content_type or "").lower()

    if not content_type.startswith("image/") or content_type in BLOCKED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only image files (JPG, PNG, GIF, WEBP) are allowed",
        )

    content = await file.read(MAX_AVATAR_BYTES + 1)

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty",
        )

    if len(content) > MAX_AVATAR_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image must be 2MB or smaller",
        )

    return content, content_type


# =====================================================
# Upload / Replace Avatar
# =====================================================

async def upload_avatar(
    db: Session,
    user: User,
    file: UploadFile,
) -> User:
    """
    Upload a new avatar and point the user at it.

    user.avatar is an API path (served by GET /users/{id}/avatar), so
    browsers never contact Supabase directly. Each upload gets a fresh
    object key, and ?v= changes with it so caches pick up the new
    picture; the previous object is removed once the database is updated.
    """

    content, content_type = await _read_image(file)

    file_id = uuid4().hex
    ext = mimetypes.guess_extension(content_type) or ""
    path = f"{user.id}/{file_id}{ext}"

    try:
        response = await _storage_request(
            "POST",
            path,
            headers={"Content-Type": content_type},
            content=content,
        )
    except httpx.HTTPError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not reach avatar storage",
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to upload avatar",
        )

    old_path = user.avatar_path

    user.avatar = f"/users/{user.id}/avatar?v={file_id}"
    user.avatar_path = path
    user.updated_at = datetime.utcnow()

    try:
        db.commit()
    except Exception:
        db.rollback()
        await _remove_object(path)
        raise

    db.refresh(user)

    if old_path:
        await _remove_object(old_path)

    return user


# =====================================================
# Serve Avatar Image
# =====================================================

async def get_avatar_image(
    db: Session,
    user_id,
) -> tuple[bytes, str]:
    """Fetch a user's avatar bytes and content type from storage."""

    user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.deleted_at.is_(None),
        )
        .first()
    )

    if not user or not user.avatar_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avatar not found",
        )

    try:
        response = await _storage_request("GET", user.avatar_path)
    except httpx.HTTPError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not reach avatar storage",
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avatar not found",
        )

    content_type = response.headers.get("content-type", "application/octet-stream")

    return response.content, content_type


# =====================================================
# Delete Avatar
# =====================================================

async def delete_avatar(
    db: Session,
    user: User,
) -> User:

    if not user.avatar and not user.avatar_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No avatar to delete",
        )

    old_path = user.avatar_path

    user.avatar = None
    user.avatar_path = None
    user.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(user)

    if old_path:
        await _remove_object(old_path)

    return user
