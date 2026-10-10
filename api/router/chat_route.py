from fastapi import APIRouter, HTTPException
from src.services.prompt_templete import PromptGenerator
from src.config.config_chat_model import ConfigOpenAI
from api.schemas.chat_body import ChatBody, RegenerateChatBody
from src.services.data_processor import ProcessData
from src.services.session_store import ChatSessionStore
from src.services.gmb_post_checker import city_from_location, clean_gmb_post, find_gmb_post_problems

router = APIRouter()


def _parse_ai_response(response_text: str) -> dict:
    try:
        return ProcessData.EnsureDict(response_text)
    except ValueError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error


def _get_checked_response(prompt: list, company_name: str, assign_location: str) -> dict:
    """Calls the model and, if the GMB post breaks the client's rules, asks it once to fix them."""
    response_text = ConfigOpenAI().get_response(prompt)
    response = _parse_ai_response(response_text)
    if not isinstance(response.get("gmb_post"), dict):
        return response

    city = city_from_location(assign_location)
    problems = find_gmb_post_problems(response["gmb_post"], company_name, city)
    if problems:
        retry_prompt = prompt + [
            {"role": "assistant", "content": response_text},
            {
                "role": "user",
                "content": (
                    "Fix these problems in gmb_post and return the same JSON object again:\n- "
                    + "\n- ".join(problems)
                ),
            },
        ]
        try:
            retry_post = _parse_ai_response(ConfigOpenAI().get_response(retry_prompt)).get("gmb_post")
        except HTTPException:
            retry_post = None
        if isinstance(retry_post, dict) and len(find_gmb_post_problems(retry_post, company_name, city)) < len(problems):
            response["gmb_post"] = retry_post

    response["gmb_post"] = clean_gmb_post(response["gmb_post"])
    return response


def _merge_regenerated_field(
    previous_response: dict,
    generated_response: dict,
    update_field_name: str,
) -> dict:
    if update_field_name not in generated_response:
        raise HTTPException(
            status_code=502,
            detail=f"AI response did not include '{update_field_name}'.",
        )

    updated_response = previous_response.copy()
    updated_response[update_field_name] = generated_response[update_field_name]
    return updated_response


@router.post("/chat")
async def chat(chat_body: ChatBody):
    post_style = PromptGenerator.pick_post_style()
    prompt = PromptGenerator.gen_prompt(image_url=chat_body.image_url,
                                        company_name = chat_body.company_name,
                                        assign_location=chat_body.assign_location,
                                        preference_instructions=chat_body.preferred_instructions,
                                        post_style=post_style)
    response = _get_checked_response(prompt, chat_body.company_name, chat_body.assign_location)
    session = ChatSessionStore.create(
        image_url=chat_body.image_url,
        company_name= chat_body.company_name, 
        assign_location = chat_body.assign_location,
        preference_instructions=chat_body.preferred_instructions,
        post_style=post_style,
        response=response,
    )
    return {
        "session_id": session.session_id,
        "response": session.response,
    }


@router.post("/regenerate")
async def regenerate(chat_body: RegenerateChatBody):
    session = ChatSessionStore.get(chat_body.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")

    # Rotate to a different angle so a refined post doesn't keep the old structure.
    post_style = session.post_style
    if chat_body.update_field_name == "gmb_post":
        post_style = PromptGenerator.pick_post_style(exclude=session.post_style)

    try:
        prompt = PromptGenerator.regenerate_prompt(
            previous_response=session.response,
            update_field_name=chat_body.update_field_name,
            user_instruction=chat_body.user_instruction,
            image_url=session.image_url,
            company_name=session.company_name,
            assign_location=session.assign_location,
            preference_instructions=session.preference_instructions,
            post_style=post_style,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    generated_response = _get_checked_response(prompt, session.company_name, session.assign_location)
    response = _merge_regenerated_field(
        previous_response=session.response,
        generated_response=generated_response,
        update_field_name=chat_body.update_field_name,
    )
    updated_session = ChatSessionStore.update_response(
        session_id=chat_body.session_id,
        response=response,
        update_field_name=chat_body.update_field_name,
        user_instruction=chat_body.user_instruction or "",
        post_style=post_style,
    )
    if updated_session is None:
        raise HTTPException(status_code=404, detail="Session not found.")

    return {
        "session_id": updated_session.session_id,
        "response": updated_session.response,
    }


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    if not ChatSessionStore.delete(session_id):
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"message": "Session deleted successfully."}
