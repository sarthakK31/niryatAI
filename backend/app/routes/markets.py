from fastapi import APIRouter, Depends, Query
from app.middleware import get_current_user
from app.services.market_intel import (
    get_top_markets, get_country_risks, get_available_hs_codes,
    get_market_summary_for_user,
)

router = APIRouter(prefix="/api/markets", tags=["markets"])


@router.get("/top")
def top_markets(hs_code: str = Query(None), limit: int = Query(20), user=Depends(get_current_user)):
    return get_top_markets(hs_code=hs_code, limit=limit)


@router.get("/risks")
def country_risks(user=Depends(get_current_user)):
    return get_country_risks()


@router.get("/hs-codes")
def hs_codes(user=Depends(get_current_user)):
    return get_available_hs_codes()


@router.get("/my-markets")
def my_markets(user=Depends(get_current_user)):
    """Get best markets for the current user's registered HS codes."""
    return get_market_summary_for_user(user.get("hs_codes") or [])
