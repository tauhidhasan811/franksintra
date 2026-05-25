from typing import List
from collections.abc import AsyncIterable

from src.config.config_chat_model import ChatModels
from src.tools.database_tools import GetAllData
from src.tools.user_contact_info import SaveUserContactInfo
from src.services.prompt_templete import PromptGenerator


class AgenController:
    def __init__(self):
        self.agent = ChatModels().GetChatModel()
        self.promptGen = PromptGenerator()

    def __call_agent(self, prompt):
        return self.agent.invoke(prompt)

    async def __call_agent_stream(self, prompt) -> AsyncIterable[str]:
        async for chunk in self.agent.astream(prompt):
            content = getattr(chunk, "content", None)

            if isinstance(content, str) and content:
                yield content
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text = item.get("text", "")
                        if text:
                            yield text

    def __get_tools_data(self, tools: List) -> List:
        all_tools_data = []

        for tool in tools:
            name = tool["name"]
            args = tool["args"]
            if name == "GetAllData":
                tool_result = GetAllData.invoke(args)
            elif name == "SaveUserContactInfo":
                tool_result = SaveUserContactInfo.invoke(args)
            else:
                continue

            all_tools_data.append({
                "tool_name": name,
                "tool_result": tool_result
            })

        # print("*" * 60)
        # print(" " * 20, "Tools data are")
        # print("*" * 60)
        # print(all_tools_data)

        return all_tools_data

    def __get_agent_response(self, prompt):
        response = self.__call_agent(prompt=prompt)

        have_tools = False
        tools_data = []

        tools = getattr(response, "tool_calls", []) or []

        # print("x" * 60)
        # print(" " * 20, f"Find tools {tools}")
        # print("x" * 60)

        if tools:
            tools_data = self.__get_tools_data(tools=tools)
            have_tools = bool(tools_data)

        content = response.content
        return have_tools, content, tools_data

    async def get_response(self, user_query = None, relevent_info = None, previous_chat = None, file_data = None) -> AsyncIterable[str]:
        try:
            if user_query is not None:
                prompt = self.promptGen.GeneralPrompt(
                    user_query=user_query,
                    relevent_info=relevent_info,
                    previous_chat=previous_chat,
                    file_data=file_data
                )
            else: 
                prompt = self.promptGen.InitialPrompt()

            have_tools, content, tools_data = self.__get_agent_response(prompt=prompt)

            if have_tools:
                # yield "Analysing tools data...\n"
                tools_prompt = self.promptGen.ToolsPrompt(
                    user_query=user_query,
                    tools_data=tools_data
                )

                async for chunk in self.__call_agent_stream(prompt=tools_prompt):
                    yield chunk
            else:
                async for chunk in self.__call_agent_stream(prompt=prompt):
                    yield chunk

        except Exception as e:
            yield f"Error: {str(e)}"


        
