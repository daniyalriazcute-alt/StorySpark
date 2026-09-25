"""Short-term memory for agent handoff."""


class ShortTermMemory:
    """Simple session-scoped memory store."""

    def __init__(self):
        self._store = {}

    def save(self, key: str, value: str) -> None:
        self._store[key] = value

    def get(self, key: str) -> str | None:
        return self._store.get(key)

    def clear(self) -> None:
        self._store.clear()


# Module-level singleton
memory = ShortTermMemory()
