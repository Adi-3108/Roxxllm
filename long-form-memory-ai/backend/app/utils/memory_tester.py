from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from app.services.memory_service import MemoryService


class MemoryTester:
    """
    Lightweight memory system test harness.
    Intended for the /memory/test endpoint only.
    """

    def __init__(self) -> None:
        self._memory_service = MemoryService()

    async def run_full_test_suite(self, user_id: str) -> Dict[str, Any]:
        """
        Create a test memory and verify retrieval works.
        Returns a summary dict used by the API response.
        """
        results: Dict[str, Any] = {
            "started_at": datetime.utcnow().isoformat(),
            "created_memory_id": None,
            "retrieved_count": 0,
            "success": False,
        }

        # Create a basic test memory
        created = await self._memory_service.create_memory(
            user_id=user_id,
            memory_type="test",
            key="memory_test",
            value="This is a test memory",
            conversation_id=None,
            turn_number=1,
            confidence=0.5,
            importance=0.3,
            context="system_test",
        )
        results["created_memory_id"] = str(created.id)

        # Retrieve recent memories and validate presence
        memories = await self._memory_service.get_user_memories(
            user_id=user_id,
            limit=10,
            sort_by="time_created",
        )
        results["retrieved_count"] = len(memories)

        results["success"] = results["retrieved_count"] > 0
        results["summary"] = "Memory test completed" if results["success"] else "No memories retrieved"
        results["finished_at"] = datetime.utcnow().isoformat()

        return results
