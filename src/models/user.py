from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
import uuid

if TYPE_CHECKING:
    from .task import Task  # Forward reference for type checking


class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = Field(default=True)


class User(UserBase, table=True):
    """
    User model representing an application user with authentication credentials
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to tasks
    tasks: list["Task"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    """
    Schema for creating a new user
    """
    password: str


class UserUpdate(SQLModel):
    """
    Schema for updating user information
    """
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None


class UserPublic(UserBase):
    """
    Public representation of a user (excludes sensitive data)
    """
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime