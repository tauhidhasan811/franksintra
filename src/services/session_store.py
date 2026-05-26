from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class ChatSession:
    session_id: str
    image_url: str
    response: dict[str, Any]
    history: list[dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ChatSessionStore:
    _sessions: dict[str, ChatSession] = {}

    @classmethod
    def create(cls, image_url: str, response: dict[str, Any]) -> ChatSession:
        session_id = str(uuid4())
        session = ChatSession(
            session_id=session_id,
            image_url=image_url,
            response=deepcopy(response),
            history=[
                {
                    "action": "chat",
                    "response": deepcopy(response),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ],
        )
        cls._sessions[session_id] = session
        return deepcopy(session)

    @classmethod
    def get(cls, session_id: str) -> ChatSession | None:
        session = cls._sessions.get(session_id)
        if session is None:
            return None
        return deepcopy(session)

    @classmethod
    def update_response(
        cls,
        session_id: str,
        response: dict[str, Any],
        update_field_name: str,
        user_instruction: str,
    ) -> ChatSession | None:
        session = cls._sessions.get(session_id)
        if session is None:
            return None

        session.response = deepcopy(response)
        session.updated_at = datetime.now(timezone.utc).isoformat()
        session.history.append(
            {
                "action": "regenerate",
                "update_field_name": update_field_name,
                "user_instruction": user_instruction,
                "response": deepcopy(response),
                "created_at": session.updated_at,
            }
        )
        return deepcopy(session)

    @classmethod
    def delete(cls, session_id: str) -> bool:
        return cls._sessions.pop(session_id, None) is not None
