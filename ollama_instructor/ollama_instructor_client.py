# ollama_instructor_client.py

import ollama
from typing import Type, Any, Dict, Literal, List, Generator, AsyncGenerator, Mapping
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
        self.chat_history = []
        self.retry_counter = None
        self.validation_error = None

        if not debug:
            ic.disable()

    def create_prompt_and_handle_retry(self, pydantic_model: Type[BaseModel], messages: List[Dict[str, Any]], retries: int, format: Literal['json', '']):
        self.retry_counter = retries
        self.chat_history = self.chat_prompt_manager.create_chat_prompt_for_json(pydantic_model=pydantic_model, messages=messages, format=format)

    def update_prompt_with_error(self, format: Literal['json', '']):
        if self.validation_error is not None and format=='json':
            self.chat_history.append(self.chat_prompt_manager.error_guidance_prompt(validation_error=self.validation_error))
        if self.validation_error is not None and format=='':
            self.chat_history.append(self.chat_prompt_manager.error_guidance_prompt_for_reasoning(validation_error=self.validation_error))

    def prepare_messages(self, retries: int):
        messages = [self.chat_history[0], self.chat_history[1]]
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
        rich.print(code_block)
        print(type(code_block))

        return code_block

    def handle_response(self, response: Dict[str, Any], pydantic_model: Type[BaseModel], allow_partial: bool, format: Literal['json', '']):
        ic(type(response['message']['content']))
        ic(response['message']['content'])

        # Capture the raw response content
        raw_response = deepcopy(response)
        raw_response_content = raw_response['message']['content']
        self.chat_history.append(raw_response['message'])  # Store the raw message before modification
        ic(self.chat_history)

        if format == '':
            content = response['message']['content']
            if isinstance(content, str):
                content = self.extract_code_block(content)
                ic(content)
                if content == 'Code block not found' or content == 'Code block end not found':
                    content = self.validation_manager.validate_partial_model(content=raw_response_content, pydantic_model=pydantic_model)
                else:
                    content = jsonable_encoder(content)   
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
        if self.validation_error is not True and self.retry_counter > 0:
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
            except ValidationError as e:
                ic(e)
                raise e
        elif self.validation_error is True and self.retry_counter > 0:
            ic()
            #response['message']['content'] = json.loads(response['message']['content'])
            response['message']['content'] = response['message']['content'] # TODO: maybe check if already string
            response['retries_left'] = self.retry_counter
            return response
        else:
            ic()
            raise Exception("Retries exhausted and validation still fails.")

    def handle_stream_response(self, response, pydantic_model: Type[BaseModel], allow_partial: bool, format: Literal['json', '']): # not in use. Needs refactoring to handle stream and retry logic
        # format = '' is not used yet
        # TODO: implement extraction of code block from stream
        # needs maybe different functions:
        # One for the final respond and another one for the stream
        # the one for the stream should have a fallback until ```json occurs but should end, when code block ends with ```
        # OR only the final response will be extracted.
        expanding_response = ""
        for chunk in response:
            expanding_response += chunk['message']['content']
            chunk['message']['content'] = expanding_response
            chunk = self.validation_manager.validate_chat_completion_with_stream(chunk=chunk, pydantic_model=pydantic_model)
            self.validation_error = self.validation_manager.validate_for_error_message(response=chunk, pydantic_model=pydantic_model)
            chunk = self.validation_manager.add_error_log_to_final_response(response=chunk, error_message=self.validation_error, raw_message=expanding_response)
            yield chunk

        self.chat_history += [chunk['message']]
        chunk['message']['content'] = json.dumps(chunk['message']['content'])
        if self.validation_error is not True:
            if self.retry_counter == 0:
                if allow_partial:
                    try:
                        ic(allow_partial)
                        chunk = self.validation_manager.validate_partial_model(response=chunk, pydantic_model=pydantic_model)
                        ic()
                        chunk['retries_left'] = self.retry_counter
                        return chunk
                    except ValidationError as e:
                        raise e
                elif allow_partial is False:
                    try:
                        ic(allow_partial)
                        chunk = self.validation_manager.validate_chat_completion(response=chunk, pydantic_model=pydantic_model)
                        ic(chunk)
                        chunk['retries_left'] = self.retry_counter
                        return chunk
                    except ValidationError as e:
                        raise e
            else:
                ic()
                self.retry_counter -= 1
        elif self.validation_error is True and self.retry_counter > 0:
            try:
                ic()
                chunk['message']['content'] = json.loads(chunk['message']['content'])
                chunk['retries_left'] = self.retry_counter
                return chunk
            except Exception as e:
                raise e


