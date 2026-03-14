from fastapi import HTTPException, status
from typing import Optional


class TodoException(HTTPException):
    """Base exception class for todo application"""
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class UserNotFoundException(TodoException):
    """Raised when a user is not found"""
    def __init__(self, user_id: str):
        super().__init__(
            detail=f"User with id {user_id} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


class TaskNotFoundException(TodoException):
    """Raised when a task is not found"""
    def __init__(self, task_id: str):
        super().__init__(
            detail=f"Task with id {task_id} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


class UnauthorizedAccessException(TodoException):
    """Raised when a user tries to access a resource they don't own"""
    def __init__(self):
        super().__init__(
            detail="You are not authorized to access this resource",
            status_code=status.HTTP_403_FORBIDDEN
        )


class DuplicateEmailException(TodoException):
    """Raised when trying to create a user with an existing email"""
    def __init__(self):
        super().__init__(
            detail="A user with this email already exists",
            status_code=status.HTTP_409_CONFLICT
        )


class ValidationError(TodoException):
    """Raised when validation fails"""
    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )