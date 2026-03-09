"""Niryat AI Agent - Supports both AWS Bedrock (production) and Ollama (local dev)."""

from strands import Agent
from strands import tool
import boto3
import psycopg2
import pandas as pd
import re
import json
import base64
from app.config import (
    MODEL_PROVIDER, AWS_REGION,
    BEDROCK_MODEL_ID, BEDROCK_VISION_MODEL_ID,
    OLLAMA_HOST, OLLAMA_MODEL, OLLAMA_VISION_MODEL,
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET,
    DATABASE_URL, GEMINI_API_KEY,
)

# ============================
# SYSTEM PROMPT
# ============================

SYSTEM_PROMPT = """You are Niryat AI, an expert export readiness advisor for Indian MSMEs (Micro, Small and Medium Enterprises).

YOUR ROLE:
You help first-time Indian exporters understand how to start exporting, become export-ready, and find the best global markets for their products. You speak in simple, clear language that non-technical business owners can understand.

YOUR DATA SOURCES:
You have access to these tools — ALWAYS use them instead of guessing:

1. POSTGRESQL DATABASE (market intelligence):
   - query_market_data: Run SQL queries on the trade database
   - get_table_info: See available tables and their columns

   Tables available:
   - market_intelligence (country, hs_code, avg_growth_5y, volatility, total_import, opportunity_score, ai_summary)
   - country_risk (country, stability_index, risk_score)  

2. S3 DOCUMENT STORE (export procedures):
   - search_export_docs: Search for export guidance documents by keyword
   - read_export_doc: Read a specific document from S3

3. USER PROGRESS TRACKING:
   - get_user_progress: Get the user's export readiness checklist progress, completed steps, and next recommended action
   Use this when the user asks about their progress, what to do next, where they stand, or anything about their export readiness journey.

4. IMAGE PROCESSING:
   - analyze_image: Extract and describe text from an uploaded image

CRITICAL RULES — YOU MUST FOLLOW THESE:

1. NEVER HALLUCINATE DATA.
   - If a user asks about market data, trade statistics, opportunity scores, or country information: YOU MUST query the database using query_market_data. Do NOT guess numbers.
   - If the data is not in the database or S3: respond with "I don't have this specific data in my database. Let me tell you what I do have..." and suggest what you CAN help with.

2. ALWAYS USE TOOLS FIRST.
   - For market/trade questions → query_market_data
   - For export process questions → search_export_docs, then read_export_doc
   - For progress/readiness/next-step questions → get_user_progress
   - For image questions → analyze_image
   - NEVER answer a data question from memory alone.

3. SQL RULES:
   - Only generate SELECT queries. Never INSERT, UPDATE, DELETE, DROP, or ALTER.
   - Only query these tables: market_intelligence, country_risk
   - When filtering by country or hs_code, use ILIKE for flexible matching.
   - Always LIMIT results to 25 rows unless the user asks for more.
   - Example good query: SELECT country, opportunity_score, ai_summary FROM market_intelligence WHERE hs_code = '0901' ORDER BY opportunity_score DESC LIMIT 10

4. EXPLAIN YOUR REASONING.
   When you give a recommendation, explain WHY. For example:
   "Germany ranks highest for HS code 0901 (coffee) because it has an opportunity score of 0.85, driven by high import volume ($2.1B) and steady 5-year growth of 8%."

5. LANGUAGE:
   - Use simple English. Avoid jargon.
   - When using trade terms (HS code, IEC, RCMC, FOB), briefly explain them.
   - Be encouraging — many users are nervous first-time exporters.

6. SCOPE:
   - You help with: export procedures, market intelligence, document guidance, export readiness.
   - You do NOT help with: domestic sales, investment advice, legal disputes, non-trade topics.
   - If asked something outside your scope, politely say: "I specialize in export guidance for Indian MSMEs. For [topic], I'd recommend consulting [appropriate resource]."

RESPONSE FORMAT:
- Keep responses concise (under 300 words unless the user asks for detail).
- Use bullet points for lists.
- When showing data, format it as a clear table or ranked list.
- End actionable responses with a suggested next step.
"""


