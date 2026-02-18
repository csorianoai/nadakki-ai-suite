#!/usr/bin/env python3
"""
Migrate OAuth tokens from SQLite (token_store) to PostgreSQL (oauth_tokens table).

Usage:
    DATABASE_URL=postgresql://... TOKEN_ENCRYPTION_KEY=... python scripts/migrate_tokens.py

Tokens are copied as-is (still encrypted with Fernet).
"""

import asyncio
import os
import sys
import sqlite3
import logging

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

load_dotenv()

from sqlalchemy import text
from backend.db.database import init_database, get_session

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("migrate_tokens")


def read_sqlite_tokens() -> list:
    """Read all active integrations from SQLite token_store."""
    db_path = os.getenv("DATABASE_PATH", "/tmp/nadakki_data.db")
    if not os.path.exists(db_path):
        logger.warning("SQLite DB not found at %s", db_path)
        return []

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT tenant_id, platform, access_token, refresh_token, expires_at "
            "FROM tenant_integrations WHERE is_active = 1"
        )
        rows = [dict(r) for r in cursor.fetchall()]
        logger.info("Found %d active tokens in SQLite", len(rows))
        return rows
    except sqlite3.OperationalError as e:
        logger.error("SQLite error: %s", e)
        return []
    finally:
        conn.close()


async def write_pg_tokens(tokens: list) -> int:
    """Insert tokens into PostgreSQL oauth_tokens table."""
    if not init_database():
        logger.error("Cannot connect to PostgreSQL — DATABASE_URL not set or invalid")
        return 0

    inserted = 0
    async with get_session() as session:
        for token in tokens:
            try:
                # Ensure tenant exists
                await session.execute(
                    text(
                        "INSERT INTO tenants (id, name) VALUES (:id, :name) "
                        "ON CONFLICT (id) DO NOTHING"
                    ),
                    {"id": token["tenant_id"], "name": token["tenant_id"]},
                )

                await session.execute(
                    text(
                        "INSERT INTO oauth_tokens (tenant_id, platform, access_token, refresh_token, expires_at) "
                        "VALUES (:tenant_id, :platform, :access_token, :refresh_token, :expires_at) "
                    ),
                    {
                        "tenant_id": token["tenant_id"],
                        "platform": token["platform"],
                        "access_token": token["access_token"],
                        "refresh_token": token.get("refresh_token"),
                        "expires_at": token.get("expires_at"),
                    },
                )
                inserted += 1
            except Exception as e:
                logger.warning("Skipped token %s/%s: %s", token["tenant_id"], token["platform"], e)

        await session.commit()

    logger.info("Migrated %d/%d tokens to PostgreSQL", inserted, len(tokens))
    return inserted


async def main():
    tokens = read_sqlite_tokens()
    if not tokens:
        logger.info("No tokens to migrate")
        return
    await write_pg_tokens(tokens)


if __name__ == "__main__":
    asyncio.run(main())
