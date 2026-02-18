"""
Security utilities — rate limiter + live gate.
"""

import os
import time
import threading
import logging
from collections import defaultdict
from typing import Optional

logger = logging.getLogger("nadakki.security")

# ---------------------------------------------------------------------------
# Rate Limiter (in-memory sliding window)
# ---------------------------------------------------------------------------

_DEFAULT_WINDOW_SECONDS = 60
_DEFAULT_MAX_REQUESTS = 30

_buckets: dict = defaultdict(list)  # key -> [timestamps]
_lock = threading.Lock()


def rate_limit_check(
    key: str,
    max_requests: int = _DEFAULT_MAX_REQUESTS,
    window_seconds: int = _DEFAULT_WINDOW_SECONDS,
) -> bool:
    """
    Returns True if the request is ALLOWED, False if rate-limited.
    Key should be tenant_id:ip or similar.
    """
    now = time.time()
    cutoff = now - window_seconds

    with _lock:
        timestamps = _buckets[key]
        # Prune old entries
        _buckets[key] = [t for t in timestamps if t > cutoff]
        if len(_buckets[key]) >= max_requests:
            return False
        _buckets[key].append(now)
        return True


def rate_limit_remaining(
    key: str,
    max_requests: int = _DEFAULT_MAX_REQUESTS,
    window_seconds: int = _DEFAULT_WINDOW_SECONDS,
) -> int:
    now = time.time()
    cutoff = now - window_seconds
    with _lock:
        active = [t for t in _buckets.get(key, []) if t > cutoff]
    return max(0, max_requests - len(active))


# ---------------------------------------------------------------------------
# Live Gate
# ---------------------------------------------------------------------------

def live_gate_check(dry_run: bool, role: Optional[str]) -> Optional[str]:
    """
    Returns None if allowed, or an error message if blocked.
    Only blocks when dry_run=False (live execution).
    """
    if dry_run:
        return None  # dry_run always allowed

    live_enabled = os.environ.get("LIVE_ENABLED", "false").lower() == "true"
    if not live_enabled:
        return "Live execution is disabled. Set LIVE_ENABLED=true to enable."

    if role != "admin":
        return f"Live execution requires role=admin. Got role={role!r}."

    return None
