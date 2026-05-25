import asyncio
import base64
import binascii
import json
import uuid
from urllib.parse import quote

from fastapi import APIRouter, File, Form, Header, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import Response

from src.services.voice_agent import QuoteFollowUpVoiceAgent, TemporaryVoiceMemory


router = APIRouter(prefix="/api/voice", tags=["Voice Agent"])
twilio_stream_router = APIRouter(tags=["Voice Agent"])

voice_memory = TemporaryVoiceMemory()
voice_agent: QuoteFollowUpVoiceAgent | None = None
AUDIO_FLUSH_SECONDS = 0.8
TWILIO_MEDIA_CHUNK_BYTES = 160


def _get_voice_agent() -> QuoteFollowUpVoiceAgent:
    global voice_agent
    if voice_agent is None:
        voice_agent = QuoteFollowUpVoiceAgent()
    return voice_agent


def _parse_quote_data(raw_quote_data: str):
    if not raw_quote_data:
        return {}
    try:
        return json.loads(raw_quote_data)
    except json.JSONDecodeError:
        return raw_quote_data


def _get_start_value(message: dict, key: str) -> str:
    start = message.get("start") or {}
    return str(start.get(key) or message.get(key) or "")


def _get_start_quote_data(message: dict) -> str:
    start = message.get("start") or {}
    custom_parameters = start.get("customParameters") or {}
    return str(custom_parameters.get("quote_data") or custom_parameters.get("quoteData") or "")


@router.post("/quote-follow-up")
async def quote_follow_up_voice(
    quote_data: str = Form(...),
    audio: UploadFile = File(...),
    session_id: str | None = Form(None),
    x_voice_session_id: str | None = Header(default=None),
):
    """
    Receives a customer's voice message for an abandoned quote follow-up,
    stores recent turns temporarily by session id, and returns an MP3 voice response.
    """
    try:
        active_session_id = session_id or x_voice_session_id or str(uuid.uuid4())
        audio_bytes = await audio.read()

        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Audio file is required.")

        previous_chat = voice_memory.get_history(active_session_id)
        response_audio, transcript, answer_text = await _get_voice_agent().handle_voice_follow_up(
            audio_bytes=audio_bytes,
            filename=audio.filename or "voice-input.webm",
            content_type=audio.content_type or "application/octet-stream",
            quote_data=_parse_quote_data(quote_data),
            previous_chat=previous_chat,
        )

        voice_memory.append(
            session_id=active_session_id,
            user_query=transcript,
            ai_response=answer_text,
        )

        return Response(
            content=response_audio,
            media_type="audio/mpeg",
            headers={
                "X-Voice-Session-Id": active_session_id,
                "X-Voice-Transcript": quote(transcript[:800]),
                "X-Voice-Text": quote(answer_text[:1200]),
            },
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@twilio_stream_router.websocket("/api/v1/call/ai-stream")
@router.websocket("/twilio-stream")
async def quote_follow_up_twilio_stream(
    websocket: WebSocket,
    quote_data: str = "",
    session_id: str | None = None,
):
    """
    Receives Twilio Media Streams audio directly over WebSocket and sends
    Twilio-compatible audio responses back on the same socket.
    """
    await websocket.accept()

    stream_sid = ""
    call_sid = ""
    active_session_id = session_id or str(uuid.uuid4())
    active_quote_data = quote_data
    audio_buffer = bytearray()
    flush_task: asyncio.Task | None = None
    flush_lock = asyncio.Lock()

    async def send_audio_to_twilio(audio_payload: str) -> None:
        if not stream_sid or not audio_payload:
            return

        try:
            response_audio = base64.b64decode(audio_payload)
        except (binascii.Error, ValueError):
            response_audio = b""

        chunks = [
            response_audio[index : index + TWILIO_MEDIA_CHUNK_BYTES]
            for index in range(0, len(response_audio), TWILIO_MEDIA_CHUNK_BYTES)
        ] or [b""]

        for chunk in chunks:
            payload = base64.b64encode(chunk).decode("ascii") if chunk else audio_payload
            await websocket.send_json({
                "event": "media",
                "streamSid": stream_sid,
                "media": {"payload": payload},
            })

        await websocket.send_json({
            "event": "mark",
            "streamSid": stream_sid,
            "mark": {"name": f"ai-response-{uuid.uuid4()}"},
        })

    async def flush_audio_to_ai() -> None:
        nonlocal audio_buffer
        if not stream_sid:
            return

        async with flush_lock:
            if not audio_buffer:
                return

            audio_bytes = bytes(audio_buffer)
            audio_buffer = bytearray()

            previous_chat = voice_memory.get_history(active_session_id)
            response_audio, transcript, answer_text = await _get_voice_agent().handle_twilio_voice_follow_up(
                audio_mulaw_bytes=audio_bytes,
                quote_data=_parse_quote_data(active_quote_data),
                previous_chat=previous_chat,
            )

            voice_memory.append(
                session_id=active_session_id,
                user_query=transcript,
                ai_response=answer_text,
            )
            await send_audio_to_twilio(response_audio)

    async def delayed_flush() -> None:
        await asyncio.sleep(AUDIO_FLUSH_SECONDS)
        await flush_audio_to_ai()

    def schedule_flush() -> None:
        nonlocal flush_task
        if flush_task is None or flush_task.done():
            flush_task = asyncio.create_task(delayed_flush())

    try:
        while True:
            try:
                message = await websocket.receive_json()
            except json.JSONDecodeError:
                continue

            event = message.get("event")

            if event == "start":
                stream_sid = _get_start_value(message, "streamSid")
                call_sid = _get_start_value(message, "callSid")
                active_session_id = session_id or call_sid or stream_sid or active_session_id
                active_quote_data = _get_start_quote_data(message) or active_quote_data
                continue

            if event == "media":
                payload = (message.get("media") or {}).get("payload")
                if payload:
                    try:
                        audio_buffer.extend(base64.b64decode(payload))
                        schedule_flush()
                    except (binascii.Error, ValueError):
                        continue
                continue

            if event == "stop":
                if flush_task and not flush_task.done():
                    flush_task.cancel()
                await flush_audio_to_ai()
                break
    except WebSocketDisconnect:
        pass
    finally:
        if flush_task and not flush_task.done():
            flush_task.cancel()
        audio_buffer = bytearray()


@router.delete("/quote-follow-up/{session_id}")
async def clear_quote_follow_up_session(session_id: str):
    voice_memory.clear(session_id)
    return {"message": "Voice conversation history cleared.", "session_id": session_id}
