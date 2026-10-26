import time
from collections import defaultdict, deque

from .config import settings

_history: dict[str, deque] = defaultdict(lambda: deque(maxlen=settings.HISTORY_LIMIT))
_hits: dict[str, deque] = defaultdict(deque)
_seen: deque = deque(maxlen=1000)


def add(user_id: str, role: str, content: str) -> None:
    _history[user_id].append({"role": role, "content": content})


def get(user_id: str) -> list[dict]:
    return list(_history[user_id])


def reset(user_id: str) -> None:
    _history.pop(user_id, None)


def is_duplicate(mid: str | None) -> bool:
    if not mid:
        return False
    if mid in _seen:
        return True
    _seen.append(mid)
    return False


def rate_limited(user_id: str) -> bool:
    now = time.time()
    q = _hits[user_id]
    while q and now - q[0] > 60:
        q.popleft()
    if len(q) >= settings.RATE_LIMIT_PER_MIN:
        return True
    q.append(now)
    return False
