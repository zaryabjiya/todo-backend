from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Any
from datetime import datetime
from passlib.context import CryptContext
from ...models.user import User, UserCreate, UserPublic
from ...db.session import get_session
from ...middleware.auth_middleware import create_access_token
from ...utils.exceptions import DuplicateEmailException

router = APIRouter()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


@router.post("/register", response_model=UserPublic)
def register_user(user_data: UserCreate, session: Session = Depends(get_session)) -> Any:
    """
    Register a new user account
    """
    # Check if user with this email already exists
    existing_user = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing_user:
        raise DuplicateEmailException()
    
    # Hash the password
    hashed_password = get_password_hash(user_data.password)
    
    # Create the new user
    user = User(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        hashed_password=hashed_password
    )
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return user


@router.post("/login")
def login_user(user_data: UserCreate, session: Session = Depends(get_session)) -> Any:
    """
    Authenticate a user and return a JWT token
    """
    # Find user by email
    user = session.exec(select(User).where(User.email == user_data.email)).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="Account is deactivated"
        )
    
    # Create access token
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "exp": datetime.utcnow().timestamp() + 3600  # Token expires in 1 hour
    }
    access_token = create_access_token(token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name
        }
    }


@router.post("/logout")
def logout_user() -> Any:
    """
    Invalidate the user's session (client-side token removal)
    """
    # In a stateless JWT system, the actual invalidation happens on the client
    # The server doesn't maintain session state
    return {"message": "Logged out successfully"}