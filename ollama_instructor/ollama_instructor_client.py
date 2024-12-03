# ollama_instructor_client.py
from typing_extensions import deprecated

import ollama
from ollama._types import Message, Options
from typing import Iterator, Type, Any, Literal, Mapping, Sequence
from pydantic import BaseModel, ValidationError

from .prompt_manager import ChatPromptManager
from .validation_manager import ValidationManager
from .base_client import BaseOllamaInstructorClient # , logger

from .log_config import logger

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

    def chat_completion(self, pydantic_model: Type[BaseModel], messages: Sequence[Mapping[str, Any] | Message], model: str, retries: int = 3, format: Literal['', 'json'] = 'json', allow_partial: bool = False, options: Options | None = None, keep_alive: float | str | None = None) -> Mapping[str, Any]:
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
        # logging
        logger.debug(msg=f"def {self.chat_completion.__name__}")
        # functionality
        self.reset_states(retries=retries)
        self.create_prompt(pydantic_model, messages, retries, format=format)

        logger.debug("Start while loop")
        while self.validation_error is not False and self.retry_counter > 0:
            self.update_prompt_with_error(format=format)

            try:
                logger.debug("Prepare message and set left retries")
                messages = self.prepare_messages(retries)
                logger.debug("Request ollama client")
                response = self.ollama_client.chat(
                    model=model,
                    messages=messages,
                    format=format,
                    stream=False,
                    options=options,
                    keep_alive=keep_alive
                )
                logger.debug(msg=f"Raw response: {response['message']['content']}")
                try:
                    return self.handle_response(response=response, pydantic_model=pydantic_model, allow_partial=allow_partial, format=format)
                except ValidationError as e:
                    logger.debug(msg=f"ValidationError: {e}")
                    self.retry_counter -= 1

            except Exception as e:
                raise e
        # TODO: Test the exception for retries
        #raise Exception("Retries exhausted and validation still fails.")

    @deprecated("The chat_completion_with_stream function is currently broken due to a dependency version update. Please use chat_completion instead until this is fixed.")
    def chat_completion_with_stream(self, pydantic_model: Type[BaseModel], messages: Sequence[Mapping[str, Any] | Message], model: str, retries: int = 3, format: Literal['', 'json'] = 'json', allow_partial: bool = False, options: Options | None = None, keep_alive: float | str | None = None) -> Iterator[Mapping[str, Any]] | None:
        '''
        WARNING: This method is currently broken due to a dependency version update.
        Please use `chat_completion` instead until this is fixed.

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
        # logging
        logger.debug(msg=f"def {self.chat_completion_with_stream.__name__}")
        # functionality
        self.reset_states(retries=retries)
        self.create_prompt(pydantic_model, messages, retries, format=format)

        expanded_chunk = ''

        response = self.ollama_client.chat(
            model=model,
            messages=messages,
            format=format,
            stream=True,
            options=options,
            keep_alive=keep_alive
        )


        for chunk in response:
            expanded_chunk += chunk['message']['content']
            chunk['message']['content'] = expanded_chunk

            yield chunk

        # TODO: start from here with the new logic





"""
        # Start the while loop
        while self.retry_counter >= 0:
            if self.validation_error is not False:
                self.chat_history.append(self.chat_prompt_manager.error_guidance_prompt(validation_error=self.validation_error))
            expanding_response = ""
            try:
                logger.debug("Prepare message and set left retries")
                messages = self.prepare_messages(retries)
                logger.debug("Request ollama client")
                response = self.ollama_client.chat(
                    model=model,
                    messages=messages,
                    format=format,
                    stream=True,
                    options=options,
                    keep_alive=keep_alive
                )
                logger.debug("Process chunks in for-loop")
                for chunk in response:
                    # Ensure chunk is a dictionary
                    if isinstance(chunk, dict) and 'message' in chunk and isinstance(chunk['message'], dict):
                        expanding_response += chunk['message']['content']
                        chunk['message']['content'] = expanding_response
                        rich.print(chunk['message']['content'])

                        # Validation block of chunks
                        chunk: Iterator[Mapping[str, Any]] = self.validation_manager.validate_chat_completion_with_stream(chunk=chunk, pydantic_model=pydantic_model)
                        self.validation_error = self.validation_manager.validate_for_error_message(response=chunk, pydantic_model=pydantic_model)
                        chunk = self.validation_manager.add_error_log_to_final_response(response=chunk, error_message=self.validation_error, raw_message=expanding_response)
                        chunk['retries_left'] = self.retry_counter
                        yield chunk
                    else:
                        print("Unexpected structure in chunk:", chunk)

                # Append chat_history
                if isinstance(chunk, dict) and 'message' in chunk:
                    self.chat_history += [chunk['message']]
                else:
                    print("Unexpected final chunk structure:", chunk)

                # Turn the final response into a str
                if isinstance(chunk, dict) and 'message' in chunk and isinstance(chunk['message'], dict):
                    chunk['message']['content'] = json.dumps(chunk['message']['content'])

                    # Validate the final response
                    if self.validation_error is not False:
                        if self.retry_counter == 0:
                            if allow_partial:
                                try:
                                    chunk = self.validation_manager.validate_partial_model(response=chunk, pydantic_model=pydantic_model)
                                    return chunk
                                except ValidationError as e:
                                    print("Retries exhausted and validation still fails.")
                                    raise e
                            else:
                                try:
                                    chunk = self.validation_manager.validate_chat_completion(response=chunk, pydantic_model=pydantic_model)
                                    return chunk
                                except ValidationError as e:
                                    print("Retries exhausted and validation still fails.")
                                    raise e
                        else:
                            self.retry_counter -= 1
                    else:
                        chunk['message']['content'] = json.loads(chunk['message']['content'])
                        return chunk
            except Exception as e:
                raise e
"""



class OllamaInstructorAsyncClient(BaseOllamaInstructorClient):
    def __init__(self, host: str = 'http://localhost:11434', debug: bool = False):
        super().__init__(host, debug)

    async def async_init(self):
        self.ollama_client = ollama.AsyncClient(host=self.host)
        self.validation_manager = ValidationManager()
        self.chat_prompt_manager = ChatPromptManager()

    async def chat_completion(self, pydantic_model: Type[BaseModel], messages: Sequence[Mapping[str, Any] | Message], model: str, retries: int = 3, format: Literal['', 'json'] = 'json', allow_partial: bool = False, options: Options | None = None, keep_alive: float | str | None = None):
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
        # logging
        logger.debug(msg=f"def {self.chat_completion.__name__}")
        # functionality
        self.reset_states(retries=retries)
        self.create_prompt(pydantic_model, messages, retries, format=format)

        logger.debug("Start while loop")
        while self.validation_error is not False and self.retry_counter > 0:
            self.update_prompt_with_error(format=format)

            try:
                messages = self.prepare_messages(retries)
                response = await self.ollama_client.chat(
                    model=model,
                    messages=messages,
                    format=format,
                    stream=False,
                    options=options,
                    keep_alive=keep_alive
                )
                logger.debug(msg=f"Raw response: {response['message']['content']}")
                try:
                    return self.handle_response(response=response, pydantic_model=pydantic_model, allow_partial=allow_partial, format=format)
                except ValidationError as e:
                    logger.debug(msg=f"ValidationError: {e}")
                    self.retry_counter -= 1

            except Exception as e:
                raise e
