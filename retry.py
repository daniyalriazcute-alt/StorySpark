"""Retry logic — max 1 retry on failure."""
from typing import Callable, Any


def retry_once(func: Callable[..., Any], *args, **kwargs) -> Any:
    """Execute func once. If result is falsy, retry exactly one more time."""
    result = func(*args, **kwargs)
    if not result:
        result = func(*args, **kwargs)
    return result
