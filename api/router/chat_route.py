from fastapi import APIRouter, Form, File, UploadFile
import tempfile
import shutil
import os
from src.services.data_processor import DataProcessor
from fastapi.responses import StreamingResponse
from api.schemas.chat_body import Chatbody, ChatWithFile, ImagePromptBody, RegenerateChatBody
from src.services.prompt_templete import PromptGenerator
from src.controller.agent_controller import AgenController
from src.services.rag_knowledge import RagKnowledge
from src.config.config_embedding_model import Embedder
from src.config.config_chat_model import ConfigOpenAI


embedder = Embedder().hugg_sentence_embedder()
rag = RagKnowledge(embedding_model=embedder)
data_processor = DataProcessor()

router = APIRouter(prefix='/api/ai', tags=['Chat With AI'])


def _get_latest_query(body: RegenerateChatBody) -> str:
    if body.user_query:
        return body.user_query
    if body.previous_chat:
        return body.previous_chat[-1].user_query
    return ""

@router.post('/chatbot')
async def chat_with_ai(body: Chatbody):
    try:
        previous_chat = body.previous_chat
        selected_chat = data_processor.process_previous_history(previous_data=previous_chat)
        user_query = body.user_query
        relevent_info = rag.retrive_chunk(user_query)
        # print(relevent_info)
        file_data = {
            "is_read": False, 
            "data": "no data"
        }
        agent_controller = AgenController()

        return StreamingResponse(agent_controller.get_response(user_query=user_query, 
                                                            relevent_info = relevent_info, 
                                                            previous_chat=selected_chat,
                                                            file_data=file_data), 
                                                            media_type='text/event-stream')
    
    except Exception as ex:
         
         return StreamingResponse(str(ex))


@router.post('/image-description')
async def describe_image(body: ImagePromptBody):
    try:
        prompt = PromptGenerator.gen_prompt(image_url=body.image_url)
        response = ConfigOpenAI().get_response(prompt)
        return {"response": response}

    except Exception as ex:

         return {"error": str(ex)}


@router.post('/chatbot-regenerate')
async def regenerate_chat_response(body: RegenerateChatBody):
    try:
        user_query = _get_latest_query(body)
        selected_chat = data_processor.process_previous_history(previous_data=body.previous_chat)
        relevent_info = rag.retrive_chunk(user_query)
        regenerate_query = (
            f"{body.regenerate_instruction}\n\n"
            f"Latest user request to answer again:\n{user_query}"
        )
        file_data = {
            "is_read": False,
            "data": "no data"
        }
        agent_controller = AgenController()

        return StreamingResponse(agent_controller.get_response(user_query=regenerate_query,
                                                            relevent_info = relevent_info,
                                                            previous_chat=selected_chat,
                                                            file_data=file_data),
                                                            media_type='text/event-stream')

    except Exception as ex:

         return StreamingResponse(str(ex))



@router.post('/chatbot-with-file')
async def chat_with_ai(previous_chat: str = Form(),
                        user_query: str = Form(),
                        file: UploadFile = File(None)):
    try:
        file_data = {
            "is_read": False, 
            "data": "no data"
        }
        previous_chat = ChatWithFile.from_form_value(previous_chat).previous_chat
        if file is not None:
            with tempfile.TemporaryDirectory() as temp_dir:
                    file_name = file.filename
                    file_path = os.path.join(temp_dir, file_name)
                    with open(file_path, "wb") as buffer:
                        shutil.copyfileobj(file.file, buffer)
                    # print(file_path)
                    read_file_data = DataProcessor.file_reader_route(path=file_path)
            file_data = read_file_data

        
        selected_chat = data_processor.process_previous_history(previous_data=previous_chat)
        user_query = user_query
        relevent_info = rag.retrive_chunk(user_query)
        # print(relevent_info)
        agent_controller = AgenController()

        return StreamingResponse(agent_controller.get_response(user_query=user_query, 
                                                            relevent_info = relevent_info, 
                                                            previous_chat=selected_chat,
                                                            file_data=file_data), 
                                                            media_type='text/event-stream')
    
    except Exception as ex:
         
         return StreamingResponse(str(ex))
    
    
@router.post('/chatbot-initial-message')
async def chat_with_ai():
    try:
        
        agent_controller = AgenController()

        return StreamingResponse(agent_controller.get_response(), media_type='text/event-stream')
    
    except Exception as ex:
         
         return StreamingResponse(str(ex))
