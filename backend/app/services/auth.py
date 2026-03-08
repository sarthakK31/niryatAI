import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from app.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRY_HOURS
from app.database import get_cursor


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


def register_user(email: str, password: str, full_name: str,
                  company_name: str = None, hs_codes: list = None, state: str = None):
    pwd_hash = hash_password(password)
    with get_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO users (email, password_hash, full_name, company_name, hs_codes, state)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, email, full_name, company_name, hs_codes, state, created_at
        """, (email, pwd_hash, full_name, company_name, hs_codes, state))
        row = cur.fetchone()
    return {
        "id": str(row[0]), "email": row[1], "full_name": row[2],
        "company_name": row[3], "hs_codes": row[4], "state": row[5],
        "created_at": row[6]
    }


def authenticate_user(email: str, password: str):
    with get_cursor() as cur:
        cur.execute("""
            SELECT id, email, password_hash, full_name, company_name, hs_codes, state, created_at
            FROM users WHERE email = %s
        """, (email,))
        row = cur.fetchone()
    if not row or not verify_password(password, row[2]):
        return None
    print("[DEBUG] DB Fetched Row: ", row)
    return {
        "id": str(row[0]), "email": row[1], "full_name": row[3],
        "company_name": row[4], "hs_codes": row[5], "state": row[6],
        "created_at": row[7]
    }


def get_user_by_id(user_id: str):
    with get_cursor() as cur:
        cur.execute("""
            SELECT id, email, full_name, company_name, hs_codes, state, created_at
            FROM users WHERE id = %s
        """, (user_id,))
        row = cur.fetchone()
    if not row:
        return None
    return {
        "id": str(row[0]), "email": row[1], "full_name": row[2],
        "company_name": row[3], "hs_codes": row[4], "state": row[5],
        "created_at": row[6]
    }


def update_user(user_id: str, full_name: str = None, company_name: str = None,
                hs_codes: list = None, state: str = None):
    updates = []
    params = []
    if full_name is not None:
        updates.append("full_name = %s")
        params.append(full_name)
    if company_name is not None:
        updates.append("company_name = %s")
        params.append(company_name)
    if hs_codes is not None:
        updates.append("hs_codes = %s")
        params.append(hs_codes)
    if state is not None:
        updates.append("state = %s")
        params.append(state)
    if not updates:
        return get_user_by_id(user_id)

    updates.append("updated_at = NOW()")
    params.append(user_id)

    with get_cursor(commit=True) as cur:
        cur.execute(f"""
            UPDATE users SET {', '.join(updates)}
            WHERE id = %s
            RETURNING id, email, full_name, company_name, hs_codes, state, created_at
        """, params)
        row = cur.fetchone()
    return {
        "id": str(row[0]), "email": row[1], "full_name": row[2],
        "company_name": row[3], "hs_codes": row[4], "state": row[5],
        "created_at": row[6]
    }