# ============================
# TOOL DEFINITIONS
# ============================

def _get_db_connection():
    return psycopg2.connect(DATABASE_URL)


def _get_s3_client():
    if AWS_ACCESS_KEY_ID:
        return boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION,
        )
    # On EC2/ECS, use IAM role credentials automatically
    return boto3.client("s3", region_name=AWS_REGION)


ALLOWED_TABLES = {"market_intelligence", "country_risk"}
BLOCKED_KEYWORDS = {"insert", "update", "delete", "drop", "alter", "truncate", "create", "grant", "revoke"}

# Current user context — set before each agent invocation
_current_user_id = None


@tool
def query_market_data(sql_query: str) -> str:
    """
    Execute a read-only SQL query against the trade intelligence database.
    Only SELECT queries on market_intelligence and country_risk tables are allowed.
    Use this tool whenever you need trade data, opportunity scores, country risks, or import statistics.
    """
    lower = sql_query.strip().lower()

    if not lower.startswith("select"):
        return "ERROR: Only SELECT queries are allowed."

    if any(kw in lower for kw in BLOCKED_KEYWORDS):
        return "ERROR: This query contains blocked keywords. Only SELECT queries are allowed."

    referenced = re.findall(r'(?:from|join)\s+([a-zA-Z_][a-zA-Z0-9_]*)', lower)
    for t in referenced:
        if t not in ALLOWED_TABLES:
            return f"ERROR: Table '{t}' is not accessible. Available tables: market_intelligence, country_risk"

    try:
        conn = _get_db_connection()
        df = pd.read_sql(sql_query, conn)
        conn.close()

        if df.empty:
            return "No results found for this query. The data may not exist in the database for the specified filters."

        if len(df) <= 25:
            return df.to_string(index=False)
        else:
            return df.head(25).to_string(index=False) + f"\n\n... showing 25 of {len(df)} results."

    except Exception as e:
        return f"ERROR executing query: {str(e)}. Please check the SQL syntax and try again."


