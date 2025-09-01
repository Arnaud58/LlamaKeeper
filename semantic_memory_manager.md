# Semantic Memory Management System for LlamaKeeper

## Overview
A sophisticated memory management system that supports semantic storage, retrieval, and contextual understanding of character memories.

## Implementation

```python
from typing import Dict, List, Any, Optional, Union
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum, auto
from dataclasses import dataclass, field
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class MemoryType(Enum):
    """
    Categorization of memory types
    Provides a structured approach to memory classification
    """
    PERSONAL_EXPERIENCE = auto()
    DIALOGUE = auto()
    EMOTIONAL_STATE = auto()
    GOAL = auto()
    LEARNED_KNOWLEDGE = auto()
    RELATIONSHIP = auto()

@dataclass
class SemanticMemory:
    """
    Advanced memory representation with semantic encoding
    """
    id: UUID = field(default_factory=uuid4)
    content: str = field(default_factory=str)
    memory_type: MemoryType = MemoryType.PERSONAL_EXPERIENCE
    timestamp: datetime = field(default_factory=datetime.now)
    importance: float = 0.5
    context: Dict[str, Any] = field(default_factory=dict)
    semantic_vector: Optional[np.ndarray] = None
    associated_entities: List[str] = field(default_factory=list)

class SemanticMemoryManager:
    """
    Advanced memory management system with semantic capabilities
    Supports complex memory storage, retrieval, and reasoning
    """
    
    def __init__(
        self, 
        embedding_model: Optional[Any] = None,
        max_memories: int = 1000,
        long_term_threshold: float = 0.7
    ):
        """
        Initialize semantic memory manager
        
        Args:
            embedding_model (Any, optional): Semantic embedding model
            max_memories (int): Maximum number of memories to store
            long_term_threshold (float): Importance threshold for long-term memory
        """
        # Memory storage
        self._memories: Dict[UUID, SemanticMemory] = {}
        self._long_term_memories: Dict[UUID, SemanticMemory] = {}
        
        # Embedding and semantic processing
        self._embedding_model = embedding_model or self._default_embedding
        self._max_memories = max_memories
        self._long_term_threshold = long_term_threshold
    
    def _default_embedding(self, text: str) -> np.ndarray:
        """
        Default simple embedding method
        Can be replaced with more advanced embedding models
        
        Args:
            text (str): Text to embed
        
        Returns:
            np.ndarray: Semantic vector representation
        """
        # Simple word-level embedding (placeholder)
        words = text.lower().split()
        # Create a simple vector based on word presence
        return np.array([
            len([w for w in words if c in w]) 
            for c in 'abcdefghijklmnopqrstuvwxyz'
        ], dtype=float)
    
    async def store_memory(
        self, 
        content: str, 
        memory_type: MemoryType = MemoryType.PERSONAL_EXPERIENCE,
        importance: float = 0.5,
        context: Optional[Dict[str, Any]] = None,
        associated_entities: Optional[List[str]] = None
    ) -> SemanticMemory:
        """
        Store a new memory with semantic encoding
        
        Args:
            content (str): Memory content
            memory_type (MemoryType): Type of memory
            importance (float): Memory importance score
            context (Dict, optional): Additional context
            associated_entities (List[str], optional): Related entities
        
        Returns:
            SemanticMemory: Stored memory
        """
        # Generate semantic vector
        semantic_vector = self._embedding_model(content)
        
        # Create memory object
        memory = SemanticMemory(
            content=content,
            memory_type=memory_type,
            importance=max(0, min(1, importance)),
            context=context or {},
            semantic_vector=semantic_vector,
            associated_entities=associated_entities or []
        )
        
        # Store memory
        self._memories[memory.id] = memory
        
        # Manage memory capacity
        await self._manage_memory_capacity()
        
        # Check for long-term memory
        if memory.importance >= self._long_term_threshold:
            self._long_term_memories[memory.id] = memory
        
        return memory
    
    async def _manage_memory_capacity(self):
        """
        Manage memory storage capacity
        Remove least important memories when capacity is exceeded
        """
        if len(self._memories) > self._max_memories:
            # Sort memories by importance and timestamp
            sorted_memories = sorted(
                self._memories.values(),
                key=lambda m: (m.importance, m.timestamp),
                reverse=False
            )
            
            # Remove least important memories
            memories_to_remove = sorted_memories[:len(self._memories) - self._max_memories]
            
            for memory in memories_to_remove:
                # Only remove if not a long-term memory
                if memory.id not in self._long_term_memories:
                    del self._memories[memory.id]
    
    async def retrieve_memories(
        self, 
        query: str, 
        top_k: int = 5,
        memory_type: Optional[MemoryType] = None,
        min_importance: float = 0.0
    ) -> List[SemanticMemory]:
        """
        Retrieve memories using semantic similarity
        
        Args:
            query (str): Search query
            top_k (int): Number of memories to retrieve
            memory_type (MemoryType, optional): Filter by memory type
            min_importance (float): Minimum importance threshold
        
        Returns:
            List[SemanticMemory]: Most relevant memories
        """
        # Generate query embedding
        query_vector = self._embedding_model(query)
        
        # Filter memories
        candidate_memories = [
            memory for memory in self._memories.values()
            if (memory_type is None or memory.memory_type == memory_type) and
               memory.importance >= min_importance
        ]
        
        # Calculate semantic similarity
        similarities = [
            cosine_similarity(
                query_vector.reshape(1, -1), 
                memory.semantic_vector.reshape(1, -1)
            )[0][0]
            for memory in candidate_memories
        ]
        
        # Sort memories by similarity and importance
        scored_memories = [
            (memory, similarity) 
            for memory, similarity in zip(candidate_memories, similarities)
        ]
        
        sorted_memories = sorted(
            scored_memories, 
            key=lambda x: (x[1], x[0].importance), 
            reverse=True
        )
        
        return [memory for memory, _ in sorted_memories[:top_k]]
    
    async def update_memory_importance(
        self, 
        memory_id: UUID, 
        new_importance: float
    ):
        """
        Update the importance of a specific memory
        
        Args:
            memory_id (UUID): ID of the memory to update
            new_importance (float): New importance value
        """
        if memory_id in self._memories:
            memory = self._memories[memory_id]
            old_importance = memory.importance
            
            # Update importance
            memory.importance = max(0, min(1, new_importance))
            
            # Manage long-term memory status
            if (old_importance < self._long_term_threshold and 
                memory.importance >= self._long_term_threshold):
                self._long_term_memories[memory_id] = memory
            elif (old_importance >= self._long_term_threshold and 
                  memory.importance < self._long_term_threshold):
                self._long_term_memories.pop(memory_id, None)
    
    def get_memory_summary(
        self, 
        character_id: Optional[UUID] = None,
        memory_type: Optional[MemoryType] = None
    ) -> Dict[str, Any]:
        """
        Generate a summary of stored memories
        
        Args:
            character_id (UUID, optional): Filter by character
            memory_type (MemoryType, optional): Filter by memory type
        
        Returns:
            Dict: Memory summary statistics
        """
        # Filter memories
        filtered_memories = [
            memory for memory in self._memories.values()
            if (memory_type is None or memory.memory_type == memory_type)
        ]
        
        # Compute summary statistics
        summary = {
            'total_memories': len(filtered_memories),
            'long_term_memories': len(self._long_term_memories),
            'memory_type_distribution': {},
            'importance_distribution': {
                'low': 0,
                'medium': 0,
                'high': 0
            }
        }
        
        # Compute memory type distribution
        for memory in filtered_memories:
            type_count = summary['memory_type_distribution'].get(
                memory.memory_type.name, 0
            )
            summary['memory_type_distribution'][memory.memory_type.name] = type_count + 1
            
            # Compute importance distribution
            if memory.importance < 0.3:
                summary['importance_distribution']['low'] += 1
            elif memory.importance < 0.7:
                summary['importance_distribution']['medium'] += 1
            else:
                summary['importance_distribution']['high'] += 1
        
        return summary

# Example Usage
async def demonstrate_memory_management():
    """
    Demonstrate advanced memory management capabilities
    """
    # Initialize memory manager
    memory_manager = SemanticMemoryManager()
    
    # Store memories
    adventure_memory = await memory_manager.store_memory(
        content="Explored an ancient ruins and discovered a hidden treasure",
        memory_type=MemoryType.PERSONAL_EXPERIENCE,
        importance=0.8,
        context={
            'location': 'Ancient Ruins',
            'emotion': 'Excitement'
        },
        associated_entities=['treasure', 'adventure']
    )
    
    dialogue_memory = await memory_manager.store_memory(
        content="Negotiated a peace treaty with rival kingdom",
        memory_type=MemoryType.DIALOGUE,
        importance=0.9,
        context={
            'participants': ['Diplomat', 'Kingdom Representative'],
            'outcome': 'Successful negotiation'
        }
    )
    
    # Retrieve memories
    query_memories = await memory_manager.retrieve_memories(
        query="exciting adventure",
        top_k=3,
        memory_type=MemoryType.PERSONAL_EXPERIENCE
    )
    
    # Get memory summary
    summary = memory_manager.get_memory_summary()
    
    return {
        'stored_memories': [adventure_memory, dialogue_memory],
        'retrieved_memories': query_memories,
        'memory_summary': summary
    }
```

## Key Features

1. **Semantic Memory Storage**
   - Contextual memory representation
   - Semantic vector encoding
   - Importance-based memory management

2. **Advanced Retrieval**
   - Semantic similarity search
   - Flexible filtering
   - Relevance-based ranking

3. **Memory Type Classification**
   - Structured memory categorization
   - Type-based filtering and analysis

4. **Capacity Management**
   - Automatic memory pruning
   - Long-term memory preservation
   - Importance-based storage

## Memory Types

- **Personal Experience**: Individual events and memories
- **Dialogue**: Conversations and interactions
- **Emotional State**: Mood and emotional experiences
- **Goal**: Objectives and aspirations
- **Learned Knowledge**: Acquired information
- **Relationship**: Interpersonal connections

## Benefits

- **Flexibility**: Adaptable memory management
- **Intelligence**: Semantic understanding
- **Efficiency**: Intelligent memory storage
- **Depth**: Rich contextual tracking

## Recommended Next Steps

1. Implement more advanced embedding models
2. Develop machine learning-based memory relevance scoring
3. Create memory compression techniques
4. Add distributed memory storage support