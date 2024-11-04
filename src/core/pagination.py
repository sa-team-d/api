
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class PaginationParams(BaseModel):
    page: int = Field(default=0, ge=1)
    per_page: int = Field(default=19, ge=1, le=100)
    sort: Optional[str] = None
    filter: Optional[Dict[str, Any]] = None
    fields: Optional[List[str]] = None
