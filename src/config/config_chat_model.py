from openai import OpenAI
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()


@dataclass
class ChatModelResponse:
    content: str


class ConfigOpenAI:
    def __init__(self, model_name: str = "gpt-5.5-2026-04-23"):
        self.model_name = model_name

    def get_response(self, input_data):

        client = OpenAI()
        response = client.responses.create(
            model=self.model_name,
            input=input_data,
        )
        return response.output_text


class OpenAIChatModel:
    def __init__(self, model_name: str = "gpt-5.5-2026-04-23"):
        self.client = OpenAI()
        self.model_name = model_name

    def invoke(self, prompt):
        response = self.client.responses.create(
            model=self.model_name,
            input=prompt,
        )
        return ChatModelResponse(content=response.output_text)

    async def astream(self, prompt):
        yield self.invoke(prompt)


class ChatModels:
    def __init__(self, model_name: str = "gpt-5.5-2026-04-23"):
        self.model_name = model_name

    def GetChatModel(self):
        return OpenAIChatModel(model_name=self.model_name)
