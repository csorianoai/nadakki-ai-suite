"""
Audit Logger — JSONL persistence for agent execution events.
Writes one JSON line per execution to data/audit_logs.jsonl.
Thread-safe via a Lock.
"""

import json
import logging
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("nadakki.audit")

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_LOG_FILE = _DATA_DIR / "audit_logs.jsonl"
_lock = threading.Lock()


def _ensure_dir():
    _DATA_DIR.mkdir(parents=True, exist_ok=True)


def generate_trace_id() -> str:
    return uuid.uuid4().hex[:16]


def write_log(entry: Dict[str, Any]) -> None:
    _ensure_dir()
    line = json.dumps(entry, default=str)
    with _lock:
        with open(_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")


def read_logs(
    tenant_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    if not _LOG_FILE.exists():
        return []

    results: List[Dict[str, Any]] = []
    with open(_LOG_FILE, "r", encoding="utf-8") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            try:
                entry = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if tenant_id and entry.get("tenant_id") != tenant_id:
                continue
            if agent_id and entry.get("agent_id") != agent_id:
                continue
            results.append(entry)

    # Return most recent first, up to limit
    return results[-limit:][::-1]
