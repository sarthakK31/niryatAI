from fastapi import APIRouter, HTTPException
from app.models.schemas import UserRegister, UserLogin, TokenResponse, UserProfile
from app.services.auth import register_user, authenticate_user, create_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(data: UserRegister):
    try:
        user = register_user(
            email=data.email,
            password=data.password,
            full_name=data.full_name,
            company_name=data.company_name,
            hs_codes=data.hs_codes,
            state=data.state,
        )
    except Exception as e:
        if "duplicate key" in str(e).lower():
            raise HTTPException(status_code=400, detail="Email already registered")
        raise HTTPException(status_code=500, detail=str(e))

    token = create_token(user["id"])
    return TokenResponse(access_token=token, user=UserProfile(**user))


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin):
    user = authenticate_user(data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token(user["id"])
    return TokenResponse(access_token=token, user=UserProfile(**user))
