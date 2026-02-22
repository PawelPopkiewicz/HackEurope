"""Pub/sub event bus used to broadcast SSE messages to connected dashboard clients."""

import asyncio
import json
from typing import Set


class EventBus:
    """Simple in-memory publish/subscribe bus backed by ``asyncio.Queue``.

    Subscribers receive every message emitted after they subscribe.
    Each subscriber gets its own queue so slow consumers do not block others.
    """

    def __init__(self):
        self.subscribers: Set[asyncio.Queue] = set()

    async def subscribe(self) -> asyncio.Queue:
        """Create and register a new subscriber queue.

        Returns:
            asyncio.Queue: A queue that will receive all future emitted messages.
        """
        queue = asyncio.Queue()
        self.subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue):
        """Remove a subscriber queue so it no longer receives messages.

        Args:
            queue: The subscriber queue to remove.
        """
        if queue in self.subscribers:
            self.subscribers.remove(queue)

    async def emit(self, data: dict):
        """Broadcast a message to every active subscriber.

        The *data* dict is JSON-serialised into SSE format (``data: ...\\n\\n``)
        and placed onto each subscriber queue concurrently.

        Args:
            data: The event payload to broadcast.
        """
        if not self.subscribers:
            # logger.info("No active subscribers, skipping broadcast.")
            return
            
        message = f"data: {json.dumps(data)}\n\n"
        # Create tasks to avoid blocking if one queue is slow
        tasks = [asyncio.create_task(queue.put(message)) for queue in self.subscribers]
        if tasks:
            await asyncio.wait(tasks)
            # logger.info(f"Broadcasted message to {len(tasks)} subscribers.")

# Global instances for the specific streams
# We could use one bus or multiple. The user wants a consolidated stream, 
# so one bus is better.
dashboard_bus = EventBus()
