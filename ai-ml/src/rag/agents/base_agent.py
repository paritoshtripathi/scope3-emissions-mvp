"""
Base Agent class for RAG system
"""
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.memory: List[Dict[str, Any]] = []
        self.state: Dict[str, Any] = {}

    @abstractmethod
    async def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute thinking step with given context
        
        Args:
            context: Current context including query and retrieved documents
            
        Returns:
            Updated context with agent's thoughts
        """
        pass

    @abstractmethod
    async def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute action based on thoughts
        
        Args:
            context: Current context including thoughts
            
        Returns:
            Action results
        """
        pass

    def update_memory(self, observation: Dict[str, Any]) -> None:
        """Update agent's memory with new observation"""
        self.memory.append(observation)

    def get_memory(self, k: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get last k memories or all if k is None"""
        if k is None:
            return self.memory
        return self.memory[-k:]

    def clear_memory(self) -> None:
        """Clear agent's memory"""
        self.memory = []

    def update_state(self, updates: Dict[str, Any]) -> None:
        """Update agent's state"""
        self.state.update(updates)

    def get_state(self) -> Dict[str, Any]:
        """Get current state"""
        return self.state.copy()