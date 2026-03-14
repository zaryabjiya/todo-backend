from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
import uuid

if TYPE_CHECKING:
    from .user import User  # Forward reference for type checking


class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    due_date: Optional[datetime] = None
    priority: str = Field(default="medium", regex="^(low|medium|high)$")  # Using regex for enum-like behavior


class Task(TaskBase, table=True):
    """
    Task model representing a todo item owned by a user
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to user
    user: "User" = Relationship(back_populates="tasks")


class TaskCreate(TaskBase):
    """
    Schema for creating a new task
    """
    title: str = Field(min_length=1, max_length=200)


class TaskUpdate(SQLModel):
    """
    Schema for updating a task
    """
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = Field(default=None, regex="^(low|medium|high)$")


class TaskPublic(TaskBase):
    """
    Public representation of a task
    """
    id: uuid.UUID
    user_id: uuid.UUID
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime