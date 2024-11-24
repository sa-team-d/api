from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List


class User(BaseModel):
    uid: str  = Field(...) # The user's ID firebase
    email: EmailStr = Field(...) # The user's email
    site : Optional[int] = None # if ffm, else none
    name: str = Field(...)
    phone_number: Optional[str] = None

class UserWithToken(User):
    id_token: str = Field(...)


class UserLogin(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

class UserResponse(BaseModel):
    success: bool
    data: Optional[UserWithToken | User | List[User]] = None
    message: Optional[str] = None

