# prompt_manager.py

from ollama._types import Message
from pydantic import BaseModel
from typing import List, Type, Any, Literal, Sequence, Mapping
import json

class ChatPromptManager:
    def __init__(self):
        self.message_history: List[Message]

    def basic_prompt(self, pydantic_model: Type[BaseModel]):
        '''
        Creates a basic prompt for the LLM based on the given Pydantic model.

        Args:
            pydantic_model (Type[BaseModel]): The Pydantic model.

        Returns:
            str: The basic prompt.
        '''
        default_system_prompt = f'''
        You are the world class algorithm for JSON responses. You will get provided a JSON schema of a Pydantic model. Your task is to extract those in this JSON schema specified properties out of a given text or image (or its context) and return a VALID JSON response adhering to the JSON schema.
        \nHere is the JSON schema: {pydantic_model.model_json_schema()}.
        \n\nYou WILL return the instance of the JSON schema with the CORRECT extracted data, NOT the JSON schema itself. The instance of the JSON schema has the following fields to extract the data for: {list(pydantic_model.model_fields.keys())}.
        '''
        return default_system_prompt

    def basic_reasoning_prompt(self, pydantic_model: Type[BaseModel]): # TODO: make clear step by step instructions with Markdown
        default_system_prompt = f'''
        # Instructions
        \n
        ## Role
        \n
        You are a world class assistant with strong reasoning capabilities.
        \n
        ## Step by step instructions
        \n
        You will get provided with a JSON schema of a Pydantic model.\n
        Your task is to extract those in this JSON schema specified properties out of a given text or imag (or its context) and return a VALID JSON response in adhering to the JSON schema.\n\n

        Get this done by following the following steps:
        1. Make a short description of the task you were given and its goal.\n
        2. Reason step by step about the best values for the fields in the JSON response. Every field in the JSON response should be a valid value according to the JSON schema. Don't come up with random fields which are not properties of the JSON schema. Don't come up with values for the fields which are not valid according to the JSON schema.\n
        3. Provide a code block with the JSON response. The code block has to start with ```json and ends with ```. Do NOT come up with code examples of any programming language. Only respond the instance of the JSON schema withing the code block (```json ```) while adhering to the JSON schema.\n

        ## The JSON schema
        \n
        Here is the JSON schema: {pydantic_model.model_json_schema()}.\n
        In the code block you WILL return the instance of the JSON schema with the CORRECT extracted data, NOT the JSON schema itself. The instance of the JSON schema has the following fields to extract the data for: {list(pydantic_model.model_fields.keys())}.
        '''

        return default_system_prompt

    def error_guidance_prompt(self, validation_error: bool | str | dict) -> Message:
        '''
        This function creates an error guidance prompt for the LLM.

        Args:
            validation_error (bool | str | dict): The validation error.

        Returns:
            Dict[str, Any]: The error guidance prompt as a message (dict).
        '''
        error_guidance_prompt: Message = {
                                    'role': 'system',
                                    'content': f'The last response raised the following validation error: {json.dumps(validation_error)}. Response with the corrected JSON and fill in the correct data while adhering the context and the JSON schema above! Make sure to adhere to given enums and choose the most likely value if value is required.'
                                }
        return error_guidance_prompt

    def error_guidance_prompt_for_reasoning(self, validation_error: bool | str | dict) -> Message:
        """
        This function creates an error guidance prompt for the LLM, when format = '' and reasoning is enabled.

        Args:
            validation_error (bool | str | dict): The validation error.

        Returns:
            Dict[str, Any]: The error guidance prompt as a message (dict).
        """
        error_guidance_prompt = f'The code block of the last response raised the following validation error: {json.dumps(validation_error)}. Response with the corrected JSON in the code block and fill in the correct data while adhering the context and the JSON schema above! A code block has to start with ```json and ends with ```. If you are not using a code block the validation will fail!'

        error_guidance_message: Message = {
                                    'role': 'system',
                                    'content': error_guidance_prompt
                                }
        return error_guidance_message

    def create_chat_prompt_for_json(
        self,
        pydantic_model: Type[BaseModel],
        messages: Sequence[Mapping[str, Any] | Message],
        format: Literal['json', '']
    ) -> List[Message]:
        """
        Creates a chat prompt for the LLM based on the given Pydantic model.
        It will contain the system prompt as well, to instruct the LLM to response the instance of the JSON schema.

        ATTENTION: If a system prompt already exists in the messages list, ollama-instructor will not add its OWN basic_prompt.

        Args:
            pydantic_model (Type[BaseModel]): The Pydantic model.
            messages (List[Dict[str, Any]]): The chat messages.

        Returns:
            List[Dict[str, Any]]: The chat messages.
        """
        chat_messages: List[Message] = messages
        if format == 'json':
            basic_prompt = self.basic_prompt(pydantic_model=pydantic_model)
        elif format == '':
            basic_prompt = self.basic_reasoning_prompt(pydantic_model=pydantic_model)
        if chat_messages[0]['role'] == 'user':
            chat_messages.insert(0, {"role": "system", "content": basic_prompt})
        #elif chat_messages[0]['role'] == 'system':
            #chat_messages.insert(1, {"role": "system", "content": basic_prompt})
        elif chat_messages[0]['role'] == 'system':
            pass
        #else:
            #chat_messages.insert(0, {"role": "system", "content": basic_prompt})
        self.message_history = chat_messages
        return messages
