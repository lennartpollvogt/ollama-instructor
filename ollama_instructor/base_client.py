from ollama._types import Message
from typing import Type, Any, Literal, List, Mapping, Sequence, AsyncIterator
from pydantic import BaseModel, ValidationError
import json
import re
from fastapi.encoders import jsonable_encoder

from .prompt_manager import ChatPromptManager
from .validation_manager import ValidationManager
from .log_config import logger, logging


class BaseOllamaInstructorClient:
    def __init__(self, host: str = 'http://localhost:11434', debug: bool = False):
        self.host = host
        self.debug = debug
        self.ollama_client = None
        self.validation_manager = ValidationManager()
        self.chat_prompt_manager = ChatPromptManager()
        self.chat_history: List[Message] = []
        self.retry_counter: int
        self.validation_error = None
        self.error: ValidationError

        if not debug:
            logger.setLevel(logging.INFO)
        else:
            logger.setLevel(logging.DEBUG)

    # resetting the states with each request to avoid errors using
    # instances of the client in a loop
    def reset_states(self, retries):
        '''
        Resets the state of the client by clearing the validation error,
        setting the retry counter to the specified number of retries,
        and clearing the chat history. This is intended to ensure that
        each request starts with a clean state, avoiding errors when using
        instances of the client in a loop.

        Args:
            retries (int): The number of retries to set for the request.
                           This will be stored in the `retry_counter` attribute.
        '''
        # logging
        logger.debug(msg=f"def {self.reset_states.__name__}")
        # functionality
        self.validation_error = None
        self.retry_counter = retries
        self.chat_history = []

    # PROMPTING
    def create_prompt(self, pydantic_model: Type[BaseModel], messages: Sequence[Mapping[str, Any] | Message], retries: int, format: Literal['json', '']):
        # logging
        logger.debug(msg=f"def {self.create_prompt.__name__}")
        # functionality
        self.chat_history = self.chat_prompt_manager.create_chat_prompt_for_json(pydantic_model=pydantic_model, messages=messages, format=format)

    def update_prompt_with_error(self, format: Literal['json', '']):
        # logging
        logger.debug(msg=f"def {self.update_prompt_with_error.__name__}")
        # fuctionality
        if self.validation_error is not None and format=='json':
            logger.info(msg=f"Validation error! Retries left: {self.retry_counter}")
            self.chat_history.append(self.chat_prompt_manager.error_guidance_prompt(validation_error=self.validation_error))
        if self.validation_error is not None and format=='':
            self.chat_history.append(self.chat_prompt_manager.error_guidance_prompt_for_reasoning(validation_error=self.validation_error))

    def prepare_messages(self, retries: int) -> List[Message]:
        # logging
        logger.debug(msg=f"def {self.prepare_messages.__name__}")
        # fuctionality
        messages: Sequence[Mapping[str, Any] | Message] = [self.chat_history[0], self.chat_history[1]]
        if self.retry_counter != retries:
            messages.extend(self.chat_history[-2:])
        logger.debug(msg=f"messages have the following type: {type(messages)}")
        logger.debug(msg="Convert content into strings")
        for message in messages:
            message['content'] = str(message['content'])
        logger.debug(msg=f"Messages: {messages}")
        return messages


    # RESPONSE HANDLING
    def extract_code_block(self, content: str) -> str:
        # logging
        logger.debug(msg=f"def {self.extract_code_block.__name__}")
        # fuctionality
        start = content.find('```json')
        if start == -1:
            logger.warning("No JSON code block found")
            return "Code block not found"

        start += len('```json\n')  # Move start to the end of '```json\n'
        end = content.find('```', start)
        if end == -1:
            logger.warning("JSON code block is not closed")
            return "Code block end not found"

        code_block = content[start:end]

        # Remove comments from the code block
        code_block = re.sub(r'//.*|#.*|%.*', '', code_block)
        code_block = re.sub(r'/\*.*?\*/', '', code_block, flags=re.DOTALL)

        # Remove empty lines
        code_block = '\n'.join(line for line in code_block.splitlines() if line.strip())

        logger.debug(f"Extracted code block: {code_block}")
        return code_block

    def handle_response(self, response: Mapping[str, Any] | AsyncIterator[Mapping[str, Any]],
                        pydantic_model: Type[BaseModel], allow_partial: bool,
                        format: Literal['json', '']) -> Mapping[str, Any] | AsyncIterator[Mapping[str, Any]]:
        # logging
        logger.debug(msg=f"def {self.handle_response.__name__}")
        # fuctionality

        if isinstance(response, AsyncIterator):
            return response

        raw_response = response['message']['content']
        self.chat_history.append(response['message'])

        content = self.process_content(raw_response, format, pydantic_model)
        if content in ['Code block not found', 'Code block end not found']:
            response['message']['content'] = content
        else:
            response['message']['content'] = self.extract_json(content)

        self.validation_error = self.validation_manager.validate_for_error_message(response, pydantic_model)
        response = self.validation_manager.add_error_log_to_final_response(response, self.validation_error, raw_response)

        return self.validate_and_return_response(response, pydantic_model, allow_partial)

    def process_content(self, content: str, format: str, pydantic_model: Type[BaseModel]) -> str:
        # logging
        logger.debug(msg=f"def {self.process_content.__name__}")
        # fuctionality
        if format == '':
            content = self.extract_code_block(content)
            if content == '{}':
                self.chat_history[-1] = self.create_empty_model_dict(pydantic_model)
            return jsonable_encoder(content)
        return jsonable_encoder(content)

    def create_empty_model_dict(self, pydantic_model: Type[BaseModel]) -> Message:
        # logging
        logger.debug(msg=f"def {self.create_empty_model_dict.__name__}")
        # fuctionality
        content: dict = {key: None for key in pydantic_model.model_fields}

        updated_response: Message = {
            'role': 'assistant',
            'content': f'```json\n{json.dumps(content)}\n```'
        }
        return updated_response

    def extract_json(self, content: str) -> dict:
        # logging
        logger.debug(msg=f"def {self.extract_json.__name__}")
        # fuctionality
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            logger.error("Failed to extract JSON from content")
            return {}

    def validate_and_return_response(self, response: Mapping[str, Any],
                                     pydantic_model: Type[BaseModel],
                                     allow_partial: bool) -> Mapping[str, Any] | AsyncIterator[Mapping[str, Any]]:
        # logging
        logger.debug(msg=f"def {self.validate_and_return_response.__name__}")
        # fuctionality
        if self.validation_error is False:
            response['retries_left'] = self.retry_counter
            return response

        try:
            if self.retry_counter > 1:
                return self.validate_response(response, pydantic_model, False)
            elif self.retry_counter == 1:
                return self.validate_response(response, pydantic_model, allow_partial)
            else:
                raise Exception("Retries exhausted and validation still fails.")
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            raise e

    def validate_response(self, response: Mapping[str, Any],
                          pydantic_model: Type[BaseModel],
                          allow_partial: bool) -> Mapping[str, Any]:
        # logging
        logger.debug(msg=f"def {self.validate_response.__name__}")
        # fuctionality
        validator = self.validation_manager.validate_partial_model if allow_partial else self.validation_manager.validate_chat_completion
        validated_response: Mapping[str, Any] | AsyncIterator[Mapping[str, Any]] = validator(response, pydantic_model)
        validated_response['retries_left'] = self.retry_counter
        return validated_response
