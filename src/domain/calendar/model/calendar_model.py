from pydantic import BaseModel
from typing import List, Optional

class CalendarEventDTO(BaseModel):
    summary: Optional[str] = "" 
    description: Optional[str] = ""
    start_time: int  # Unix Timestamp
    end_time: int    # Unix Timestamp
    user_ids: List[int] = []