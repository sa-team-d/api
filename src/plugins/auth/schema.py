from typing import List
from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId
from typing import Optional
from datetime import datetime


class Auth(BaseModel):
    uid: str
    email: str
    role: str
