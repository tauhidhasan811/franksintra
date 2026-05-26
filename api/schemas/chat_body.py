from pydantic import BaseModel
from typing import Optional


class ChatBody(BaseModel):
    image_url: str


class RegenerateChatBody(BaseModel):
    session_id: str
    update_field_name: str
    user_instruction: Optional[str] = None
