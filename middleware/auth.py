from fastapi import HTTPException, status, Depends, Header
from typing import Dict, Optional
import jwt
import os
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Get the auth secret from environment
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")


class TokenData(BaseModel):
    user_id: str
    email: Optional[str] = None


def verify_jwt_token(token: str) -> TokenData:
    """
    Verify JWT token and return user information
    """
    try:
        # Decode the JWT token using the shared secret
        payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=["HS256"])
        
        # Extract user information from the token
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
        token_data = TokenData(user_id=user_id, email=email)
        return token_data
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


def get_current_user(authorization: str = Header(...)) -> TokenData:
    """
    Dependency to get current user from JWT token in Authorization header
    Expected format: "Bearer <token>"
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing or malformed"
        )
    
    # Extract the token from the Authorization header
    token = authorization.split(" ")[1]
    
    # Verify the token and get user information
    token_data = verify_jwt_token(token)
    
    return token_data