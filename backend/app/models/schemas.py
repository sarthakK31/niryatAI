from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


# ---- Auth ----
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    company_name: Optional[str] = None
    hs_codes: Optional[list[str]] = None
    state: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserProfile(BaseModel):
    id: str
    email: str
    full_name: str
    company_name: Optional[str]
    hs_codes: Optional[list[str]]
    state: Optional[str]
    created_at: datetime


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    hs_codes: Optional[list[str]] = None
    state: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile


# ---- Chat ----
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


class ChatSession(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime


class ChatMessage(BaseModel):
    role: str
    content: str
    image_description: Optional[str] = None
    created_at: datetime


# ---- Export Readiness ----
class ReadinessStep(BaseModel):
    step_number: int
    title: str
    description: Optional[str]
    category: str
    substeps: list["ReadinessSubstep"]
    completed_count: int
    total_count: int


class ReadinessSubstep(BaseModel):
    id: int
    substep_number: int
    title: str
    description: Optional[str]
    completed: bool
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None


class MarkSubstepRequest(BaseModel):
    substep_id: int
    completed: bool
    notes: Optional[str] = None


# ---- Market Intelligence ----
class MarketIntelligenceRow(BaseModel):
    country: str
    hs_code: str
    avg_growth_5y: Optional[float]
    volatility: Optional[float]
    total_import: Optional[float]
    opportunity_score: Optional[float]
    ai_summary: Optional[str]


class CountryRiskRow(BaseModel):
    country: str
    stability_index: Optional[float]
    risk_score: Optional[float]
