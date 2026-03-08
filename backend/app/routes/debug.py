from fastapi import APIRouter, Request

router = APIRouter(prefix="/api", tags=["debug"])

@router.get("/debug")
async def debug(request: Request):
    print("HEADERS:", request.headers)
    return dict(request.headers)