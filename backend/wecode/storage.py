"""Atomic storage boundary. Replace this adapter, not HTTP/domain logic, for persistence."""
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass, field
from threading import RLock
from typing import ContextManager, Protocol


@dataclass
class State:
    accounts: dict = field(default_factory=dict)
    emails: dict = field(default_factory=dict)
    sessions: dict = field(default_factory=dict)


class StorageUnavailable(Exception):
    """Adapter cannot currently commit/read; do not expose adapter details."""


class Storage(Protocol):
    def transaction(self) -> ContextManager[State]:
        """Yield isolated state; commit atomically on success, roll back on exception."""
        ...


class MemoryStorage:
    """One process only. Global lock serializes writes and coherent reads.

    Copy-on-commit prevents partial updates on failures and leaking mutable references.
    Accounts/sessions/history intentionally disappear when this instance/process ends.
    """
    def __init__(self):
        self._state = State()
        self._lock = RLock()

    @contextmanager
    def transaction(self):
        with self._lock:
            pending = deepcopy(self._state)
            yield pending
            self._state = deepcopy(pending)
