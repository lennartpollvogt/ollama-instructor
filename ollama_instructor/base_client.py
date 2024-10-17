import ollama
from ollama._types import Message
from typing import Type, Any, Dict, Literal, List, Generator, AsyncGenerator, Mapping, Iterator, Sequence, AsyncIterator
from pydantic import BaseModel, ValidationError
import json
from copy import deepcopy
import re
import rich
from fastapi.encoders import jsonable_encoder
from icecream import ic
ic.configureOutput(prefix='ollama-instrutor | ')

from ollama_instructor.prompt_manager import ChatPromptManager
from ollama_instructor.validation_manager import ValidationManager

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
            ic.disable()

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
        self.validation_error = None
        self.retry_counter = retries
        self.chat_history = []

    def create_prompt(self, pydantic_model: Type[BaseModel], messages: List[Message], retries: int, format: Literal['json', '']):
        self.chat_history = self.chat_prompt_manager.create_chat_prompt_for_json(pydantic_model=pydantic_model, messages=messages, format=format)

    def update_prompt_with_error(self, format: Literal['json', '']):
        if self.validation_error is not None and format=='json':
            self.chat_history.append(self.chat_prompt_manager.error_guidance_prompt(validation_error=self.validation_error))
        if self.validation_error is not None and format=='':
            self.chat_history.append(self.chat_prompt_manager.error_guidance_prompt_for_reasoning(validation_error=self.validation_error))

    def prepare_messages(self, retries: int) -> List[Message]:
        messages: Sequence[Message] = [self.chat_history[0], self.chat_history[1]]
        if self.retry_counter != retries:
            messages.extend(self.chat_history[-2:])
        return messages

    def extract_code_block(self, content: str) -> str: # TODO: make extract search for fields
        start = content.find('```json')
        if start == -1:
            return 'Code block not found'

        start += len('```json\n')  # Move start to the end of '```json\n'
        end = content.find('```', start)
        if end == -1:
            return 'Code block end not found'

        code_block = content[start:end]
        # Remove comments from the code block
        code_block = re.sub(r'//.*|#.*|%.*', '', code_block)
        code_block = re.sub(r'/\*.*?\*/', '', code_block, flags=re.DOTALL)
        ic(code_block)
        ic(type(code_block))

        return code_block

    def handle_response(self, response: Mapping[str, Any] | AsyncIterator[Mapping[str, Any]], pydantic_model: Type[BaseModel], allow_partial: bool, format: Literal['json', '']) -> Mapping[str, Any] | AsyncIterator[Mapping[str, Any]]:
        ic(type(response['message']['content']))
        ic(response)

        # Capture the raw response content
        raw_response = deepcopy(response)
        raw_response_content = raw_response['message']['content']
        self.chat_history.append(raw_response['message'])  # Store the raw message before modification

        if format == '':
            content: str = response['message']['content']
            if isinstance(content, str):
                content = self.extract_code_block(content)
                ic(content)
                if content == 'Code block not found' or content == 'Code block end not found':
                    partial_content = {}
                    # create empty dict with keys from pydantic model and set all values to None
                    for key in pydantic_model.model_fields:
                        partial_content[key] = None
                    # convert content to string
                    #content = json.dumps(content)
                    updated_response: Message = {
                        'role': 'assistant',
                        'content': f'```json\n{partial_content}\n```'
                    }
                    # replace the last message in chat_history with the updated content
                    self.chat_history[-1] = updated_response
                else:
                    content = jsonable_encoder(content)
                    ic()
                    ic(content)
        else:
            content = jsonable_encoder(response['message']['content'])

        # Extract JSON from response if there is additional text (e.g. whitespace)
        response['message']['content'] = json.loads(re.search(r'\{.*\}', content, re.DOTALL).group())

        ic(type(response['message']['content'])) # must be string otherwise would fail in retry
        self.validation_error = self.validation_manager.validate_for_error_message(response=response, pydantic_model=pydantic_model)
        ic(self.validation_error)
        ic()
        # Store the full raw response content
        response = self.validation_manager.add_error_log_to_final_response(response=response, error_message=self.validation_error, raw_message=raw_response_content)
        ic()
        ic(self.retry_counter)

        # Validate and return response under certain conditions
        if self.validation_error is not False:
            if self.retry_counter > 1:
                try:
                    ic(allow_partial)
                    response = self.validation_manager.validate_chat_completion(response=response, pydantic_model=pydantic_model)
                    ic(response)
                    response['retries_left'] = self.retry_counter
                    return response
                except ValidationError as e:
                    ic(e)
                    raise e
            elif self.retry_counter == 1:
                try:
                    if allow_partial:
                        ic(allow_partial)
                        response = self.validation_manager.validate_partial_model(response=response, pydantic_model=pydantic_model)
                        ic()
                        response['retries_left'] = self.retry_counter
                        return response
                    elif allow_partial is False:
                        ic(allow_partial)
                        response = self.validation_manager.validate_chat_completion(response=response, pydantic_model=pydantic_model)
                        ic(response)
                        response['retries_left'] = self.retry_counter
                        return response
                except ValidationError as e:
                    ic(e)
                    raise e
            else:
                ic()
                raise Exception("Retries exhausted and validation still fails.")
        else:
            ic()
            response['message']['content'] = response['message']['content'] # TODO: maybe check if already string
            response['retries_left'] = self.retry_counter
            return response

    # specific for streaming
    def validate_chunk(self, chunk: Dict[str, Any], pydantic_model: Type[BaseModel]):
        try:
            chunk['message']['content'] = json.loads(re.search(r'\{.*\}', chunk['message']['content'], re.DOTALL).group())
            ic(type(chunk['message']['content']))  # must be string otherwise would fail in retry
            self.validation_error = self.validation_manager.validate_for_error_message(response=chunk, pydantic_model=pydantic_model)
        except Exception as e:
            self.validation_error = str(e)

    def handle_stream_response(self, chunk: Iterator[Mapping[str, Any]], pydantic_model: Type[BaseModel], allow_partial: bool) -> Iterator[Mapping[str, Any]]:
        if self.validation_error is not False:
            if self.retry_counter == 0:
                ic()
                if allow_partial:
                    ic(allow_partial)
                    try:
                        chunk = self.validation_manager.validate_partial_model(response=chunk, pydantic_model=pydantic_model)
                        ic()
                        chunk['retries_left'] = self.retry_counter
                        yield chunk
                        return chunk
                    except ValidationError as e:
                        print("Retries exhausted and validation still fails.")
                        raise e
                else:
                    ic(allow_partial)
                    try:
                        chunk = self.validation_manager.validate_chat_completion(response=chunk, pydantic_model=pydantic_model)
                        ic(chunk)
                        chunk['retries_left'] = self.retry_counter
                        yield chunk
                        return chunk
                    except ValidationError as e:
                        ic()
                        print("Retries exhausted and validation still fails.")
                        raise e
            else:
                ic()
                self.retry_counter -= 1
        else:
            ic()
            chunk['message']['content'] = json.loads(chunk['message']['content'])
            chunk['retries_left'] = self.retry_counter
            yield chunk
            return chunk
