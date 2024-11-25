from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

class User(BaseModel):
    uid: str = Field(
        ...,
        description="Firebase user ID - must be a string and is required"
    )
    email: EmailStr = Field(
        ..., 
        description="must be a valid email string and is required"
    )
    site: Optional[int] = Field(
        None,
        description="must be an integer or null"
    )
    first_name: str = Field(
        ...,
        description="must be a string and is required"
    )
    last_name: str = Field(
        ...,
        description="must be a string and is required"
    )
    phone_number: str = Field(
        ...,
        description="must be a string and is required"
    )

class UserWithToken(User):
    id_token: str = Field(..., description="Authentication token")

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")

class UserResponse(BaseModel):
    success: bool
    data: Optional[UserWithToken | User | List[User]] = Field(
        None,
        description="Response data containing user information"
    )
    message: Optional[str] = Field(
        None,
        description="Response message"
    )