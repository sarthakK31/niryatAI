"""HS code reference endpoints."""

from fastapi import APIRouter, Depends, Query
from app.middleware import get_current_user
from app.services.hs_lookup import search_hs_codes, get_descriptions_for_codes

router = APIRouter(prefix="/api/hs-codes", tags=["hs-codes"])


@router.get("/search")
def search(q: str = Query(..., min_length=1), limit: int = Query(20, le=50), _=Depends(get_current_user)):
    """Search HS codes by code prefix or product description keyword."""
    return search_hs_codes(q, limit)


@router.post("/descriptions")
def descriptions(hs_codes: list[str], _=Depends(get_current_user)):
    """Get product descriptions for a list of HS codes."""
    return get_descriptions_for_codes(hs_codes)
