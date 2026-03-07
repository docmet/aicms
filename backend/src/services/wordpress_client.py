"""WordPress REST API client service."""

from typing import Any

import httpx
from fastapi import HTTPException


class WordPressClient:
    """HTTP client for WordPress REST API using Application Password auth."""

    def __init__(self, site_url: str, username: str, password: str) -> None:
        self.site_url = site_url.rstrip("/")
        self.username = username
        self.password = password

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        """Make an authenticated request to the WP REST API v2 endpoint."""
        url = f"{self.site_url}/wp-json/wp/v2{path}"
        try:
            async with httpx.AsyncClient(
                auth=httpx.BasicAuth(self.username, self.password),
                timeout=15.0,
            ) as client:
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
        except httpx.ConnectError as e:
            raise HTTPException(status_code=502, detail=f"Cannot connect to WordPress site: {e}") from e
        except httpx.TimeoutException as e:
            raise HTTPException(status_code=502, detail=f"WordPress site timed out: {e}") from e
        except httpx.HTTPStatusError:
            raise

    async def get_site_info(self) -> Any:
        """GET /wp-json/ — returns site name, description, url."""
        url = f"{self.site_url}/wp-json/"
        try:
            async with httpx.AsyncClient(
                auth=httpx.BasicAuth(self.username, self.password),
                timeout=15.0,
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except httpx.ConnectError as e:
            raise HTTPException(status_code=502, detail=f"Cannot connect to WordPress site: {e}") from e
        except httpx.TimeoutException as e:
            raise HTTPException(status_code=502, detail=f"WordPress site timed out: {e}") from e
        except httpx.HTTPStatusError:
            raise

    async def verify_credentials(self) -> Any:
        """GET /wp/v2/users/me — verifies auth and returns user role/capabilities."""
        return await self._request("GET", "/users/me?context=edit")

    async def list_posts(self, status: str = "any", per_page: int = 20) -> Any:
        """List WordPress posts."""
        return await self._request("GET", f"/posts?status={status}&per_page={per_page}&_embed=1")

    async def get_post(self, post_id: int) -> Any:
        """Get a single WordPress post."""
        return await self._request("GET", f"/posts/{post_id}?_embed=1")

    async def create_post(self, title: str, content: str, status: str = "draft", **extra: Any) -> Any:
        """Create a new WordPress post."""
        return await self._request(
            "POST",
            "/posts",
            json={"title": title, "content": content, "status": status, **extra},
        )

    async def update_post(self, post_id: int, **fields: Any) -> Any:
        """Update an existing WordPress post."""
        return await self._request("PATCH", f"/posts/{post_id}", json=fields)

    async def list_pages(self, status: str = "publish", per_page: int = 20) -> Any:
        """List WordPress pages."""
        # WP REST API returns 400 for status=any on pages without explicit edit context;
        # expand to comma-separated list instead.
        if status == "any":
            status = "publish,draft,pending,private"
        return await self._request("GET", f"/pages?status={status}&per_page={per_page}")

    async def get_page(self, page_id: int) -> Any:
        """Get a single WordPress page."""
        return await self._request("GET", f"/pages/{page_id}?_embed=1")

    async def create_page(self, title: str, content: str, status: str = "draft", **extra: Any) -> Any:
        """Create a new WordPress page."""
        return await self._request(
            "POST",
            "/pages",
            json={"title": title, "content": content, "status": status, **extra},
        )

    async def update_page(self, page_id: int, **fields: Any) -> Any:
        """Update an existing WordPress page."""
        return await self._request("PATCH", f"/pages/{page_id}", json=fields)

    async def list_categories(self, per_page: int = 50) -> Any:
        """List WordPress categories."""
        return await self._request("GET", f"/categories?per_page={per_page}")

    async def list_tags(self, per_page: int = 50) -> Any:
        """List WordPress tags."""
        return await self._request("GET", f"/tags?per_page={per_page}")

    async def update_site_settings(self, title: str | None = None, description: str | None = None) -> Any:
        """Update WordPress site settings (requires manage_options capability)."""
        payload: dict[str, str] = {}
        if title is not None:
            payload["title"] = title
        if description is not None:
            payload["description"] = description
        url = f"{self.site_url}/wp-json/wp/v2/settings"
        try:
            async with httpx.AsyncClient(
                auth=httpx.BasicAuth(self.username, self.password),
                timeout=15.0,
            ) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
        except httpx.ConnectError as e:
            raise HTTPException(status_code=502, detail=f"Cannot connect to WordPress site: {e}") from e
        except httpx.TimeoutException as e:
            raise HTTPException(status_code=502, detail=f"WordPress site timed out: {e}") from e
        except httpx.HTTPStatusError:
            raise
