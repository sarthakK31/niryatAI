import asyncio
import base64
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from app.middleware import get_current_user
from app.services.chat_persistence import (
    create_session, get_user_sessions, get_session_messages,
    add_message, auto_title_session, build_chat_context,
)
from app.services.agent import run_agent_with_context, process_image
from app.models.schemas import ChatResponse, ChatSession, ChatMessage

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.get("/sessions", response_model=list[ChatSession])
def list_sessions(user=Depends(get_current_user)):
    return get_user_sessions(user["id"])


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessage])
def list_messages(session_id: str, user=Depends(get_current_user)):
    return get_session_messages(session_id)


@router.post("/send", response_model=ChatResponse)
async def send_message(
    message: str = Form(...),
    session_id: str = Form(None),
    image: UploadFile | None = File(None),
    user=Depends(get_current_user),
):
    # Create or reuse session
    if not session_id:
        session_id = create_session(user["id"])
        auto_title_session(session_id, message)

    # Process image if provided
    image_base64 = None
    image_desc = None
    if image:
        image_bytes = await image.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    # Build conversation context from DB
    history = build_chat_context(session_id, max_messages=10)

    # Store user message
    add_message(session_id, "user", message)

    # Run agent in a thread to avoid blocking the async event loop
    response = await asyncio.to_thread(
        run_agent_with_context,
        user_message=message,
        conversation_history=history,
        user_profile=user,
        image_base64=image_base64,
    )

    # Store assistant response
    add_message(session_id, "assistant", response, image_description=image_desc)

    return ChatResponse(response=response, session_id=session_id)


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str, user=Depends(get_current_user)):
    from app.database import get_cursor
    with get_cursor(commit=True) as cur:
        cur.execute(
            "DELETE FROM chat_sessions WHERE id = %s AND user_id = %s",
            (session_id, user["id"]),
        )
    return {"status": "deleted"}
