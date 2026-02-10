
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.models.memory import Memory


class MemoryService:
    """Service layer for memory operations with conflict resolution."""

    async def create_memory(
        self,
        user_id: str,
        memory_type: str,
        key: str,
        value: str,
        conversation_id: Optional[str],
        turn_number: int,
        confidence: float = 0.5,
        importance: float = 0.5,
        context: str = ""
    ) -> Memory:
        """
        Create a new memory for a user.
        AUTOMATICALLY DEACTIVATES old memories with the same key to handle preference updates.
        """
        
        print(f"\n🔍 Checking for existing memory: {memory_type}/{key}")
        
        # Find and deactivate any existing memory with the same key and type
        existing_memories = await Memory.find(
            Memory.user_id == user_id,
            Memory.memory_type == memory_type,
            Memory.key == key,
            Memory.is_active == True
        ).to_list()
        
        if existing_memories:
            print(f"🔄 Found {len(existing_memories)} existing memory(ies) for key '{key}'")
            for old_mem in existing_memories:
                print(f"   Deactivating: {old_mem.value} (Turn {old_mem.source_turn})")
                old_mem.is_active = False
                old_mem.updated_at = datetime.utcnow()
                await old_mem.save()
            print(f"✅ Deactivated old memories")
        
        # Create new memory
        memory = Memory(
            user_id=user_id,
            memory_type=memory_type,
            key=key,
            value=value,
            context=context,
            source_conversation_id=conversation_id,
            source_turn=turn_number,
            confidence=confidence,
            importance_score=importance,
            is_active=True,
            created_at=datetime.utcnow()
        )

        await memory.insert()
        
        print(f"✅ Created new memory: [{memory_type}] {key} = {value} (Turn {turn_number})")
        
        return memory

    async def get_user_memories(
        self,
        user_id: str,
        memory_type: Optional[str] = None,
        limit: int = 100,
        sort_by: str = "recency",  # "recency", "importance", or "time_created"
        hours_ago: Optional[int] = None  # Filter memories from last N hours
    ) -> List[Memory]:
        """
        Get all active memories for a user with enhanced sorting options.
        Enhanced to consider both turn numbers and creation timestamps.
        """
        from datetime import datetime, timedelta
        
        # Build base query
        query = Memory.find(
            Memory.user_id == user_id,
            Memory.is_active == True
        )

        if memory_type:
            query = query.find(Memory.memory_type == memory_type)
        
        # Add time-based filtering if specified
        if hours_ago is not None:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_ago)
            query = query.find(Memory.created_at >= cutoff_time)

        # Enhanced sorting logic
        if sort_by == "time_created":
            # Sort by actual creation time (most recent first)
            memories = await query.sort("-created_at").limit(limit).to_list()
        elif sort_by == "recency":
            # Hybrid sort: prioritize by creation time, then by turn number
            # This ensures memories from recent conversations are included
            memories = await query.to_list()  # Get all, then sort in Python for hybrid logic
            
            # Sort with hybrid scoring
            def hybrid_sort_key(mem):
                now = datetime.utcnow()
                hours_old = (now - mem.created_at).total_seconds() / 3600
                
                # Recent memories (last 6 hours) get highest priority
                if hours_old <= 6:
                    time_score = 1000 - (hours_old * 100)  # Higher score for newer
                else:
                    time_score = 400 - min(hours_old * 2, 400)  # Gradual decay
                
                # Add turn-based score (lower penalty for older turns)
                turn_score = max(0, 100 - mem.source_turn)
                
                return time_score + turn_score
            
            memories.sort(key=hybrid_sort_key, reverse=True)
            memories = memories[:limit]
        elif sort_by == "importance":
            memories = await query.sort("-importance_score").limit(limit).to_list()
        else:
            # Default to time_created for reliability
            memories = await query.sort("-created_at").limit(limit).to_list()
            
        return memories

    async def search_memories(
        self,
        user_id: str,
        query_text: str,
        current_turn: int = 0,
        top_k: int = 5,
        memory_types: Optional[List[str]] = None
    ) -> List[Memory]:
        """
        Enhanced memory search with time-aware retrieval.
        Considers both creation time and turn numbers for comprehensive memory access.
        """
        from datetime import datetime, timedelta
        
        query = Memory.find(
            Memory.user_id == user_id,
            Memory.is_active == True
        )
        
        if memory_types:
            query = query.find({"memory_type": {"$in": memory_types}})
        
        # Get more memories to ensure we don't miss important ones
        memories = await query.sort("-created_at").limit(top_k * 5).to_list()
        
        # Enhanced relevance scoring with time-aware weighting
        scored_memories = []
        query_lower = query_text.lower()
        now = datetime.utcnow()
        
        for mem in memories:
            score = 0.0
            
            # Check if query keywords appear in memory value or key
            mem_text = f"{mem.key} {mem.value}".lower()
            query_words = query_lower.split()
            
            for word in query_words:
                if len(word) > 2 and word in mem_text:
                    score += 1.0
            
            # TIME-AWARE RECENCY BOOST (NEW)
            # Calculate hours since creation
            hours_ago = (now - mem.created_at).total_seconds() / 3600
            
            # Strong boost for very recent memories (last 4 hours)
            if hours_ago <= 4:
                time_boost = 3.0 * (1 - hours_ago / 4)  # Linear decay from 3.0 to 0
            # Moderate boost for memories from 4-24 hours ago
            elif hours_ago <= 24:
                time_boost = 1.0 * (1 - (hours_ago - 4) / 20)  # Linear decay from 1.0 to 0
            # Small boost for memories from 1-7 days ago
            elif hours_ago <= 168:  # 7 days
                time_boost = 0.5 * (1 - (hours_ago - 24) / 144)  # Linear decay from 0.5 to 0
            else:
                time_boost = 0.0
            
            score += time_boost
            
            # Turn-based recency boost (for within same conversation)
            if current_turn > 0:
                turns_ago = current_turn - mem.source_turn
                if turns_ago >= 0:  # Only boost for memories from earlier or current turn
                    turn_boost = max(0, 2.0 - (turns_ago / 10))
                    score += turn_boost
            
            # Importance boost
            score += mem.importance_score * 2
            
            # Access frequency boost (frequently accessed memories are important)
            if mem.access_count > 0:
                access_boost = min(1.0, mem.access_count * 0.1)
                score += access_boost
            
            scored_memories.append((score, mem))
        
        # Sort by score and return top_k
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        return [mem for score, mem in scored_memories[:top_k]]
    
    async def refresh_memory_access(
        self,
        memory_id: str,
        user_id: str,
        current_turn: int
    ) -> bool:
        """Update memory access statistics."""
        
        memory = await Memory.get(memory_id)
        if not memory or memory.user_id != user_id:
            return False
        
        memory.access_count += 1
        memory.last_accessed_turn = current_turn
        memory.updated_at = datetime.utcnow()
        await memory.save()
        
        return True

    async def update_memory(
        self,
        memory_id: str,
        user_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Memory]:
        """Update an existing memory."""

        memory = await Memory.get(memory_id)
        if not memory or memory.user_id != user_id:
            return None

        allowed_fields = {
            "value",
            "context",
            "confidence",
            "importance_score",
            "is_active",
            "expires_at"
        }

        for field, value in updates.items():
            if field in allowed_fields:
                setattr(memory, field, value)

        memory.updated_at = datetime.utcnow()
        await memory.save()

        return memory

    async def delete_memory(
        self,
        memory_id: str,
        user_id: str
    ) -> bool:
        """Soft delete a memory (mark inactive)."""

        memory = await Memory.get(memory_id)
        if not memory or memory.user_id != user_id:
            return False

        memory.is_active = False
        memory.updated_at = datetime.utcnow()
        await memory.save()

        return True
    
    async def delete_conversation_memories(
        self,
        conversation_id: str,
        user_id: str
    ) -> int:
        """
        Delete (deactivate) ALL memories associated with a specific conversation.
        Returns the count of memories deleted.
        """
        
        memories = await Memory.find(
            Memory.user_id == user_id,
            Memory.source_conversation_id == conversation_id,
            Memory.is_active == True
        ).to_list()
        
        count = 0
        for mem in memories:
            mem.is_active = False
            mem.updated_at = datetime.utcnow()
            await mem.save()
            count += 1
            print(f"   Deactivated memory: [{mem.memory_type}] {mem.key}: {mem.value}")
        
        return count

    async def get_memory_stats(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """Get memory statistics for a user."""

        memories = await Memory.find(
            Memory.user_id == user_id,
            Memory.is_active == True
        ).to_list()

        stats = {
            "total_memories": len(memories),
            "by_type": {},
            "high_importance_memories": 0
        }

        for mem in memories:
            stats["by_type"].setdefault(mem.memory_type, 0)
            stats["by_type"][mem.memory_type] += 1

            if mem.importance_score >= 0.8:
                stats["high_importance_memories"] += 1

        return stats

    async def refresh_memory_access(
        self,
        memory_id: str,
        user_id: str,
        current_turn: int
    ) -> bool:
        """Update last accessed metadata for a memory."""

        memory = await Memory.get(memory_id)
        if not memory or memory.user_id != user_id:
            return False

        memory.access_count += 1
        memory.last_accessed_turn = current_turn
        memory.updated_at = datetime.utcnow()
        await memory.save()

        return True