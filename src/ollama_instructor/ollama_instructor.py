from ollama import Client, AsyncClient, Message, Options, ChatResponse
from pydantic import BaseModel, ValidationError
from typing import Type, Mapping, Any, Sequence, Literal
import stamina
import sys
import logging

from ._logging import LoggingMixin

# copied from ollama-python library. See `_types.py` of ollama python package
if sys.version_info < (3, 9):
    from typing import Iterator, AsyncIterator
else:
    from collections.abc import Iterator, AsyncIterator


class OllamaInstructor(Client, LoggingMixin):
    """
    A subclass of the Ollama Client that supports JSON schema validation

    This class adds two key features:
    1. Validates output against a provided Pydantic model schema
    2. Includes retry logic for failed requests

    Methods:
        chat_stream: Stream responses from the LLM with schema validation
        chat_completion: Get a single response from the LLM with schema validation

     Args:
        *args: Arguments to pass to the Ollama Client
        enable_logging: Whether to enable logging
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Logging format string
        **kwargs: Keyword arguments to pass to the Ollama Client
    """
    def __init__(
        self,
        *args,
        enable_logging: bool = False,
        log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO",
        log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(f"ollama_instructor.{self.__class__.__name__}")

        if enable_logging:
            self.setup_logging(level=log_level, format=log_format)

        self.logger.debug("Initialized OllamaInstructor")

    def chat_stream(
        self,
        format: Type[BaseModel],
        model: str,
        messages: Sequence[Mapping[str, Any] | Message] | None = None,
        options: Mapping[str, Any] | Options | None = None,
        keep_alive: float | str | None = None,
        *,
        retries: int = 3
    ) -> Iterator[ChatResponse]:
        self.logger.info(f"Starting chat stream with model: {model}")
        self.logger.debug(f"Using format schema: {format.model_json_schema()}")
        @stamina.retry(on=(ValidationError), attempts=retries, timeout=None)
        def _chat_stream(
            self,
            format: Type[BaseModel],
            model: str,
            messages: Sequence[Mapping[str, Any] | Message] | None = None,
            options: Mapping[str, Any] | Options | None = None,
            keep_alive: float | str | None = None
        ) -> Iterator[ChatResponse]:
            response_iterator = self.chat(
                model=model,
                messages=messages,
                format=format.model_json_schema(),
                stream=True,
                options=options,
                keep_alive=keep_alive
            )
            self.logger.debug("Successfully initiated chat stream")
            expand_content: str = ''
            for chunk_data in response_iterator:
                if chunk_data.message.content is not None:
                    expand_content += chunk_data.message.content
                    print(expand_content)
                    if chunk_data.done:
                        self.logger.info("Stream complete, validating final content")
                        format.model_validate_json(expand_content)
                        self.logger.debug("Content validation successful")
                    #chunk_data.message.content = expand_content
                    yield chunk_data
                else:
                    self.logger.error("Validation failed")
                    raise ValidationError

        return _chat_stream(self, format, model, messages, options, keep_alive)

    def chat_completion(
        self,
        format: Type[BaseModel],
        model: str,
        messages: Sequence[Mapping[str, Any] | Message] | None = None,
        options: Mapping[str, Any] | Options | None = None,
        keep_alive: float | str | None = None,
        *,
        retries: int = 3
    ) -> ChatResponse | None:
        self.logger.info(f"Starting chat completion with model: {model}")
        @stamina.retry(on=(ValidationError), attempts=retries, timeout=None)
        def _chat_completion(
            self,
            format: Type[BaseModel],
            model: str,
            messages: Sequence[Mapping[str, Any] | Message] | None = None,
            options: Mapping[str, Any] | Options | None = None,
            keep_alive: float | str | None = None
        ) -> ChatResponse:
            response = self.chat(
                model=model,
                messages=messages,
                format=format.model_json_schema(),
                stream=False,
                options=options,
                keep_alive=keep_alive
            )
            self.logger.debug("Successfully initiated chat completion")
            if response.message.content is not None:
                format.model_validate_json(response.message.content)
                self.logger.debug("Content validation successful")
                return response
            else:
                self.logger.error("Validation failed")
                raise ValidationError

        return _chat_completion(self, format, model, messages, options, keep_alive)


class OllamaInstructorAsync(AsyncClient, LoggingMixin):
    """
    A subclass of the Ollama AsyncClient that supports JSON schema validation

    This class adds two key features:
    1. Validates output against a provided Pydantic model schema
    2. Includes retry logic for failed requests

    Methods:
        chat_stream: Stream responses from the LLM with schema validation
        chat_completion: Get a single response from the LLM with schema validation

    Args:
        *args: Arguments to pass to the Ollama AsyncClient
        enable_logging: Whether to enable logging
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Logging format string
        **kwargs: Keyword arguments to pass to the Ollama AsyncClient
    """
    def __init__(
        self,
        *args,
        enable_logging: bool = False,
        log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO",
        log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(f"ollama_instructor.{self.__class__.__name__}")

        if enable_logging:
            self.setup_logging(level=log_level, format=log_format)

        self.logger.debug("Initialized OllamaInstructorAsync")

    async def chat_stream(
        self,
        format: Type[BaseModel],
        model: str,
        messages: Sequence[Mapping[str, Any] | Message] | None = None,
        options: Mapping[str, Any] | Options | None = None,
        keep_alive: float | str | None = None,
        *,
        retries: int = 3
    ) -> AsyncIterator[ChatResponse]:
        self.logger.info(f"Starting async chat stream with model: {model}")
        self.logger.debug(f"Using format schema: {format.model_json_schema()}")
        @stamina.retry(on=(ValidationError), attempts=retries, timeout=None)
        async def _chat_stream(
            self,
            format: Type[BaseModel],
            model: str,
            messages: Sequence[Mapping[str, Any] | Message] | None = None,
            options: Mapping[str, Any] | Options | None = None,
            keep_alive: float | str | None = None
        ) -> AsyncIterator[ChatResponse]:
            response_iterator = await self.chat(
                model=model,
                messages=messages,
                format=format.model_json_schema(),
                stream=True,
                options=options,
                keep_alive=keep_alive
            )
            self.logger.debug("Successfully initiated async chat stream")
            expand_content: str = ''
            async for chunk_data in response_iterator:
                if chunk_data.message.content is not None:
                    expand_content += chunk_data.message.content
                    if chunk_data.done:
                        self.logger.info("Stream complete, validating final content")
                        format.model_validate_json(expand_content)
                        self.logger.debug("Content validation successful")
                    #chunk_data.message.content = expand_content
                    yield chunk_data
                else:
                    self.logger.error("Validation failed")
                    raise ValidationError

        return _chat_stream(self, format, model, messages, options, keep_alive)

    async def chat_completion(
        self,
        format: Type[BaseModel],
        model: str,
        messages: Sequence[Mapping[str, Any] | Message] | None = None,
        options: Mapping[str, Any] | Options | None = None,
        keep_alive: float | str | None = None,
        *,
        retries: int = 3
    ) -> ChatResponse:
        self.logger.info(f"Starting chat completion with model: {model}")
        @stamina.retry(on=(ValidationError), attempts=retries, timeout=None)
        async def _chat_completion(
            self,
            format: Type[BaseModel],
            model: str,
            messages: Sequence[Mapping[str, Any] | Message] | None = None,
            options: Mapping[str, Any] | Options | None = None,
            keep_alive: float | str | None = None
        ) -> ChatResponse:
            response = await self.chat(
                model=model,
                messages=messages,
                format=format.model_json_schema(),
                stream=False,
                options=options,
                keep_alive=keep_alive
            )
            self.logger.debug("Successfully initiated chat completion")
            if response.message.content is not None:
                format.model_validate_json(response.message.content)
                self.logger.debug("Content validation successful")
                return response
            else:
                self.logger.error("Validation failed")
                raise ValidationError

        return await _chat_completion(self, format, model, messages, options, keep_alive)
