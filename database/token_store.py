"""
Nadakki AI Suite - Token Store
Encrypted storage for OAuth tokens in SQLite.
Tokens are ALWAYS encrypted with Fernet before storage.
"""
import os
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from cryptography.fernet import Fernet

logger = logging.getLogger("TokenStore")

DB_PATH = os.getenv("DATABASE_PATH", "/tmp/nadakki_data.db")


def _get_db_path() -> str:
    return os.getenv("DATABASE_PATH", DB_PATH)


class TokenStore:
    """Encrypted token storage backed by SQLite."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or _get_db_path()
        key = os.getenv("TOKEN_ENCRYPTION_KEY")
        if not key:
            raise ValueError("TOKEN_ENCRYPTION_KEY environment variable is required")
        # Fernet key must be 32 url-safe base64-encoded bytes
        self.fernet = Fernet(key.encode() if isinstance(key, str) else key)
        self._init_tables()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self):
        db_dir = os.path.dirname(os.path.abspath(self.db_path))
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tenant_integrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id VARCHAR(100) NOT NULL,
                platform VARCHAR(50) NOT NULL,
                access_token TEXT NOT NULL,
                refresh_token TEXT,
                user_id VARCHAR(255),
                user_name VARCHAR(255),
                user_email VARCHAR(255),
                page_id VARCHAR(100),
                page_name VARCHAR(255),
                ig_account_id VARCHAR(100),
                ads_customer_ids TEXT,
                analytics_property_id VARCHAR(100),
                youtube_channel_id VARCHAR(100),
                scopes TEXT,
                expires_at TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(tenant_id, platform)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS oauth_state_store (
                state_key VARCHAR(255) PRIMARY KEY,
                tenant_id VARCHAR(100) NOT NULL,
                nonce VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS oauth_activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id VARCHAR(100),
                platform VARCHAR(50),
                action VARCHAR(50),
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()
        logger.info("Token store tables initialized")

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string with Fernet."""
        return self.fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a Fernet-encrypted string."""
        return self.fernet.decrypt(ciphertext.encode()).decode()

    async def save_integration(
        self, tenant_id: str, platform: str, data: Dict[str, Any]
    ) -> bool:
        """Save or update an integration. Tokens are encrypted before storage."""
        conn = self._get_conn()
        cursor = conn.cursor()

        try:
            # Encrypt tokens
            encrypted_access = self.encrypt(data["access_token"])
            encrypted_refresh = (
                self.encrypt(data["refresh_token"])
                if data.get("refresh_token")
                else None
            )

            # Check if existing record has a refresh_token we should preserve
            if not data.get("refresh_token"):
                cursor.execute(
                    "SELECT refresh_token FROM tenant_integrations WHERE tenant_id=? AND platform=?",
                    (tenant_id, platform),
                )
                existing = cursor.fetchone()
                if existing and existing["refresh_token"]:
                    encrypted_refresh = existing["refresh_token"]

            now = datetime.utcnow().isoformat()

            cursor.execute(
                """
                INSERT INTO tenant_integrations
                    (tenant_id, platform, access_token, refresh_token,
                     user_id, user_name, user_email,
                     page_id, page_name, ig_account_id,
                     ads_customer_ids, analytics_property_id, youtube_channel_id,
                     scopes, expires_at, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
                ON CONFLICT(tenant_id, platform) DO UPDATE SET
                    access_token=excluded.access_token,
                    refresh_token=COALESCE(excluded.refresh_token, tenant_integrations.refresh_token),
                    user_id=excluded.user_id,
                    user_name=excluded.user_name,
                    user_email=excluded.user_email,
                    page_id=excluded.page_id,
                    page_name=excluded.page_name,
                    ig_account_id=excluded.ig_account_id,
                    ads_customer_ids=excluded.ads_customer_ids,
                    analytics_property_id=excluded.analytics_property_id,
                    youtube_channel_id=excluded.youtube_channel_id,
                    scopes=excluded.scopes,
                    expires_at=excluded.expires_at,
                    is_active=1,
                    updated_at=excluded.updated_at
                """,
                (
                    tenant_id,
                    platform,
                    encrypted_access,
                    encrypted_refresh,
                    data.get("user_id"),
                    data.get("user_name"),
                    data.get("user_email"),
                    data.get("page_id"),
                    data.get("page_name"),
                    data.get("ig_account_id"),
                    json.dumps(data.get("ads_customer_ids")) if data.get("ads_customer_ids") else None,
                    data.get("analytics_property_id"),
                    data.get("youtube_channel_id"),
                    data.get("scopes"),
                    data.get("expires_at"),
                    now,
                    now,
                ),
            )
            conn.commit()
            logger.info(f"Integration saved: {tenant_id}/{platform}")
            return True
        except Exception as e:
            conn.rollback()
            logger.error(f"Error saving integration: {e}")
            raise
        finally:
            conn.close()

    async def get_integration(
        self, tenant_id: str, platform: str
    ) -> Optional[Dict[str, Any]]:
        """Get integration with decrypted tokens."""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM tenant_integrations WHERE tenant_id=? AND platform=? AND is_active=1",
            (tenant_id, platform),
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        result = dict(row)
        try:
            result["access_token"] = self.decrypt(result["access_token"])
        except Exception:
            logger.warning(f"Failed to decrypt access_token for {tenant_id}/{platform}")
            result["access_token"] = None

        if result.get("refresh_token"):
            try:
                result["refresh_token"] = self.decrypt(result["refresh_token"])
            except Exception:
                logger.warning(f"Failed to decrypt refresh_token for {tenant_id}/{platform}")
                result["refresh_token"] = None

        if result.get("ads_customer_ids"):
            try:
                result["ads_customer_ids"] = json.loads(result["ads_customer_ids"])
            except (json.JSONDecodeError, TypeError):
                pass

        return result

    async def delete_integration(self, tenant_id: str, platform: str) -> bool:
        """Soft-delete an integration."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tenant_integrations SET is_active=0, updated_at=? WHERE tenant_id=? AND platform=?",
            (datetime.utcnow().isoformat(), tenant_id, platform),
        )
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0

    async def list_integrations(self, tenant_id: str) -> List[Dict[str, Any]]:
        """List all active integrations for a tenant (tokens masked)."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT tenant_id, platform, user_email, page_id, page_name, ig_account_id, "
            "expires_at, is_active, created_at, updated_at "
            "FROM tenant_integrations WHERE tenant_id=? AND is_active=1",
            (tenant_id,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # --- OAuth State ---

    async def save_oauth_state(
        self, state_key: str, tenant_id: str, nonce: str, ttl_minutes: int = 10
    ) -> bool:
        """Save a CSRF state for OAuth flow (one-time use)."""
        conn = self._get_conn()
        cursor = conn.cursor()
        expires = (datetime.utcnow() + timedelta(minutes=ttl_minutes)).isoformat()
        try:
            cursor.execute(
                "INSERT INTO oauth_state_store (state_key, tenant_id, nonce, expires_at) VALUES (?, ?, ?, ?)",
                (state_key, tenant_id, nonce, expires),
            )
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            logger.error(f"Error saving oauth state: {e}")
            return False
        finally:
            conn.close()

    async def validate_and_consume_state(
        self, state_key: str
    ) -> Optional[Dict[str, Any]]:
        """Validate and consume (delete) a CSRF state. Returns None if invalid/expired."""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM oauth_state_store WHERE state_key=?", (state_key,)
        )
        row = cursor.fetchone()

        if not row:
            conn.close()
            return None

        result = dict(row)

        # Delete immediately (one-time use)
        cursor.execute(
            "DELETE FROM oauth_state_store WHERE state_key=?", (state_key,)
        )
        conn.commit()
        conn.close()

        # Check expiration
        expires_at = datetime.fromisoformat(result["expires_at"])
        if datetime.utcnow() > expires_at:
            return None

        return result

    # --- Activity Log ---

    async def log_activity(
        self, tenant_id: str, platform: str, action: str, details: str = ""
    ):
        """Log an OAuth activity."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO oauth_activity_log (tenant_id, platform, action, details) VALUES (?, ?, ?, ?)",
            (tenant_id, platform, action, details),
        )
        conn.commit()
        conn.close()
