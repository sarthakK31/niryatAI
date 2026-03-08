from fastapi import APIRouter, Depends
from app.middleware import get_current_user
from app.services.readiness import get_readiness_summary
from app.services.market_intel import get_market_summary_for_user, get_map_data

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/")
def get_dashboard(user=Depends(get_current_user)):
    """Aggregated dashboard data for the frontend."""
    user_hs = user.get("hs_codes") or []
    readiness = get_readiness_summary(user["id"])
    top_markets = get_market_summary_for_user(user_hs)
    map_markets = get_map_data(user_hs)

    return {
        "user": {
            "name": user["full_name"],
            "company": user.get("company_name"),
        },
        "readiness": readiness,
        "top_markets": top_markets[:5],
        "map_data": map_markets,
    }
