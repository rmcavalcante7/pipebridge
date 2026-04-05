"""
In-memory cache for modeled Pipe schema.
"""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from threading import Lock
from typing import Any, Callable, Optional

from pipebridge.models.phase import Phase
from pipebridge.models.pipe import Pipe


@dataclass
class _PipeSchemaCacheEntry:
    """
    Internal cache entry for a modeled pipe schema.

    :param pipe: Pipe = Cached modeled pipe
    :param loaded_at: datetime = Load timestamp
    :param expires_at: datetime = Expiration timestamp
    """

    pipe: Pipe
    loaded_at: datetime
    expires_at: datetime

    def isExpired(self, now: datetime) -> bool:
        """
        Check if the entry is expired.

        :param now: datetime = Current time

        :return: bool = Whether the entry is expired
        """
        return now >= self.expires_at


class PipeSchemaCache:
    """
    Thread-safe in-memory cache for modeled pipe schema.

    This cache stores complete :class:`pipebridge.models.pipe.Pipe` objects keyed
    by ``pipe_id`` and maintains a phase-to-pipe index to allow efficient
    lookup of a phase schema after the first load.

    Design goals of this first version:

    - in-memory only
    - TTL-based expiration
    - lock by cache key
    - lazy refresh on demand
    - no background thread
    - no hidden autonomous behavior

    :param ttl_seconds: int = Number of seconds a cached schema remains valid

    :example:
        >>> cache = PipeSchemaCache(ttl_seconds=60)
        >>> isinstance(cache, PipeSchemaCache)
        True
    """

    def __init__(self, ttl_seconds: int = 300) -> None:
        """
        Initialize the in-memory pipe schema cache.

        :param ttl_seconds: int = Number of seconds a schema remains valid
        """
        self._ttl_seconds = ttl_seconds
        self._entries: dict[str, _PipeSchemaCacheEntry] = {}
        self._phase_to_pipe: dict[str, str] = {}
        self._entry_locks: dict[str, Lock] = {}
        self._global_lock = Lock()

    def _now(self) -> datetime:
        """
        Return the current UTC timestamp for cache operations.

        :return: datetime = Timezone-aware UTC timestamp
        """
        return datetime.now(UTC)

    @property
    def ttl_seconds(self) -> int:
        """
        Retrieve the configured TTL for cache entries.

        :return: int = TTL in seconds
        """
        return self._ttl_seconds

    def get(self, pipe_id: str) -> Optional[Pipe]:
        """
        Retrieve a non-expired cached pipe schema.

        :param pipe_id: str = Pipe identifier

        :return: Pipe | None = Cached pipe if present and valid
        """
        now = self._now()
        entry = self._entries.get(pipe_id)
        if entry is None:
            return None
        if entry.isExpired(now):
            return None
        return entry.pipe

    def getPhaseSchema(self, phase_id: str) -> Optional[Phase]:
        """
        Retrieve a phase schema from the cached pipe catalog index.

        :param phase_id: str = Phase identifier

        :return: Phase | None = Cached phase schema if available
        """
        pipe_id = self._phase_to_pipe.get(phase_id)
        if not pipe_id:
            return None

        pipe = self.get(pipe_id)
        if pipe is None:
            return None

        return pipe.getPhase(phase_id)

    def getPipeIdForPhase(self, phase_id: str) -> Optional[str]:
        """
        Retrieve the cached pipe identifier associated with a phase.

        :param phase_id: str = Phase identifier

        :return: str | None = Cached pipe identifier
        """
        return self._phase_to_pipe.get(phase_id)

    def getOrLoad(self, pipe_id: str, loader: Callable[[], Pipe]) -> Pipe:
        """
        Retrieve a cached schema or lazily load and cache it.

        If multiple threads request the same ``pipe_id`` simultaneously, only
        one thread executes the loader while the others wait on the per-key
        lock.

        :param pipe_id: str = Pipe identifier
        :param loader: Callable[[], Pipe] = Lazy loader for the pipe schema

        :return: Pipe = Cached or freshly loaded schema
        """
        cached = self.get(pipe_id)
        if cached is not None:
            return cached

        lock = self._getEntryLock(pipe_id)
        with lock:
            cached = self.get(pipe_id)
            if cached is not None:
                return cached

            pipe = loader()
            self.set(pipe_id, pipe)
            return pipe

    def set(self, pipe_id: str, pipe: Pipe) -> None:
        """
        Store a modeled pipe schema in the cache and refresh indexes.

        :param pipe_id: str = Pipe identifier
        :param pipe: Pipe = Modeled pipe schema

        :return: None
        """
        now = self._now()
        entry = _PipeSchemaCacheEntry(
            pipe=pipe,
            loaded_at=now,
            expires_at=now + timedelta(seconds=self._ttl_seconds),
        )
        self._entries[pipe_id] = entry

        for phase in pipe.phases:
            if phase and phase.id:
                self._phase_to_pipe[phase.id] = pipe_id

    def invalidate(self, pipe_id: str) -> None:
        """
        Invalidate a specific cached pipe schema.

        :param pipe_id: str = Pipe identifier

        :return: None
        """
        entry = self._entries.pop(pipe_id, None)
        if entry is None:
            return

        phase_ids = [phase.id for phase in entry.pipe.phases if phase and phase.id]
        for phase_id in phase_ids:
            self._phase_to_pipe.pop(phase_id, None)

    def invalidateAll(self) -> None:
        """
        Invalidate all cached schemas and indexes.

        :return: None
        """
        self._entries.clear()
        self._phase_to_pipe.clear()

    def getEntryInfo(self, pipe_id: str) -> Optional[dict[str, Any]]:
        """
        Retrieve metadata about a cache entry.

        :param pipe_id: str = Pipe identifier

        :return: dict[str, Any] | None = Entry metadata if present
        """
        entry = self._entries.get(pipe_id)
        if entry is None:
            return None

        now = self._now()
        return {
            "pipe_id": pipe_id,
            "loaded_at": entry.loaded_at,
            "expires_at": entry.expires_at,
            "is_expired": entry.isExpired(now),
            "phase_count": len(entry.pipe.phases),
        }

    def getStats(self) -> dict[str, Any]:
        """
        Retrieve aggregate cache statistics.

        :return: dict[str, Any] = Cache summary
        """
        now = self._now()
        expired_entries = sum(
            1 for entry in self._entries.values() if entry.isExpired(now)
        )
        return {
            "ttl_seconds": self._ttl_seconds,
            "entries": len(self._entries),
            "indexed_phases": len(self._phase_to_pipe),
            "expired_entries": expired_entries,
        }

    def _getEntryLock(self, pipe_id: str) -> Lock:
        """
        Retrieve or create a per-entry lock.

        :param pipe_id: str = Pipe identifier

        :return: Lock = Per-entry lock
        """
        with self._global_lock:
            lock = self._entry_locks.get(pipe_id)
            if lock is None:
                lock = Lock()
                self._entry_locks[pipe_id] = lock
            return lock
