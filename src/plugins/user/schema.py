from datetime import datetime
from turtle import update
from typing import List, Optional
from venv import create
from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
    uid: str # Firebase UID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: EmailStr
    created_at: datetime = datetime.now()
    updated_at: Optional[datetime] = None

#class UserBase(BaseModel):
#    email: EmailStr
#    display_name: Optional[str] = Field(None, min_length=2, max_length=100)
#    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
#    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
#    phone_number: Optional[str] = None
#    profile_image: Optional[str] = None
#
#class UserCreate(UserBase):
#    password: str = Field(..., min_length=8)
#
#class UserUpdate(BaseModel):
#    display_name: Optional[str] = Field(None, min_length=2, max_length=100)
#    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
#    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
#    phone_number: Optional[str] = None
#    profile_image: Optional[str] = None
#
#class UserResponse(UserBase):
#    id: str
#    is_active: bool = True
#    is_verified: bool = False
#    permissions: List[str] = []
#    roles: List[str] = []
#    created_at: datetime
#    updated_at: Optional[datetime] = None
#
#class FirebaseAuthRequest(BaseModel):
#    id_token: str = Field(..., description="Firebase ID token")
#
#class FirebaseAuthResponse(BaseModel):
#    access_token: str
#    token_type: str = "bearer"
#    expires_in: int = Field(..., gt=0)
#    user: UserResponse
#
#class UserRole(BaseModel):
#    user_id: str
#    roles: List[str] = Field(..., min_items=1)
#
#class UserRoleUpdate(BaseModel):
#    roles: List[str] = Field(..., min_items=1)