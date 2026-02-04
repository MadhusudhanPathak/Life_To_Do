"""
Goal entity module for the Life To Do application.

This module defines the Goal data class that represents individual goals
with their properties and metadata.
"""
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class Goal:
    """
    Represents a goal with its properties and metadata.
    
    Attributes:
        name: Unique identifier for the goal
        description: Detailed description of the goal
        priority: Priority level (e.g., 'High', 'Medium', 'Low')
        due_date: Optional deadline for the goal
        dependencies: List of goal names this goal depends on
        created_at: Timestamp when the goal was created
        completed: Boolean indicating if the goal is completed
    """
    name: str
    description: str = ""
    priority: str = "Medium"
    due_date: Optional[datetime] = None
    dependencies: List[str] = None
    created_at: datetime = None
    completed: bool = False
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def __str__(self) -> str:
        return f"Goal: {self.name}\nDescription: {self.description}\nPriority: {self.priority}\nDue Date: {self.due_date}"
    
    def __repr__(self) -> str:
        return f"Goal(name='{self.name}', priority='{self.priority}', completed={self.completed})"