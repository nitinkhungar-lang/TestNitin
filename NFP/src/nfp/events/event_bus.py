"""DomainEventBus for NFP.

Synchronous, in-process event bus. No external broker (Constitution C8).
"""
from __future__ import annotations

from collections import defaultdict
from typing import Callable, Type

from nfp.events.domain_events import DomainEvent


class DomainEventBus:
    """Simple synchronous in-process event bus.

    Handlers are called in the order they were registered.
    Exceptions in handlers propagate to the caller.

    Example::

        bus = DomainEventBus()

        def on_activity_recorded(event: ActivityRecorded) -> None:
            print(f"Activity recorded: {event.activity_id}")

        bus.subscribe(ActivityRecorded, on_activity_recorded)
        bus.publish(ActivityRecorded(...))
    """

    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list[Callable[[DomainEvent], None]]] = defaultdict(list)

    def subscribe(self, event_type: type[DomainEvent], handler: Callable[[DomainEvent], None]) -> None:
        """Subscribe a handler to a specific event type.

        Args:
            event_type: The DomainEvent subclass to subscribe to.
            handler: Callable that receives the event.
        """
        self._handlers[event_type].append(handler)

    def publish(self, event: DomainEvent) -> None:
        """Publish a single domain event to all registered handlers.

        Args:
            event: The domain event to publish.
        """
        for handler in self._handlers.get(type(event), []):
            handler(event)

    def publish_all(self, events: list[DomainEvent]) -> None:
        """Publish a list of domain events in order.

        Args:
            events: List of domain events to publish.
        """
        for event in events:
            self.publish(event)
