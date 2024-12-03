from pydantic import BaseModel, ValidationError
from typing import Any, Type, Mapping, Iterator, List
import json
from fastapi.encoders import jsonable_encoder
from partial_json_parser import loads
#from partial_json_parser.options import STR, OBJ # activate during development of ollama-instructor
from partial_json_parser.core.options import STR, OBJ # deactivate during development of ollama-instructor but activate before uploading to PyPI
from promptools import extractors
from pydantic_core import ErrorDetails

from .cleaner import clean_nested_data_with_error_dict, create_partial_model
from .log_config import logger


class ValidationManager:
    '''
    The `ValidationManager` class provides several functions to make sure the responses of LLMs are validated against a given Pydantic model.
    '''

    ####################
    # HELPER FUNCTION
    ####################
    def add_error_log_to_final_response(
        self,
        response: Mapping[str, Any],
        error_message: bool | None | List[ErrorDetails],
        raw_message: str | dict
    ) -> Mapping[str, Any]:
        '''
        This adds the error message to the final response, with the final validation.

        Args:
            response: the response from the final validation
            error_message: the error message from the first validation
            raw_message: the original message

        Returns:
            the updated response with the error message and the raw message added
        '''
        # logging
        logger.debug(msg=f"def {self.add_error_log_to_final_response.__name__}")
        # functionality
        new_response = dict(response)
        if raw_message is isinstance(raw_message, dict):
            raw_message = json.dumps(raw_message)
        raw_message = {
            'role': 'assistant',
            #'content': json.dumps(raw_message)
            'content': str(raw_message)
        }
        new_response['raw_message'] = raw_message
        if error_message is True:
            new_response['validation_error'] = str(None)
            return new_response
        else:
            new_response['validation_error'] = str(error_message)
            return new_response

    ####################
    # VALIDATION FUNCTIONS
    ####################
    def validate_for_error_message(
        self,
        response: Mapping[str, Any],
        pydantic_model: Type[BaseModel],
    )-> bool | None | List[ErrorDetails]:
        '''
        This validates the final response from a chat completion (with or without streaming).

        Args:
            response: the final response of the chat completion function
            pydantic_model: the pydantic model for validate the final response

        Returns:
            `False` or `ValidationError`
        '''
        # logging
        logger.debug(msg=f"def {self.validate_for_error_message.__name__}")
        # functionality
        try:
            data = response['message']['content']
            if isinstance(data, str):
                parsed_chunk_dict = json.loads(data)
            else:
                parsed_chunk_dict = data

            pydantic_model.model_validate(obj=parsed_chunk_dict)
            return False
        except ValidationError as e:
            return e.errors(include_url=False)

    def validate_partial_model(
        self,
        response: Mapping[str, Any] | Iterator[Mapping[str, Any]],
        pydantic_model: Type[BaseModel]
    ) -> Mapping[str, Any] | Iterator[Mapping[str, Any]]:
        '''
        This function will take the Pydantic model and parse it into a partial model.
        Then the final response will be compared with the partial model and gets cleaned when still some `ValidationError` occur.
        The response is a cleand version of the final response.

        To use this function the argument `allow_partial` must be set to `True`.

        Args:
            response: the final response of the chat completion function
            pydantic_model: the pydantic model to be used to create the partial model

        Returns:
            Dict[str, Any]: the cleand version of the final response
        '''
        # logging
        logger.debug(msg=f"def {self.validate_partial_model.__name__}")
        # functionality
        data = response['message']['content']
        #parsed_chunk_dict = json.loads(data)
        parsed_chunk_dict = data
        partial_model = create_partial_model(pydantic_model=pydantic_model)
        try:
            #cleaned_data = self.clean_data(data=parsed_chunk_dict, model=partial_model)
            cleaned_data = clean_nested_data_with_error_dict(data=parsed_chunk_dict, pydantic_model=partial_model)
            response['message']['content'] = jsonable_encoder(cleaned_data)
            return response
        except ValidationError as e:
            raise e

    ####################
    # VALIDATION OF CHAT COMPLETION
    ####################
    def validate_chat_completion(
        self,
        response: Mapping[str, Any],
        pydantic_model: Type[BaseModel],
    ) -> Mapping[str, Any]:
        """
        Validates the response from a chat completion request, ensuring the content is valid according to the provided Pydantic model.

        Args:
            response (Dict[str, Any]): The response dictionary from the chat completion request.
            pydantic_model (Type[BaseModel]): The Pydantic model to validate the response against.

        Returns:
            Dict[str, Any]: The validated response dictionary, with the content field updated to match the Pydantic model.
        """
        # logging
        logger.debug(msg=f"def {self.validate_chat_completion.__name__}")
        # functionality
        data = response['message']['content']
        #parsed_chunk_dict = json.loads(data)
        parsed_chunk_dict = data
        try:
            valid_data = pydantic_model.model_validate(parsed_chunk_dict)
            valid_data.model_dump(exclude_unset=True)
            response['message']['content'] = json.dumps(valid_data)
            return response
        except ValidationError as e:
            raise e

    ####################
    # VALIDATION OF STREAMS
    ####################
    def validate_chat_completion_with_stream(self, chunk: Iterator[Mapping[str, Any]], pydantic_model: Type[BaseModel]) -> Iterator[Mapping[str, Any]]:
        # logging
        logger.debug(msg=f"def {self.validate_chat_completion_with_stream.__name__}")
        # functionality
        data = chunk['message']['content']
        fallback_data = {}
        partial_pydantic_model = create_partial_model(pydantic_model=pydantic_model)
        try:
            parsed_chunk = loads(json_string=data, allow_partial=OBJ)
            valid_data = extractors.extract_json(text=data, expect=pydantic_model, fallback=partial_pydantic_model(**parsed_chunk).model_dump(), allow_partial=STR | OBJ)
            chunk['message']['content'] = jsonable_encoder(valid_data)
        except ValidationError as e:
            print('ValidationError', e)
            parsed_chunk = loads(json_string=data, allow_partial=OBJ)
            valid_data = extractors.extract_json(text=data, expect=pydantic_model, fallback=partial_pydantic_model(**fallback_data).model_dump(), allow_partial=OBJ)
            chunk['message']['content'] = jsonable_encoder(valid_data) #custom_encoder=Dict[Any, Any]
            chunk['validation_error'] = str(e.errors(include_url=False))
        except Exception as e:
            print('Exception', e)
            parsed_chunk = loads(json_string=data, allow_partial=OBJ)
            chunk['message']['content'] = jsonable_encoder(parsed_chunk)
            chunk['validation_error'] = str(e)
        return chunk
