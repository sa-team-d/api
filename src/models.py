"""
Define the database table schema. This is the data that will be stored in the database. This tells us what the database table will look like.
"""

from pydantic import BaseModel
from typing import Optional

class Machine(BaseModel):
    id: int
    name: str
    type: str
