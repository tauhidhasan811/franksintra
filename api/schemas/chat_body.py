from pydantic import BaseModel
from typing import Dict, List
import json

class ChatHistoryItem(BaseModel):
    user_query: str
    ai_response: str

class ChatWithFile(BaseModel):
    previous_chat: List[ChatHistoryItem]

    @classmethod
    def from_form_value(cls, value: str):
        data = json.loads(value)
        if isinstance(data, list):
            return cls(previous_chat=data)
        if isinstance(data, dict) and "previous_chat" not in data:
            return cls(previous_chat=[data])
        return cls.model_validate(data)


class Chatbody(BaseModel):
    previous_chat: List[ChatHistoryItem]
    user_query: str
