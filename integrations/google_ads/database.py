# ===============================================================================
# NADAKKI AI Suite - Database Abstraction Layer
# core/database.py
# ===============================================================================

"""
Async database interface with two implementations:
1. AsyncPGDatabase - PostgreSQL via asyncpg (production)
2. InMemoryDatabase - Dict-based mock (development/testing)

Both implement the same interface so all components work identically
regardless of backend.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import logging
import os

logger = logging.getLogger("nadakki.database")


class DatabaseInterface:
    """Abstract interface for async database operations."""
    
    async def execute(self, query: str, *args) -> Any:
        raise NotImplementedError
    
    async def fetchone(self, query: str, *args) -> Optional[Dict]:
        raise NotImplementedError
    
    async def fetch(self, query: str, *args) -> List[Dict]:
        raise NotImplementedError
    
    async def initialize(self):
        raise NotImplementedError
    
    async def close(self):
        raise NotImplementedError


class AsyncPGDatabase(DatabaseInterface):
    """PostgreSQL implementation using asyncpg."""
    
    def __init__(self, dsn: str = None):
        self.dsn = dsn or os.getenv(
            "DATABASE_URL",
            "postgresql://nadakki:nadakki@localhost:5432/nadakki_google_ads"
        )
        self.pool = None
    
    async def initialize(self):
        """Create connection pool."""
        try:
            import asyncpg
            self.pool = await asyncpg.create_pool(
                self.dsn,
                min_size=2,
                max_size=10,
                command_timeout=30,
            )
            logger.info("PostgreSQL pool created")
        except ImportError:
            raise ImportError(
                "asyncpg is required for PostgreSQL. "
                "Install with: pip install asyncpg"
            )
    
    async def execute(self, query: str, *args) -> Any:
        async with self.pool.acquire() as conn:
            result = await conn.execute(query, *args)
            # asyncpg returns "DELETE 5" etc.
            if result and isinstance(result, str):
                parts = result.split()
                if len(parts) >= 2 and parts[-1].isdigit():
                    return int(parts[-1])
            return result
    
    async def fetchone(self, query: str, *args) -> Optional[Dict]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None
    
    async def fetch(self, query: str, *args) -> List[Dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(r) for r in rows]
    
    async def close(self):
        if self.pool:
            await self.pool.close()
            logger.info("PostgreSQL pool closed")


class InMemoryDatabase(DatabaseInterface):
    """
    In-memory database for development and testing.
    
    Supports basic INSERT, SELECT, UPDATE, DELETE patterns
    used by the NADAKKI components. NOT a full SQL engine.
    """
    
    def __init__(self):
        self._tables: Dict[str, List[Dict]] = {}
        self._auto_increment: Dict[str, int] = {}
    
    async def initialize(self):
        """Initialize in-memory tables."""
        self._tables = {
            "tenant_credentials": [],
            "credential_access_log": [],
            "idempotency_keys": [],
            "sagas": [],
            "saga_steps": [],
        }
        self._auto_increment = {
            "credential_access_log": 0,
            "saga_steps": 0,
        }
        logger.info("InMemoryDatabase initialized")
    
    async def execute(self, query: str, *args) -> Any:
        """Execute a write operation (INSERT, UPDATE, DELETE)."""
        query_lower = query.strip().lower()
        
        if query_lower.startswith("insert"):
            return await self._handle_insert(query, args)
        elif query_lower.startswith("update"):
            return await self._handle_update(query, args)
        elif query_lower.startswith("delete"):
            return await self._handle_delete(query, args)
        elif query_lower.startswith("create"):
            return "CREATE"  # Schema creation - no-op in memory
        
        return 0
    
    async def fetchone(self, query: str, *args) -> Optional[Dict]:
        """Fetch a single row."""
        rows = await self.fetch(query, *args)
        return rows[0] if rows else None
    
    async def fetch(self, query: str, *args) -> List[Dict]:
        """Fetch multiple rows."""
        table_name = self._extract_table(query)
        if not table_name or table_name not in self._tables:
            return []
        
        rows = self._tables[table_name]
        
        # Apply WHERE filters
        filtered = self._apply_where(rows, query, args)
        
        # Apply ORDER BY
        if "order by" in query.lower():
            order_field = self._extract_order_field(query)
            if order_field:
                reverse = "desc" in query.lower().split("order by")[1]
                filtered.sort(
                    key=lambda r: r.get(order_field, ""),
                    reverse=reverse,
                )
        
        # Apply LIMIT
        limit = self._extract_limit(query)
        if limit:
            filtered = filtered[:limit]
        
        return filtered
    
    async def close(self):
        """Clear all data."""
        self._tables.clear()
        logger.info("InMemoryDatabase closed")
    
    # ---------------------------------------------------------------------
    # Internal Handlers
    # ---------------------------------------------------------------------
    
    async def _handle_insert(self, query: str, args) -> Any:
        table_name = self._extract_table(query)
        if not table_name:
            return 0
        
        if table_name not in self._tables:
            self._tables[table_name] = []
        
        # Extract column names from query
        cols = self._extract_columns(query)
        
        # Build row
        row = {}
        for i, col in enumerate(cols):
            if i < len(args):
                row[col] = args[i]
            else:
                row[col] = None
        
        # Add timestamps
        now = datetime.utcnow()
        if "created_at" not in row or row["created_at"] is None:
            row["created_at"] = now
        if "timestamp" not in row or row["timestamp"] is None:
            row["timestamp"] = now
        
        # Handle auto-increment
        if table_name in self._auto_increment:
            self._auto_increment[table_name] += 1
            if "id" not in row or row["id"] is None:
                row["id"] = self._auto_increment[table_name]
        
        # Handle ON CONFLICT (upsert)
        if "on conflict" in query.lower():
            conflict_col = self._extract_conflict_column(query)
            if conflict_col and conflict_col in row:
                # Find existing
                existing_idx = None
                for idx, existing in enumerate(self._tables[table_name]):
                    if existing.get(conflict_col) == row[conflict_col]:
                        existing_idx = idx
                        break
                
                if existing_idx is not None:
                    # Update existing
                    self._tables[table_name][existing_idx].update(row)
                    return 1
        
        self._tables[table_name].append(row)
        return 1
    
    async def _handle_update(self, query: str, args) -> int:
        table_name = self._extract_table(query)
        if not table_name or table_name not in self._tables:
            return 0
        
        rows = self._tables[table_name]
        filtered = self._apply_where(rows, query, args)
        
        # Extract SET values
        set_pairs = self._extract_set_pairs(query, args)
        
        count = 0
        for row in filtered:
            for key, value in set_pairs.items():
                row[key] = value
            count += 1
        
        return count
    
    async def _handle_delete(self, query: str, args) -> int:
        table_name = self._extract_table(query)
        if not table_name or table_name not in self._tables:
            return 0
        
        rows = self._tables[table_name]
        to_keep = []
        deleted = 0
        
        for row in rows:
            if self._matches_where(row, query, args):
                deleted += 1
            else:
                to_keep.append(row)
        
        self._tables[table_name] = to_keep
        return deleted
    
    # ---------------------------------------------------------------------
    # SQL Parsing Helpers (simplified)
    # ---------------------------------------------------------------------
    
    def _extract_table(self, query: str) -> Optional[str]:
        """Extract table name from query."""
        q = query.lower().strip()
        
        for keyword in ["from", "into", "update", "table"]:
            if keyword in q:
                parts = q.split(keyword)
                if len(parts) > 1:
                    table_part = parts[1].strip().split()[0]
                    # Clean up
                    table_part = table_part.strip("(").strip(")").strip(";")
                    if table_part and table_part.isidentifier():
                        return table_part
        
        return None
    
    def _extract_columns(self, query: str) -> List[str]:
        """Extract column names from INSERT INTO ... (...) VALUES."""
        try:
            # Find content between first ( and first )
            start = query.index("(") + 1
            end = query.index(")")
            cols_str = query[start:end]
            return [c.strip().strip('"') for c in cols_str.split(",")]
        except (ValueError, IndexError):
            return []
    
    def _extract_conflict_column(self, query: str) -> Optional[str]:
        """Extract conflict column from ON CONFLICT (col)."""
        q = query.lower()
        try:
            idx = q.index("on conflict")
            rest = query[idx:]
            start = rest.index("(") + 1
            end = rest.index(")")
            return rest[start:end].strip()
        except (ValueError, IndexError):
            return None
    
    def _apply_where(self, rows: List[Dict], query: str, args) -> List[Dict]:
        """Filter rows based on WHERE clause."""
        return [r for r in rows if self._matches_where(r, query, args)]
    
    def _matches_where(self, row: Dict, query: str, args) -> bool:
        """Check if a row matches WHERE conditions."""
        q = query.lower()
        
        if "where" not in q:
            return True
        
        where_part = q.split("where")[1].split("order by")[0].split("limit")[0]
        
        # Parse simple conditions: col = $N, col != $N
        conditions = where_part.replace(" and ", "&&").split("&&")
        
        for condition in conditions:
            condition = condition.strip()
            
            # Skip NOW() comparisons and subqueries
            if "now()" in condition or "filter" in condition:
                continue
            
            # Handle: col = $N
            if "=" in condition and "$" in condition:
                parts = condition.split("=")
                if len(parts) == 2:
                    col = parts[0].strip().split(".")[-1].strip()
                    param_str = parts[1].strip()
                    
                    if param_str.startswith("$"):
                        try:
                            param_idx = int(param_str.replace("$", "")) - 1
                            if param_idx < len(args):
                                if row.get(col) != args[param_idx]:
                                    return False
                        except (ValueError, IndexError):
                            pass
        
        return True
    
    def _extract_set_pairs(self, query: str, args) -> Dict[str, Any]:
        """Extract SET column=value pairs from UPDATE."""
        result = {}
        q = query.lower()
        
        try:
            set_part = q.split("set")[1].split("where")[0]
            pairs = set_part.split(",")
            
            for pair in pairs:
                if "=" in pair and "$" in pair:
                    col, val = pair.split("=", 1)
                    col = col.strip()
                    val = val.strip()
                    
                    if val.startswith("$"):
                        try:
                            idx = int(val.replace("$", "")) - 1
                            if idx < len(args):
                                result[col] = args[idx]
                        except (ValueError, IndexError):
                            pass
                elif "now()" in pair.lower():
                    col = pair.split("=")[0].strip()
                    result[col] = datetime.utcnow()
        except (ValueError, IndexError):
            pass
        
        return result
    
    def _extract_order_field(self, query: str) -> Optional[str]:
        """Extract ORDER BY field."""
        q = query.lower()
        try:
            order_part = q.split("order by")[1].split("limit")[0]
            field = order_part.strip().split()[0]
            return field
        except (ValueError, IndexError):
            return None
    
    def _extract_limit(self, query: str) -> Optional[int]:
        """Extract LIMIT value."""
        q = query.lower()
        try:
            limit_part = q.split("limit")[1].strip()
            return int(limit_part.split()[0])
        except (ValueError, IndexError):
            return None


# -----------------------------------------------------------------------------
# Factory
# -----------------------------------------------------------------------------

async def create_database(use_memory: bool = None) -> DatabaseInterface:
    """
    Create and initialize the appropriate database.
    
    Args:
        use_memory: Force in-memory mode. If None, auto-detect:
            - If DATABASE_URL is set > PostgreSQL
            - Otherwise > InMemory
    """
    if use_memory is None:
        use_memory = not os.getenv("DATABASE_URL")
    
    if use_memory:
        db = InMemoryDatabase()
    else:
        db = AsyncPGDatabase()
    
    await db.initialize()
    return db

