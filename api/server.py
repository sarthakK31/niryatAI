from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from ai_client.client.chat_agent import chat
import base64

app = FastAPI()

class ChatResponse(BaseModel):
    response: str


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    user_id: str = Form(...),
    message: str = Form(...),
    image: UploadFile | None = File(None)
):

    image_base64: str | None = None

    if image:
        image_bytes: bytes = await image.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    response = chat(
        user_id=user_id,
        message=message,
        image=image_base64,
        media_type=image.content_type if image else None
    )

    return ChatResponse(response=response)