class OllamaInstructorClient(BaseOllamaInstructorClient):
    '''
    This class is the client of ollama-instructor. It is a simple wrapper around the ollama client.
    It is one of two main classes that you will use to interact with ollama-instructor.

    Attributes:
        host (str): The host URL where the Ollama service is available. Defaults to http://localhost:11434
        debug (bool): Enable debugging to output internal states and processes. Defaults to False
        ollama_client (ollama.Client): An client for the Ollama API.
        validation_manager (ValidationManager): Handles validation of responses based on Pydantic models.
        chat_prompt_manager (ChatPromptManager): Manages creation of chat prompts based on the user input.
        chat_history (List[Dict[str, Any]]): Stores the history of chat interactions.
        retry_counter (int): Counts the retries left when a validation fails.
        validation_error (Union[bool, str, dict, None]): Records any validation error encountered.

    Args:
        host (str): The url of the ollama server. Defaults to http://localhost:11434
        debug (bool): Whether to print debug messages. Defaults to False

    Methods:
        `chat_completion`: This method is used for chat completion without streaming.
        `chat_completion_with_streaming`: This method is used for chat completion with streaming.
    
    Both Methods handle your prompts, the LLM's response and its validation identically. For more information look into the docs of both methods.

    A characteristic of ollama instructor is that it makes sure that you get a valid JSON in the structur of the basic Pydantic model you send with the request.
    But, in case of validation failure, it will get rid of the invalid parts of the LLM's response. See the documentation of ollama instructor for more information on this topic.

    Information:
    The ollama instructor will return a modified version of Ollama's response dict. The modifications are as follows:
    - `validation_errors`: This will contain the `ValidationError`raised during Pydantic's validation, if the response of the LLM is invalid.
    - `raw_response`: This will contain the raw response from the LLM.
    - `retries_left`: This will contain the number of retries left for the current request.

    
    Example:
    ```Python
    from ollama_instructor.ollama_instructor_client import OllamaInstructorClient
    from pydantic import BaseModel

    class Person(BaseModel):
        name: str
        age: int

    client = OllamaInstructorClient(host="http://localhost:11434") # by default the host is http://localhost:11434
    
    response = client.chat_completion(
        model='llama3',
        pydantic_model=Person,
        messages=[
            {
                'role': 'user',
                'content': 'Jason is 21 years old.'
            }
        ]
    )
    
    print(response)
    ```
    '''
    def __init__(self, host: str = 'http://localhost:11434', debug: bool = False):
        super().__init__(host, debug)
        self.ollama_client = ollama.Client(host=host)

    def chat_completion(self, pydantic_model: Type[BaseModel], messages: List[Dict[str, Any]], model: str, retries: int = 3, format: Literal['', 'json'] = 'json', allow_partial: bool = False, **kwargs) -> Mapping[str, Any]:
        '''
        Create a chat completion with the LLM and validate the response with the provided Pydantic model.
        
        **This method is not for streaming.** Use `chat_completion_with_stream` instead.

        Args:
            pydantic_model (Type[BaseModel]): The Pydantic model for validation.
            messages (List[Dict[str, Any]]): The chat messages. ATTENTION: if your messages contain a system prompt, ollama-instructor will not provide its own system prompt. MAKE SURE to instrcut the LLM properly to your needs!
            model (str): The model to use for chatting.
            retries (int): The number of retries if the response is not valid. This will lead into another request with further instructions on the validation error of the previous response.
            format (Literal['', 'json']): The format of the response. By default it is 'json'. It's recommended to use 'json'.
            allow_partial (bool): If True, the response can be partial. Otherwise, the response must contain all fields of the Pydantic model. Have in mind that you can get an uncomplete response when set to `True`.
            **kwargs: Additional arguments to pass to the LLM client of `Ollama`.

        Returns:
            Dict[str, Any]: The Dict contains all key-value-pairs known from `Ollama` and some additional like:
                - the last validation error if there is one
                - the left retries
                - the raw response (the dictionary of 'message') of the LLM before the validation does it's magic

        Example:
            ```Python
            from ollama_instructor.ollama_instructor_client import OllamaInstructorClient
            from pydantic import BaseModel
            from enum import Enum

            client = OllamaInstructorClient(host='http://localhost:11434')

            class Gender(Enum):
                MALE = 'male'
                FEMALE = 'female'

            class Person(BaseModel):
                name: str
                age: int
                gender: Gender

            response = client.chat_completion(
                pydantic_model=Person,
                messages=[
                    {
                        'role': 'user',
                        'content': 'Jason is 45 years old.'
                    }
                ],
                model='mistral:7b-instruct',
            )
            
            print(response['message']['content'])
            # >>> Output example:
            # {'name': 'Jason', 'age': 45, 'gender': 'male'}
            ```
        '''
        self.create_prompt_and_handle_retry(pydantic_model, messages, retries, format=format)
    
        while self.validation_error is not True and self.retry_counter > 0:
            ic(self.retry_counter)
            self.update_prompt_with_error(format=format)
            ic(self.chat_history)
            
            try:
                ic()
                messages = self.prepare_messages(retries)
                ic()
                response = self.ollama_client.chat(
                    model=model,
                    messages=messages,
                    format=format,
                    stream=False,
                    **kwargs
                )
                try:
                    return self.handle_response(response=response, pydantic_model=pydantic_model, allow_partial=allow_partial, format=format)
                except ValidationError as e:
                    self.retry_counter -= 1

            except Exception as e:
                ic()
                raise e

        raise Exception("Retries exhausted and validation still fails.")

    def chat_completion_with_stream(self, pydantic_model: Type[BaseModel], messages: List[Dict[str, Any]], model: str, retries: int = 3, format: Literal['', 'json'] = 'json', allow_partial: bool = False, **kwargs) -> Generator[Dict[str, Any], None, None]: 
        '''
        Chat with the model and validate the response with the provided Pydantic model.

        **This method is for streaming.** Use `chat_completion` instead.

        Args:
            pydantic_model (Type[BaseModel]): The Pydantic model for validation.
            messages (List[Dict[str, Any]]): The chat messages.
            model (str): The LLM model.
            retries (int): The number of retries if the response is not valid.
            format (Literal['', 'json']): The format of the response.
            allow_partial (bool): If True, the response can be partial. Otherwise, the response must contain all fields of the Pydantic model. Have in mind that you can get an uncomplete response when set to `True`.
            **kwargs: Additional arguments to pass to the LLM client of `Ollama`.

        Returns:
            Generator[Dict[str, Any], None, None]: The generated response.

        Example:
            ```Python
            from ollama_instructor.ollama_instructor_client import OllamaInstructorClient
            from pydantic import BaseModel
            from enum import Enum

            client = OllamaInstructorClient(host='http://localhost:11434')

            class Gender(Enum):
                MALE = 'male'
                FEMALE = 'female'

            class Person(BaseModel):
                name: str
                age: int
                gender: Gender

            response = client.chat_completion_with_stream(
                pydantic_model=Person,
                messages=[
                    {
                        'role': 'user',
                        'content': 'Jason is 45 years old.'
                    }
                ],
                model='mistral:7b-instruct',
            )
            
            for chunk in response:
                print(chunk['message']['content'])
            # >>> Output example:
            # {'name': 'Jason', 'age': 45, 'gender': 'male'}
        '''
        self.retry_counter = retries
        system_and_user_prompt = self.chat_prompt_manager.create_chat_prompt_for_json(pydantic_model=pydantic_model, messages=messages, format='json')
        self.chat_history = system_and_user_prompt
        # start the while loop
        while self.validation_error is not None or self.retry_counter >= 0:
            if self.validation_error is not None:
                self.chat_history.append(self.chat_prompt_manager.error_guidance_prompt(validation_error=self.validation_error))
            expanding_response = ""
            try:
                ic()
                messages = []
                messages.append(self.chat_history[0])
                messages.append(self.chat_history[1])
                if self.retry_counter != retries:
                    messages.append(self.chat_history[-2])
                    messages.append(self.chat_history[-1])
                ic()
                ic(messages)
                ic(type(messages))
                response = self.ollama_client.chat(
                    model=model,
                    messages=messages,
                    format=format,
                    stream=True,
                    **kwargs
                )
                for chunk in response:
                    expanding_response += chunk['message']['content']
                    chunk['message']['content'] = expanding_response
                    # Validation block of chunks
                    chunk = self.validation_manager.validate_chat_completion_with_stream(chunk=chunk, pydantic_model=pydantic_model)
                    self.validation_error = self.validation_manager.validate_for_error_message(response=chunk, pydantic_model=pydantic_model)
                    chunk = self.validation_manager.add_error_log_to_final_response(response=chunk, error_message=self.validation_error, raw_message=expanding_response)
                    yield chunk

                # Append chat_history
                self.chat_history += [chunk['message']]
                # turn the final response into a str
                chunk['message']['content'] = json.dumps(chunk['message']['content'])
                # Validate the final response
                if self.validation_error is not True:
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
                   
            except Exception as e:
                ic()
                ic(e)
                raise e

