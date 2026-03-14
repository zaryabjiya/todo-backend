from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, and_, func
from typing import Any, List
from uuid import UUID
from datetime import datetime

from ...models.task import Task, TaskCreate, TaskUpdate, TaskPublic
from ...models.user import User
from ...db.session import get_session
from ...middleware.auth_middleware import get_current_user
from ...utils.exceptions import TaskNotFoundException, UnauthorizedAccessException

router = APIRouter()


@router.get("/", response_model=List[TaskPublic])
def get_user_tasks(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    status: str = Query(None, regex="^(all|pending|completed)$"),
) -> Any:
    """
    Retrieve all tasks for the current user
    """
    # Build the query with user filtering
    query = select(Task).where(Task.user_id == current_user.id)

    # Apply status filter if specified
    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)

    # Apply pagination
    query = query.offset(skip).limit(limit).order_by(Task.created_at.desc())

    tasks = session.exec(query).all()
    return tasks


@router.post("/", response_model=TaskPublic)
def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Any:
    """
    Create a new task for the current user
    """
    # Create task with the current user as owner
    task = Task.from_orm(task_data)
    task.user_id = current_user.id

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.get("/{task_id}", response_model=TaskPublic)
def get_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Any:
    """
    Retrieve a specific task for the current user
    """
    task = session.get(Task, task_id)

    if not task:
        raise TaskNotFoundException(str(task_id))

    # Verify that the task belongs to the current user
    if task.user_id != current_user.id:
        raise UnauthorizedAccessException()

    return task


@router.put("/{task_id}", response_model=TaskPublic)
def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Any:
    """
    Update an existing task for the current user
    """
    task = session.get(Task, task_id)

    if not task:
        raise TaskNotFoundException(str(task_id))

    # Verify that the task belongs to the current user
    if task.user_id != current_user.id:
        raise UnauthorizedAccessException()

    # Update task fields
    update_data = task_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    # Update the updated_at timestamp
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.patch("/{task_id}/complete")
def toggle_task_completion(
    task_id: UUID,
    completed: bool,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Any:
    """
    Mark a task as complete or incomplete
    """
    task = session.get(Task, task_id)

    if not task:
        raise TaskNotFoundException(str(task_id))

    # Verify that the task belongs to the current user
    if task.user_id != current_user.id:
        raise UnauthorizedAccessException()

    # Update completion status
    task.completed = completed
    if completed:
        task.completed_at = datetime.utcnow()
    else:
        task.completed_at = None

    # Update the updated_at timestamp
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.delete("/{task_id}")
def delete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Any:
    """
    Delete a specific task for the current user
    """
    task = session.get(Task, task_id)

    if not task:
        raise TaskNotFoundException(str(task_id))

    # Verify that the task belongs to the current user
    if task.user_id != current_user.id:
        raise UnauthorizedAccessException()

    session.delete(task)
    session.commit()

    return {"message": "Task deleted successfully"}