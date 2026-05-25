from src.services.prompt_templete import PromptGenerator
from src.config.config_chat_model import ConfigOpenAI
prompt = PromptGenerator.gen_prompt(image_url="https://res.cloudinary.com/dhtiyigyy/image/upload/v1779690733/local_hgumf0.jpg")


response = ConfigOpenAI().get_response(prompt)
print(response)