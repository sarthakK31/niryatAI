from fastapi import APIRouter, Depends
from app.middleware import get_current_user
from app.services.readiness import (
    get_all_steps_with_progress, mark_substep, get_readiness_summary,
)
from app.models.schemas import MarkSubstepRequest

router = APIRouter(prefix="/api/readiness", tags=["readiness"])


@router.get("/steps")
def get_steps(user=Depends(get_current_user)):
    return get_all_steps_with_progress(user["id"])


@router.get("/summary")
def get_summary(user=Depends(get_current_user)):
    return get_readiness_summary(user["id"])


@router.post("/mark")
def mark_step(data: MarkSubstepRequest, user=Depends(get_current_user)):
    mark_substep(user["id"], data.substep_id, data.completed, data.notes)
    return {"status": "updated"}
