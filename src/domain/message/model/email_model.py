from pydantic import BaseModel, EmailStr
from typing import Optional


class ConfirmCodeDTO(BaseModel):
    email: EmailStr
    code: str


class EmailVO(BaseModel):
    sender_id: int  # user_id
    recipient_id: int  # user_id
    subject: str
    body: str
