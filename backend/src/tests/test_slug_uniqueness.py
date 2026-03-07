"""Tests for page slug uniqueness constraint (PLSH-04).

These tests verify that the partial unique index on pages(site_id, slug)
WHERE is_deleted=false is enforced correctly. They are marked xfail because
the SQLite in-memory test DB does not enforce PostgreSQL partial indexes.
Run these against a real PostgreSQL test DB after plan 14-03 has been applied.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


async def _create_user_and_site(
    client: AsyncClient, db: AsyncSession, email: str, site_slug: str
) -> tuple[str, str]:
    """Helper: register a user, create a site, return (access_token, site_id)."""
    reg = await client.post(
        "/api/auth/register",
        json={"email": email, "password": "password123"},
    )
    assert reg.status_code == 201, reg.text
    login = await client.post(
        "/api/auth/login",
        data={"username": email, "password": "password123"},
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    site = await client.post(
        "/api/sites/",
        json={"name": "Test Site", "slug": site_slug},
        headers=headers,
    )
    assert site.status_code == 201, site.text
    site_id = site.json()["id"]
    return token, site_id


@pytest.mark.xfail(
    reason="requires PostgreSQL partial unique index from plan 14-03; SQLite does not enforce it",
    strict=False,
)
async def test_duplicate_page_slug_returns_409(
    client: AsyncClient, db: AsyncSession
) -> None:
    """Two pages with the same slug on the same site should be rejected with 409."""
    token, site_id = await _create_user_and_site(
        client, db, "slug-test-1@example.com", "slug-test-site-1"
    )
    headers = {"Authorization": f"Bearer {token}"}

    r1 = await client.post(
        f"/api/sites/{site_id}/pages",
        json={"title": "About", "slug": "about"},
        headers=headers,
    )
    assert r1.status_code == 201, r1.text

    r2 = await client.post(
        f"/api/sites/{site_id}/pages",
        json={"title": "About Duplicate", "slug": "about"},
        headers=headers,
    )
    assert r2.status_code == 409, f"Expected 409 but got {r2.status_code}: {r2.text}"


@pytest.mark.xfail(
    reason="requires PostgreSQL partial unique index from plan 14-03; SQLite does not enforce it",
    strict=False,
)
async def test_soft_deleted_page_slug_can_be_reused(
    client: AsyncClient, db: AsyncSession
) -> None:
    """A soft-deleted page's slug must be available for a new page on the same site."""
    token, site_id = await _create_user_and_site(
        client, db, "slug-test-2@example.com", "slug-test-site-2"
    )
    headers = {"Authorization": f"Bearer {token}"}

    r1 = await client.post(
        f"/api/sites/{site_id}/pages",
        json={"title": "Contact", "slug": "contact"},
        headers=headers,
    )
    assert r1.status_code == 201, r1.text
    page_id = r1.json()["id"]

    del_r = await client.delete(
        f"/api/sites/{site_id}/pages/{page_id}",
        headers=headers,
    )
    assert del_r.status_code in (200, 204), del_r.text

    r2 = await client.post(
        f"/api/sites/{site_id}/pages",
        json={"title": "New Contact", "slug": "contact"},
        headers=headers,
    )
    assert r2.status_code == 201, (
        f"Expected 201 after soft-delete but got {r2.status_code}: {r2.text}"
    )


async def test_pages_on_different_sites_can_share_slug(
    client: AsyncClient, db: AsyncSession
) -> None:
    """Pages on different sites may share the same slug — no cross-site uniqueness."""
    token_a, site_a = await _create_user_and_site(
        client, db, "slug-test-3a@example.com", "slug-test-site-3a"
    )
    token_b, site_b = await _create_user_and_site(
        client, db, "slug-test-3b@example.com", "slug-test-site-3b"
    )

    r_a = await client.post(
        f"/api/sites/{site_a}/pages",
        json={"title": "Home", "slug": "home"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert r_a.status_code == 201, r_a.text

    r_b = await client.post(
        f"/api/sites/{site_b}/pages",
        json={"title": "Home", "slug": "home"},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert r_b.status_code == 201, (
        f"Expected 201 for cross-site slug but got {r_b.status_code}: {r_b.text}"
    )
