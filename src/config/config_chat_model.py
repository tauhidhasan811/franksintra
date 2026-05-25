from openai import OpenAI
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()


@dataclass
class ChatModelResponse:
    content: str
    tool_calls: list


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

