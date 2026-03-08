"""JWT authentication middleware."""

import traceback
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.auth import decode_token, get_user_by_id

security = HTTPBearer(auto_error=False)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract and validate the current user from JWT token."""
    # Step 1: Decode JWT
    try:
        payload = decode_token(credentials.credentials)
    except Exception as e:
        print(f"[AUTH ERROR] Token decode failed: {type(e).__name__}: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {type(e).__name__}: {e}")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing 'sub' claim")

    # Step 2: Look up user in DB
    try:
        user = get_user_by_id(user_id)
    except Exception as e:
        print(f"[AUTH ERROR] DB lookup failed for user_id={user_id}: {type(e).__name__}: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Database error during auth: {e}")

    if not user:
        print(f"[AUTH ERROR] No user found for id={user_id}")
        raise HTTPException(status_code=401, detail=f"User not found for id: {user_id}")

    return user
