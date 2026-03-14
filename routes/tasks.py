from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select as async_select
from typing import List, Optional
from datetime import datetime, timezone
import logging

from models.task import Task, TaskCreate as TaskCreateModel, TaskRead
from models.user import User
from db.session import get_async_db
from routes.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


def normalize_datetime(dt: Optional[datetime]) -> Optional[datetime]:
    """
    Convert timezone-aware datetime to timezone-naive UTC datetime.
    This fixes the asyncpg error with timezone-aware datetimes.
    """
    if dt is None:
        return None
    # If datetime is timezone-aware, convert to UTC and remove tzinfo
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


class TaskCreateRequest(TaskCreateModel):
    """Request model for creating a task - user_id will be set from auth"""
    pass


class TaskUpdateRequest(SQLModel):
    """Request model for updating a task"""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None


@router.get("/", response_model=List[TaskRead])
async def get_tasks(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all tasks for the current user
    """
    result = await db.execute(
        async_select(Task)
        .where(Task.user_id == current_user.id)
        .order_by(Task.created_at.desc())
    )
    tasks = result.scalars().all()
    return list(tasks)


@router.post("/", response_model=TaskRead)
async def create_task(
    task_data: TaskCreateRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new task for the current user
    """
    # Normalize due_date to timezone-naive UTC
    due_date = normalize_datetime(task_data.due_date)
    
    # Create task with user_id from authenticated user
    task = Task(
        title=task_data.title,
        description=task_data.description,
        completed=task_data.completed if task_data.completed is not None else False,
        due_date=due_date,
        user_id=current_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(task)
    await db.commit()
    await db.refresh(task)

    return task


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a specific task for the current user
    """
    result = await db.execute(
        async_select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    task_data: TaskUpdateRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing task for the current user
    """
    result = await db.execute(
        async_select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update task fields
    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "due_date":
            # Normalize datetime to timezone-naive UTC
            value = normalize_datetime(value)
        setattr(task, field, value)

    # Update the updated_at timestamp
    task.updated_at = datetime.utcnow()

    db.add(task)
    await db.commit()
    await db.refresh(task)

    return task


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a specific task for the current user
    """
    result = await db.execute(
        async_select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await db.delete(task)
    await db.commit()

    return {"message": "Task deleted successfully"}


@router.patch("/{task_id}/complete", response_model=TaskRead)
async def toggle_task_completion(
    task_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """
    Toggle the completion status of a task
    """
    result = await db.execute(
        async_select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Toggle completion status
    task.completed = not task.completed
    task.completed_at = datetime.utcnow() if task.completed else None
    task.updated_at = datetime.utcnow()

    db.add(task)
    await db.commit()
    await db.refresh(task)

    return task
