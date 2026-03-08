from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_pool
from app.routes import auth, chat, readiness, markets, profile, dashboard, debug

app = FastAPI(
    title="Niryat AI",
    description="AI-Guided Export Readiness and Intelligence Platform for Indian MSMEs",
    version="1.0.0",
)

# CORS — allow frontend during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_pool()


# Register routes
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(readiness.router)
app.include_router(markets.router)
app.include_router(profile.router)
app.include_router(dashboard.router)
app.include_router(debug.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "niryat-ai"}
