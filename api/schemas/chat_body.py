from pydantic import BaseModel
from typing import Optional


class ChatBody(BaseModel):
    image_url: str
    assign_location: str
    preferred_instructions: str


class RegenerateChatBody(BaseModel):
    session_id: str
    update_field_name: str
    user_instruction: Optional[str] = None
