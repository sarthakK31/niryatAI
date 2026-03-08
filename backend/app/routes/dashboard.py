from fastapi import APIRouter, Depends
from app.middleware import get_current_user
from app.services.readiness import get_readiness_summary
from app.services.market_intel import get_market_summary_for_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/")
def get_dashboard(user=Depends(get_current_user)):
    """Aggregated dashboard data for the frontend."""
    readiness = get_readiness_summary(user["id"])
    top_markets = get_market_summary_for_user(user.get("hs_codes") or [])

    return {
        "user": {
            "name": user["full_name"],
            "company": user.get("company_name"),
        },
        "readiness": readiness,
        "top_markets": top_markets[:5],
    }
