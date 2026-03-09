import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/testdb"
)

# AWS
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET", "niryat-export-docs")

# Model provider: "bedrock", "ollama", or "gemini"
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "bedrock")

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Bedrock
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514")
BEDROCK_VISION_MODEL_ID = os.getenv("BEDROCK_VISION_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514")

# Ollama (local dev fallback)
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b-instruct-fp16")
OLLAMA_VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "qwen2.5vl:7b")

# Auth
JWT_SECRET = os.getenv("JWT_SECRET", "niryat-dev-secret-change-in-prod")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24

# Frontend URL (for CORS)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