@tool
def get_table_info() -> str:
    """
    Get the schema of available database tables.
    Use this when you need to know what columns and data types are available before writing a query.
    """
    try:
        conn = _get_db_connection()
        df = pd.read_sql("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name IN ('market_intelligence', 'country_risk')
            ORDER BY table_name, ordinal_position
        """, conn)
        conn.close()
        return df.to_string(index=False)
    except Exception as e:
        return f"ERROR: {str(e)}"


@tool
def search_export_docs(query: str) -> str:
    """
    Search for export guidance documents in S3 by keyword.
    Use this when the user asks about export procedures, registrations, compliance, documentation, or government schemes.
    Returns a list of matching document names.
    """
    try:
        s3 = _get_s3_client()
        response = s3.list_objects_v2(Bucket=S3_BUCKET)
        if "Contents" not in response:
            return "No documents found in the export guidance store."

        matches = []
        for obj in response["Contents"]:
            if query.lower() in obj["Key"].lower():
                matches.append(obj["Key"])

        if not matches:
            return f"No documents matching '{query}' found. Try broader keywords like 'IEC', 'registration', 'compliance', 'shipping'."

        return "Found documents:\n" + "\n".join(f"- {m}" for m in matches)

    except Exception as e:
        return f"ERROR accessing document store: {str(e)}"


@tool
def read_export_doc(document_key: str) -> str:
    """
    Read the full content of an export guidance document from S3.
    Use the search_export_docs tool first to find the correct document key, then use this tool to read it.
    """
    try:
        s3 = _get_s3_client()
        obj = s3.get_object(Bucket=S3_BUCKET, Key=document_key)
        content = obj["Body"].read().decode("utf-8")
        if len(content) > 4000:
            return content[:4000] + "\n\n[Document truncated. Key information is in the section above.]"
        return content
    except Exception as e:
        return f"ERROR reading document: {str(e)}"


@tool
def analyze_image(image_description: str) -> str:
    """
    Analyze an image that was uploaded by the user.
    The image has already been processed and its description is provided.
    Use this to help the user understand forms, certificates, compliance documents, or shipping labels shown in the image.
    """
    return f"Image analysis:\n{image_description}"


@tool
def get_user_progress() -> str:
    """
    Get the current user's export readiness progress and next steps.
    Use this when the user asks about their progress, where they are in the export journey,
    what they should do next, or anything related to their export readiness checklist.
    Returns: overall completion percentage, completed steps, and the next recommended step.
    """
    global _current_user_id
    if not _current_user_id:
        return "Unable to retrieve progress: user not identified."

    try:
        conn = _get_db_connection()
        cur = conn.cursor()

        # Get all steps with user's completion status
        cur.execute("""
            SELECT
                es.step_number,
                es.title AS step_title,
                es.category,
                sub.substep_number,
                sub.title AS substep_title,
                COALESCE(ur.completed, false) AS completed,
                ur.completed_at
            FROM export_steps es
            JOIN export_substeps sub ON sub.step_id = es.id
            LEFT JOIN user_readiness ur ON ur.substep_id = sub.id AND ur.user_id = %s
            ORDER BY es.step_number, sub.substep_number
        """, (_current_user_id,))
        rows = cur.fetchall()
        conn.close()

        if not rows:
            return "No export readiness steps found in the system."

        total = len(rows)
        done = sum(1 for r in rows if r[5])
        pct = round(done / total * 100, 1) if total > 0 else 0

        # Build step-by-step summary
        steps = {}
        next_step = None
        for r in rows:
            step_num, step_title, category, sub_num, sub_title, completed, completed_at = r
            if step_num not in steps:
                steps[step_num] = {"title": step_title, "category": category, "substeps": []}
            status = "DONE" if completed else "PENDING"
            steps[step_num]["substeps"].append(f"  {sub_num}. [{status}] {sub_title}")
            if not completed and next_step is None:
                next_step = f"Step {step_num}: {step_title} → {sub_title}"

        lines = [f"Export Readiness: {pct}% complete ({done}/{total} substeps done)\n"]
        for step_num in sorted(steps.keys()):
            s = steps[step_num]
            lines.append(f"Step {step_num}: {s['title']} ({s['category']})")
            lines.extend(s["substeps"])
            lines.append("")

        if next_step:
            lines.append(f"NEXT RECOMMENDED ACTION: {next_step}")
        else:
            lines.append("All steps completed! The user is export-ready.")

        return "\n".join(lines)

    except Exception as e:
        return f"ERROR fetching progress: {str(e)}"


# ============================
# VISION PROCESSING
# ============================

def process_image(image_base64: str) -> str:
    """Process an image using the configured vision model."""
    if MODEL_PROVIDER == "bedrock":
        return _process_image_bedrock(image_base64)
    elif MODEL_PROVIDER == "gemini":
        return _process_image_gemini(image_base64)
    else:
        return _process_image_ollama(image_base64)


def _process_image_bedrock(image_base64: str) -> str:
    """Process image using Bedrock's Claude vision."""
    try:
        client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
        response = client.converse(
            modelId=BEDROCK_VISION_MODEL_ID,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "image": {
                            "format": "png",
                            "source": {"bytes": base64.b64decode(image_base64)},
                        }
                    },
                    {
                        "text": "Describe this image in detail. If it contains a form, certificate, document, or label, extract all visible text and explain what the document is."
                    },
                ],
            }],
            inferenceConfig={"maxTokens": 1024},
        )
        return response["output"]["message"]["content"][0]["text"]
    except Exception as e:
        return f"Could not process image: {str(e)}"


