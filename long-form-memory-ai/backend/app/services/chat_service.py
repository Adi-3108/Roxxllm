from typing import List, Dict, Any, AsyncGenerator
from fastapi import HTTPException
from app.models.chat import Conversation, Message
from app.services.llm_service import LLMService


class ChatService:
    def __init__(self):
        self.llm_service = LLMService()

    async def create_conversation(
        self,
        user_id: str,
        title: str = None
    ) -> Conversation:
        conv = Conversation(
            user_id=user_id,
            title=title or "New Conversation"
        )
        await conv.insert()
        return conv

    async def get_conversation_history(
        self,
        conversation_id: str,
        user_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:

        conv = await Conversation.get(conversation_id)
        if not conv or conv.user_id != user_id:
            raise HTTPException(status_code=404, detail="Conversation not found")

        messages = (
            await Message.find(Message.conversation_id == conversation_id)
            .sort("+turn_number")
            .limit(limit)
            .to_list()
        )

        return [
            {
                "id": str(m.id),
                "role": m.role,
                "content": m.content,
                "turn_number": m.turn_number,
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ]

    async def process_message(
        self,
        user_id: str,
        conversation_id: str,
        content: str,
        stream: bool = False
    ) -> AsyncGenerator[Dict[str, Any], None]:

        print("\n===== CHAT INPUT =====")
        print("User:", user_id)
        print("Conversation:", conversation_id)
        print("Message:", content)
        print("Stream:", stream)
        print("======================\n")

        conv = await Conversation.get(conversation_id)
        if not conv or conv.user_id != user_id:
            raise HTTPException(status_code=404, detail="Conversation not found")

        conv.turn_count += 1
        await conv.save()

        # Save user message
        user_msg = Message(
            conversation_id=conversation_id,
            turn_number=conv.turn_count,
            role="user",
            content=content
        )
        await user_msg.insert()

        # Build history
        history = await Message.find(
            Message.conversation_id == conversation_id
        ).sort("+turn_number").to_list()

        messages = [
            {"role": m.role, "content": m.content}
            for m in history
        ]

        print("\n===== CONTEXT TO LLM =====")
        for m in messages:
            print(m)
        print("=========================\n")

        full_response = ""

        async for event in self.llm_service.generate_response(
            messages=messages,
            stream=stream
        ):
            print("LLM EVENT:", event)

            if event["type"] in ("token", "final"):
                chunk = event.get("content", "")
                full_response += chunk

                if stream:
                    yield {
                        "type": "chunk",
                        "content": chunk
                    }

            elif event["type"] == "error":
                yield event
                return

        print("\n===== FINAL RESPONSE =====")
        print(full_response)
        print("==========================\n")

        assistant_msg = Message(
            conversation_id=conversation_id,
            turn_number=conv.turn_count,
            role="assistant",
            content=full_response
        )
        await assistant_msg.insert()

        yield {
            "type": "complete",
            "message": {
                "id": str(assistant_msg.id),
                "content": full_response,
                "turn_number": conv.turn_count,
                "created_at": assistant_msg.created_at.isoformat(),
            }
        }