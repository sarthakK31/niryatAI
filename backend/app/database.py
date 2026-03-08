import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from app.config import DATABASE_URL

# Connection pool: min 2, max 10 connections
_pool = None


def init_pool():
    global _pool
    if _pool is None:
        _pool = pool.ThreadedConnectionPool(2, 10, DATABASE_URL)
    return _pool


def get_pool():
    global _pool
    if _pool is None:
        init_pool()
    return _pool


@contextmanager
def get_connection():
    """Get a connection from the pool, auto-return on exit."""
    p = get_pool()
    conn = p.getconn()
    try:
        yield conn
    finally:
        # Reset connection state before returning to pool.
        # This prevents "idle in transaction" leaks that cause
        # subsequent queries on this connection to fail.
        try:
            conn.reset()
        except Exception:
            pass
        p.putconn(conn)


@contextmanager
def get_cursor(commit=False):
    """Get a cursor from a pooled connection."""
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
