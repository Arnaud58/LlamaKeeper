import asyncio
import logging
import uuid
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Type


class EventType(Enum):
    """
    Standard event types for the system
    """

    CHARACTER_CREATED = auto()
    CHARACTER_UPDATED = auto()
    STORY_GENERATED = auto()
    MODEL_LOADED = auto()
    MEMORY_STORED = auto()
    GENERATION_STARTED = auto()
    GENERATION_COMPLETED = auto()
    SYSTEM_ERROR = auto()
    CUSTOM = auto()


class Event:
    """
    Represents a system event with metadata and payload
    """

    def __init__(
        self,
        event_type: EventType,
        payload: Dict[str, Any],
        source: Optional[str] = None,
    ):
        """
        Initialize an event

        Args:
            event_type (EventType): Type of the event
            payload (Dict): Event-specific data
            source (str, optional): Source of the event
        """
        self.id = str(uuid.uuid4())
        self.type = event_type
        self.payload = payload
        self.source = source
        self.timestamp = asyncio.get_event_loop().time()

    def __repr__(self):
        return f"Event(id={self.id}, type={self.type}, source={self.source})"


class EventBus:
    """
    Centralized event bus for asynchronous event handling
    Supports plugin-based event listeners and standard event types
    """

    _instance = None

    def __new__(cls):
        """
        Singleton pattern implementation

        Returns:
            EventBus: Singleton instance
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """
        Initialize the event bus
        """
        self._listeners: Dict[EventType, List[Callable]] = {}
        self._global_listeners: List[Callable] = []
        self._logger = logging.getLogger("EventBus")
        self._logger.setLevel(logging.INFO)
        self._event_queue = asyncio.Queue()
        self._processing_task = None

    def register_listener(
        self, event_type: EventType, listener: Callable[[Event], Any]
    ):
        """
        Register a listener for a specific event type

        Args:
            event_type (EventType): Event type to listen for
            listener (Callable): Listener function
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []

        self._listeners[event_type].append(listener)
        self._logger.info(f"Registered listener for {event_type}")

    def register_global_listener(self, listener: Callable[[Event], Any]):
        """
        Register a global listener for all events

        Args:
            listener (Callable): Listener function
        """
        self._global_listeners.append(listener)
        self._logger.info("Registered global listener")

    async def emit(
        self,
        event_type: EventType,
        payload: Dict[str, Any],
        source: Optional[str] = None,
    ):
        """
        Emit an event to the event bus

        Args:
            event_type (EventType): Type of the event
            payload (Dict): Event-specific data
            source (str, optional): Source of the event
        """
        event = Event(event_type, payload, source)
        await self._event_queue.put(event)
        self._logger.info(f"Event emitted: {event}")

    async def _process_events(self):
        """
        Process events from the queue
        """
        while True:
            try:
                event = await self._event_queue.get()

                # Call global listeners
                for global_listener in self._global_listeners:
                    try:
                        await global_listener(event)
                    except Exception as e:
                        self._logger.error(f"Global listener error: {e}")

                # Call type-specific listeners
                if event.type in self._listeners:
                    for listener in self._listeners[event.type]:
                        try:
                            await listener(event)
                        except Exception as e:
                            self._logger.error(f"Listener error for {event.type}: {e}")

                self._event_queue.task_done()

            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"Event processing error: {e}")

    def start(self):
        """
        Start the event processing loop
        """
        if self._processing_task is None or self._processing_task.done():
            loop = asyncio.get_event_loop()
            self._processing_task = loop.create_task(self._process_events())
            self._logger.info("Event bus started")

    def stop(self):
        """
        Stop the event processing loop
        """
        if self._processing_task and not self._processing_task.done():
            self._processing_task.cancel()
            self._logger.info("Event bus stopped")


def event_listener(event_type: EventType):
    """
    Decorator to register an event listener

    Args:
        event_type (EventType): Event type to listen for
    """

    def decorator(func):
        event_bus = EventBus()
        event_bus.register_listener(event_type, func)
        return func

    return decorator
