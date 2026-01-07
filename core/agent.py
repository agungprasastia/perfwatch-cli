"""
Base Agent - Foundation for all agents.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from enum import Enum


class AgentStatus(Enum):
    """Agent status enumeration."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentState:
    """Agent state container."""
    status: AgentStatus = AgentStatus.IDLE
    current_task: Optional[str] = None
    results: dict = field(default_factory=dict)
    errors: list = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        return {
            "status": self.status.value,
            "current_task": self.current_task,
            "results": self.results,
            "errors": self.errors,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class BaseAgent(ABC):
    """Base class for all agents."""
    
    def __init__(self, name: str):
        self.name = name
        self.state = AgentState()
    
    @abstractmethod
    async def execute(self, context: dict) -> dict:
        """Execute the agent's main task."""
        pass
    
    def start(self, task: str):
        """Mark agent as started."""
        self.state.status = AgentStatus.RUNNING
        self.state.current_task = task
        self.state.started_at = datetime.now()
    
    def complete(self, results: dict):
        """Mark agent as completed."""
        self.state.status = AgentStatus.COMPLETED
        self.state.results = results
        self.state.completed_at = datetime.now()
    
    def fail(self, error: str):
        """Mark agent as failed."""
        self.state.status = AgentStatus.FAILED
        self.state.errors.append(error)
        self.state.completed_at = datetime.now()
    
    def get_state(self) -> dict:
        """Get current state as dict."""
        return self.state.to_dict()
