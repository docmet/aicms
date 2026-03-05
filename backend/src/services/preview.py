"""Server-Sent Events (SSE) manager for real-time page preview.

When a content section draft is updated (via dashboard or MCP), the backend
broadcasts the new sections state to all admin editor clients connected to that
page's preview stream. The preview iframe re-renders sections sub-second.

Architecture:
  - One asyncio.Queue per connected SSE client
  - broadcast(page_id, data) → pushes to all queues for that page
  - stream() → async generator yielding SSE-formatted strings
  - Module-level singleton `preview_manager` shared across all requests
"""

import asyncio
from collections import defaultdict
from typing import AsyncGenerator
from uuid import UUID


class PreviewSSEManager:
    """In-memory SSE connection manager, keyed by page_id."""

    def __init__(self) -> None:
        # str(page_id) → list of queues (one per connected client)
        self._subscribers: dict[str, list[asyncio.Queue[str | None]]] = defaultdict(list)

    def subscribe(self, page_id: UUID) -> "asyncio.Queue[str | None]":
        """Register a new SSE listener. Returns the queue to read from."""
        queue: asyncio.Queue[str | None] = asyncio.Queue()
        self._subscribers[str(page_id)].append(queue)
        return queue

    def unsubscribe(self, page_id: UUID, queue: "asyncio.Queue[str | None]") -> None:
        """Remove a listener (called when client disconnects)."""
        listeners = self._subscribers.get(str(page_id), [])
        if queue in listeners:
            listeners.remove(queue)

    async def broadcast(self, page_id: UUID, data: str) -> None:
        """Push a JSON string to all preview clients watching this page."""
        for queue in list(self._subscribers.get(str(page_id), [])):
            await queue.put(data)

    async def stream(
        self, page_id: UUID, queue: "asyncio.Queue[str | None]"
    ) -> AsyncGenerator[str]:
        """Yield SSE-formatted event strings until the client disconnects."""
        try:
            while True:
                message = await queue.get()
                if message is None:
                    break
                yield f"data: {message}\n\n"
        finally:
            self.unsubscribe(page_id, queue)


# Singleton shared across all FastAPI requests (in-process only).
# For multi-process deployments, replace with Redis pub/sub.
preview_manager = PreviewSSEManager()
