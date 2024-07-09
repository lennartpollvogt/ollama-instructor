from pydantic import BaseModel
from typing import List, Dict, Type, Any
import json

class ChatPromptManager:
    def __init__(self):
        self.message_history: List

    ####################
    # BASIC PROMPT
    ####################
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
    \nHere is the JSON schema: {pydantic_model.model_json_schema().get('properties', {})}.
    \n\nYou WILL return the instance of the JSON schema with the CORRECT extracted data, NOT the JSON schema itself. The instance of the JSON schema has the following fields to extract the data for: {list(pydantic_model.model_fields.keys())}.
        '''
        return default_system_prompt
    
    ####################
    # ERROR GUIDANCE PROMPT
    ####################
    def error_guidance_prompt(self, validation_error: bool | str | dict) -> Dict[str, Any]:
        '''
        This function creates an error guidance prompt for the LLM.

        Args:
            validation_error (bool | str | dict): The validation error.

        Returns:
            Dict[str, Any]: The error guidance prompt as a message (dict).
        '''
        error_guidance_prompt = {
                                    'role': 'system',
                                    'content': f'The last response raised the following validation error: {json.dumps(validation_error)}. Response with the corrected JSON and fill in the correct data while adhering the context and the JSON schema above!'
                                }
        return error_guidance_prompt
    
    ####################
    # PROMPT HELPER FUNCTION
    ####################
    def create_chat_prompt_for_json(
            self,
            pydantic_model: BaseModel,
            messages: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        '''
        Creates a chat prompt for the LLM based on the given Pydantic model.
        It will contain the system prompt as well, to instruct the LLM to response the instance of the JSON schema.

        ATTENTION: If a system prompt already exists in the messages list, ollama-instructor will not add its OWN basic_prompt.

        Args:
            pydantic_model (Type[BaseModel]): The Pydantic model.
            messages (List[Dict[str, Any]]): The chat messages.

        Returns:
            List[Dict[str, Any]]: The chat messages.
        '''
        chat_messages = messages
        basic_prompt = self.basic_prompt(pydantic_model=pydantic_model)
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