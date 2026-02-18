"""
Audit Logger — dual backend: PostgreSQL (if DATABASE_URL) or JSONL fallback.
"""

import asyncio
import json
import logging
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import text

logger = logging.getLogger("nadakki.audit")

# ── JSONL fallback ──────────────────────────────────────────────────────────
_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_LOG_FILE = _DATA_DIR / "audit_logs.jsonl"
_lock = threading.Lock()


def _ensure_dir():
    _DATA_DIR.mkdir(parents=True, exist_ok=True)


def generate_trace_id() -> str:
    return uuid.uuid4().hex[:16]


# ── Write ───────────────────────────────────────────────────────────────────

def write_log(entry: Dict[str, Any]) -> None:
    """Write audit entry. Uses DB if available, else JSONL."""
    from services.db import db_available

    if db_available():
        try:
            asyncio.get_running_loop().create_task(_write_db(entry))
            return
        except RuntimeError:
            pass  # no event loop — fall through to JSONL
        except Exception as exc:
            logger.warning(f"DB audit write scheduled failed: {exc}")

    _write_jsonl(entry)


def _write_jsonl(entry: Dict[str, Any]) -> None:
    _ensure_dir()
    line = json.dumps(entry, default=str)
    with _lock:
        with open(_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")


async def _write_db(entry: Dict[str, Any]) -> None:
    from services.db import get_session
    try:
        async with get_session() as session:
            await session.execute(
                text("""
                    INSERT INTO audit_logs
                        (trace_id, tenant_id, agent_id, mode, status, http_status,
                         latency_ms, user_id, error)
                    VALUES
                        (:trace_id, :tenant_id, :agent_id, :mode, :status, :http_status,
                         :latency_ms, :user_id, :error)
                """),
                {
                    "trace_id": entry.get("trace_id", ""),
                    "tenant_id": entry.get("tenant_id", "default"),
                    "agent_id": entry.get("agent_id", ""),
                    "mode": entry.get("mode"),
                    "status": entry.get("status"),
                    "http_status": entry.get("http_status"),
                    "latency_ms": entry.get("latency_ms"),
                    "user_id": entry.get("user_id"),
                    "error": entry.get("error"),
                },
            )
            await session.commit()
    except Exception as exc:
        logger.warning(f"DB audit write failed, falling back to JSONL: {exc}")
        _write_jsonl(entry)


# ── Read ────────────────────────────────────────────────────────────────────

async def read_logs_async(
    tenant_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """Read audit logs. Uses DB if available, else JSONL."""
    from services.db import db_available

    if db_available():
        try:
            return await _read_db(tenant_id, agent_id, limit)
        except Exception as exc:
            logger.warning(f"DB audit read failed, falling back to JSONL: {exc}")

    return read_logs_jsonl(tenant_id, agent_id, limit)


async def _read_db(
    tenant_id: Optional[str],
    agent_id: Optional[str],
    limit: int,
) -> List[Dict[str, Any]]:
    from services.db import get_session

    clauses = []
    params: Dict[str, Any] = {"lim": limit}

    if tenant_id:
        clauses.append("tenant_id = :tenant_id")
        params["tenant_id"] = tenant_id
    if agent_id:
        clauses.append("agent_id = :agent_id")
        params["agent_id"] = agent_id

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    sql = f"SELECT * FROM audit_logs {where} ORDER BY created_at DESC LIMIT :lim"

    # Use tenant context for RLS when filtering by tenant
    ctx_tenant = tenant_id if tenant_id else None
    async with get_session(tenant_id=ctx_tenant) as session:
        result = await session.execute(text(sql), params)
        rows = result.mappings().all()

    return [
        {
            "trace_id": r["trace_id"],
            "tenant_id": r["tenant_id"],
            "agent_id": r["agent_id"],
            "mode": r["mode"],
            "status": r["status"],
            "http_status": r["http_status"],
            "latency_ms": r["latency_ms"],
            "user_id": r["user_id"],
            "error": r["error"],
            "timestamp": r["created_at"].isoformat() if r["created_at"] else None,
        }
        for r in rows
    ]


def read_logs_jsonl(
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
    return results[-limit:][::-1]