def _process_image_gemini(image_base64: str) -> str:
    """Process image using Google Gemini vision."""
    import requests
    try:
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}",
            json={
                "contents": [{
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": image_base64,
                            }
                        },
                        {
                            "text": "Describe this image in detail. If it contains a form, certificate, document, or label, extract all visible text and explain what the document is."
                        },
                    ]
                }],
                "generationConfig": {"maxOutputTokens": 1024},
            },
            timeout=120,
        )
        r.raise_for_status()
        result = r.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"Could not process image: {str(e)}"


def _process_image_ollama(image_base64: str) -> str:
    """Process image using local Ollama vision model."""
    import requests
    try:
        r = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json={
                "model": OLLAMA_VISION_MODEL,
                "stream": False,
                "messages": [{
                    "role": "user",
                    "content": "Describe this image in detail. If it contains a form, certificate, document, or label, extract all visible text and explain what the document is.",
                    "images": [image_base64],
                }],
            },
            timeout=300,
        )
        return r.json()["message"]["content"]
    except Exception as e:
        return f"Could not process image: {str(e)}"


# ============================
# AGENT FACTORY
# ============================

def create_agent() -> Agent:
    """Create agent using configured model provider."""
    if MODEL_PROVIDER == "bedrock":
        from strands.models.bedrock import BedrockModel
        model = BedrockModel(
            model_id=BEDROCK_MODEL_ID,
            region_name=AWS_REGION,
        )
        print(f"[AGENT] Using Bedrock model: {BEDROCK_MODEL_ID}")
    elif MODEL_PROVIDER == "gemini":
        from strands.models.gemini import GeminiModel

        model = GeminiModel(
            client_args={
                "api_key": GEMINI_API_KEY,
            },
            model_id="gemini-2.5-flash",
            params={
                "temperature": 0.7,
                "max_output_tokens": 2048,
                "top_p": 0.9,
                "top_k": 40
            }
        )
        print(f"[AGENT] Using Gemini model: gemini-2.5-flash")
    else:
        from strands.models.ollama import OllamaModel

        model = OllamaModel(
            host=OLLAMA_HOST,
            model_id=OLLAMA_MODEL,
        )
        print(f"[AGENT] Using Ollama model: {OLLAMA_MODEL}")

    return Agent(
        model=model,
        tools=[
            query_market_data,
            get_table_info,
            search_export_docs,
            read_export_doc,
            analyze_image,
            get_user_progress,
        ],
        system_prompt=SYSTEM_PROMPT,
    )


# Singleton agent instance
_agent = None


def get_agent() -> Agent:
    global _agent
    if _agent is None:
        _agent = create_agent()
    return _agent


def run_agent_with_context(
    user_message: str,
    conversation_history: str = "",
    user_profile: dict = None,
    image_base64: str = None,
) -> str:
    """Run the agent with full context injection."""
    global _current_user_id
    _current_user_id = user_profile.get("id") if user_profile else None

    agent = get_agent()

    parts = []

    if user_profile:
        profile_ctx = f"""User Profile: (Use this to personalize responses)
- Name: {user_profile.get('full_name', 'Unknown')}
- Company: {user_profile.get('company_name', 'Not specified')}
- Products (HS codes): {', '.join(user_profile.get('hs_codes') or ['Not specified'])}
- State: {user_profile.get('state', 'Not specified')}"""
        parts.append(profile_ctx)

    if conversation_history:
        parts.append(f"Recent conversation:\n{conversation_history}")

    image_desc = None
    if image_base64:
        image_desc = process_image(image_base64)
        parts.append(f"User uploaded an image. Image analysis:\n{image_desc}")

    parts.append(f"User message: {user_message}")

    full_prompt = "\n\n".join(parts)

    messages = [{
        "role": "user",
        "content": [{"type": "text", "text": full_prompt}],
    }]

    try:
        response = agent(messages)
        return str(response)
    except Exception as e:
        return f"I encountered an error processing your request. Please try again. (Error: {str(e)})"
