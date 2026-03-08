"""PostgreSQL-backed chat session and message persistence.

Replaces the in-memory defaultdict session store and Mem0.
"""

from app.database import get_cursor


def create_session(user_id: str, title: str = "New Chat") -> str:
    with get_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO chat_sessions (user_id, title)
            VALUES (%s, %s) RETURNING id
        """, (user_id, title))
        return str(cur.fetchone()[0])


def get_user_sessions(user_id: str, limit: int = 20):
    with get_cursor() as cur:
        cur.execute("""
            SELECT id, title, created_at, updated_at
            FROM chat_sessions
            WHERE user_id = %s
            ORDER BY updated_at DESC
            LIMIT %s
        """, (user_id, limit))
        rows = cur.fetchall()
    return [
        {"id": str(r[0]), "title": r[1], "created_at": r[2], "updated_at": r[3]}
        for r in rows
    ]


def get_session_messages(session_id: str, limit: int = 50):
    with get_cursor() as cur:
        cur.execute("""
            SELECT role, content, image_description, created_at
            FROM chat_messages
            WHERE session_id = %s
            ORDER BY created_at ASC
            LIMIT %s
        """, (session_id, limit))
        rows = cur.fetchall()
    return [
        {"role": r[0], "content": r[1], "image_description": r[2], "created_at": r[3]}
        for r in rows
    ]


def add_message(session_id: str, role: str, content: str,
                image_description: str = None):
    with get_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO chat_messages (session_id, role, content, image_description)
            VALUES (%s, %s, %s, %s)
        """, (session_id, role, content, image_description))
        # Update session timestamp and auto-title from first user message
        cur.execute("""
            UPDATE chat_sessions SET updated_at = NOW() WHERE id = %s
        """, (session_id,))


def auto_title_session(session_id: str, first_message: str):
    """Set session title from the first user message (truncated)."""
    title = first_message[:60].strip()
    if len(first_message) > 60:
        title += "..."
    with get_cursor(commit=True) as cur:
        cur.execute("""
            UPDATE chat_sessions SET title = %s
            WHERE id = %s AND title = 'New Chat'
        """, (title, session_id))


def build_chat_context(session_id: str, max_messages: int = 10) -> str:
    """Build a formatted conversation context string for the agent."""
    messages = get_session_messages(session_id, limit=max_messages)
    if not messages:
        return ""
    lines = []
    for msg in messages:
        role = "User" if msg["role"] == "user" else "Assistant"
        lines.append(f"{role}: {msg['content']}")
    return "\n".join(lines)