class OllamaInstructorAsyncClient(BaseOllamaInstructorClient):
    def __init__(self, host: str = 'http://localhost:11434', debug: bool = False):
        super().__init__(host, debug)

    async def async_init(self):
        self.ollama_client = ollama.AsyncClient(host=self.host)
        self.validation_manager = ValidationManager()
        self.chat_prompt_manager = ChatPromptManager()
        if not self.debug:
            ic.disable()

    async def chat_completion(self, pydantic_model: Type[BaseModel], messages: List[Dict[str, Any]], model: str, retries: int = 3, format: Literal['', 'json'] = 'json', allow_partial: bool = False, **kwargs):
        '''
        Create a chat completion with the LLM and validate the response with the provided Pydantic model.
        
        **This method is not for streaming.** Use `chat_completion_with_stream` instead.

        Args:
            pydantic_model (Type[BaseModel]): The Pydantic model for validation.
            messages (List[Dict[str, Any]]): The chat messages. ATTENTION: if your messages contain a system prompt, ollama-instructor will not provide its own system prompt. MAKE SURE to instrcut the LLM properly to your needs!
            model (str): The model to use for chatting.
            retries (int): The number of retries if the response is not valid. This will lead into another request with further instructions on the validation error of the previous response.
            format (Literal['', 'json']): The format of the response. By default it is 'json'. It's recommended to use 'json'.
            allow_partial (bool): If True, the response can be partial. Otherwise, the response must contain all fields of the Pydantic model. Have in mind that you can get an uncomplete response when set to `True`.
            **kwargs: Additional arguments to pass to the LLM client of `Ollama`.

        Returns:
            Dict[str, Any]: The Dict contains all key-value-pairs known from `Ollama` and some additional like:
                - the last validation error if there is one
                - the left retries
                - the raw response (the dictionary of 'message') of the LLM before the validation does it's magic


        Example:
        ```python
        from pydantic import BaseModel, ConfigDict
        from enum import Enum
        from typing import List
        import asyncio
        import rich

        class Gender(Enum):
            MALE = 'male'
            FEMALE = 'female'

        class Person(BaseModel):
            name: str
            age: int
            gender: Gender
            friends: List[str] = []

            model_config = ConfigDict(
                extra='forbid'
            )

        async def main():
            client = OllamaInstructorAsyncClient(
                host='http://localhost:11434',
                debug=True
            )
            await client.async_init()

            response = await client.chat_completion(
                model='phi3:instruct',
                pydantic_model=Person,
                messages=[
                    {
                        'role': 'user',
                        'content': 'Jason is 25 years old. Jason loves to play soccer with his friends Nick and Gabriel. His favorite food is pizza.'
                    }
                ],
            )
            rich.print(response)

        if __name__ == "__main__":
            asyncio.run(main())
        ```
        '''
        self.create_prompt_and_handle_retry(pydantic_model=pydantic_model, messages=messages, retries=retries, format=format)
        
        while self.validation_error is not True and self.retry_counter > 0:
            ic(self.retry_counter)
            self.update_prompt_with_error(format=format)
            ic(self.chat_history)
            
            try:
                ic()
                messages = self.prepare_messages(retries)
                ic()
                response = await self.ollama_client.chat(
                    model=model,
                    messages=messages,
                    format=format,
                    stream=False,
                    **kwargs
                )
                try:
                    return self.handle_response(response=response, pydantic_model=pydantic_model, allow_partial=allow_partial, format=format)
                except ValidationError as e:
                    self.retry_counter -= 1

            except Exception as e:
                ic()
                raise e
