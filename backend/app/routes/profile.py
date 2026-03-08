from fastapi import APIRouter, Depends
from app.middleware import get_current_user
from app.services.auth import update_user
from app.models.schemas import UserProfile, UserUpdate

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("/", response_model=UserProfile)
def get_profile(user=Depends(get_current_user)):
    return UserProfile(**user)


@router.put("/", response_model=UserProfile)
def update_profile(data: UserUpdate, user=Depends(get_current_user)):
    updated = update_user(
        user_id=user["id"],
        full_name=data.full_name,
        company_name=data.company_name,
        hs_codes=data.hs_codes,
        state=data.state,
    )
    return UserProfile(**updated)
