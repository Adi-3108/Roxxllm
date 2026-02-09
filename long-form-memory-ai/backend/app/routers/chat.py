from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, AsyncGenerator, List
import json

from app.models.user import User
from app.models.chat import Conversation
from app.routers.auth import get_current_user_dependency
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])
chat_service = ChatService()


# ---------- Schemas ----------

class MessageCreate(BaseModel):
    content: str
    conversation_id: Optional[str] = None
    stream: bool = False


class ConversationCreate(BaseModel):
    title: Optional[str] = None


# ---------- Routes ----------

@router.post("/conversations")
async def create_conversation(
    data: ConversationCreate,
    current_user: User = Depends(get_current_user_dependency),
):
    conv = await chat_service.create_conversation(
        user_id=str(current_user.id),
        title=data.title
    )

    return {
        "id": str(conv.id),
        "title": conv.title,
        "created_at": conv.created_at.isoformat(),
        "turn_count": conv.turn_count
    }


@router.get("/conversations")
async def list_conversations(
    current_user: User = Depends(get_current_user_dependency),
):
    conversations = await Conversation.find(
        Conversation.user_id == str(current_user.id)
    ).sort("-updated_at").to_list()

    return [
        {
            "id": str(c.id),
            "title": c.title,
            "created_at": c.created_at.isoformat(),
            "updated_at": c.updated_at.isoformat() if c.updated_at else None,
            "turn_count": c.turn_count
        }
        for c in conversations
    ]


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user_dependency),
    limit: int = 100
):
    return await chat_service.get_conversation_history(
        conversation_id=conversation_id,
        user_id=str(current_user.id),
        limit=limit
    )


@router.post("/send")
async def send_message(
    data: MessageCreate,
    current_user: User = Depends(get_current_user_dependency),
):
    # Create conversation if missing
    if not data.conversation_id:
        conv = await chat_service.create_conversation(
            user_id=str(current_user.id)
        )
        data.conversation_id = str(conv.id)

    # Streaming response (SSE)
    if data.stream:
        async def event_gen() -> AsyncGenerator[str, None]:
            async for event in chat_service.process_message(
                user_id=str(current_user.id),
                conversation_id=data.conversation_id,
                content=data.content,
                stream=True
            ):
                yield f"data: {json.dumps(event)}\n\n"

            yield "data: [DONE]\n\n"

        return StreamingResponse(
            event_gen(),
            media_type="text/event-stream"
        )

    # Non-streaming response
    result = None
    async for event in chat_service.process_message(
        user_id=str(current_user.id),
        conversation_id=data.conversation_id,
        content=data.content,
        stream=False
    ):
        result = event

    return result
