from pydantic import BaseModel, ValidationError
from typing import Dict, Any, Type
import json
from fastapi.encoders import jsonable_encoder
from partial_json_parser import loads
from partial_json_parser.core.options import STR, OBJ
from promptools import extractors
from icecream import ic

from .cleaner import clean_nested_data_with_error_dict, create_partial_model

class ValidationManager:
    '''
    The `ValidationManager` class provides several functions to make sure the responses of LLMs are validated against a given Pydantic model.
    '''            

    ####################
    # HELPER FUNCTION
    ####################
    def add_error_log_to_final_response(
        self,
        response: Dict[str, Any],
        error_message: ValidationError,
        raw_message: Dict[str, Any]
    ) -> Dict[str, Any]:
        '''
        This adds the error message to the final response, with the final validation.

        Args:
            response: the response from the final validation
            error_message: the error message from the first validation
            raw_message: the original message

        Returns:
            the updated response with the error message and the raw message added
        '''
        raw_message = {
            'role': 'assistant',
            'content': json.dumps(raw_message)
        }
        response['raw_message'] = raw_message 
        if error_message is True:
            ic()
            response['validation_error'] = None
            return response
        else:
            ic()
            response['validation_error'] = str(error_message)
            return response

    ####################
    # VALIDATION FUNCTIONS
    ####################
    def validate_for_error_message(
        self,
        response: Dict[str, Any],
        pydantic_model: Type[BaseModel],
    ) -> bool | Type[ValidationError]:
        '''
        This validates the final response from a chat completion (with or without streaming).

        Args:
            response: the final response of the chat completion function
            pydantic_model: the pydantic model for validate the final response

        Returns:
            `True` or `ValidationError`
        '''
        data = json.dumps(response['message']['content'])
        parsed_chunk_dict = json.loads(data)
        ic()
        try:
            if pydantic_model.model_validate(obj=parsed_chunk_dict):
                ic(True)
                return True
        except ValidationError as e:
            ic()
            return e.errors(include_url=False)
    
    def validate_partial_model(
        self,
        response: Dict[str, Any],
        pydantic_model: Type[BaseModel]
    ) -> Dict[str, Any]:
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
        data = response['message']['content']
        parsed_chunk_dict = json.loads(data)
        partial_model = create_partial_model(pydantic_model=pydantic_model)
        ic()
        try:
            #cleaned_data = self.clean_data(data=parsed_chunk_dict, model=partial_model)
            cleaned_data = clean_nested_data_with_error_dict(data=parsed_chunk_dict, pydantic_model=partial_model)
            ic()
            response['message']['content'] = jsonable_encoder(cleaned_data)
            return response
        except ValidationError as e:
            ic()
            raise e
        
    ####################
    # VALIDATION OF CHAT COMPLETION
    ####################
    def validate_chat_completion(
        self,
        response: Dict[str, Any],
        pydantic_model: Type[BaseModel],
    ) -> Dict[str, Any]:
        """
        Validates the response from a chat completion request, ensuring the content is valid according to the provided Pydantic model.
        
        Args:
            response (Dict[str, Any]): The response dictionary from the chat completion request.
            pydantic_model (Type[BaseModel]): The Pydantic model to validate the response against.
        
        Returns:
            Dict[str, Any]: The validated response dictionary, with the content field updated to match the Pydantic model.
        """
        data = response['message']['content']
        parsed_chunk_dict = json.loads(data)
        try:
            valid_data = pydantic_model.model_validate(parsed_chunk_dict)
            ic()
            valid_data.model_dump(exclude_unset=True)
            response['message']['content'] = valid_data
            return response
        except ValidationError as e:
            ic()
            raise e

    ####################
    # VALIDATION OF STREAMS
    ####################
    def validate_chat_completion_with_stream(self, chunk: Dict[str, Any], pydantic_model: Type[BaseModel]) -> Dict[str, Any]:
        ic()
        data = chunk['message']['content']
        fallback_data = {}
        partial_pydantic_model = create_partial_model(pydantic_model=pydantic_model)
        try:
            parsed_chunk = loads(json_string=data, allow_partial=OBJ)
            ic()
            valid_data = extractors.extract_json(text=data, expect=pydantic_model, fallback=partial_pydantic_model(**parsed_chunk).model_dump(), allow_partial=STR | OBJ)
            ic()
            chunk['message']['content'] = jsonable_encoder(valid_data)
        except ValidationError as e:
            ic()
            print('ValidationError', e)
            parsed_chunk = loads(json_string=data, allow_partial=OBJ)
            valid_data = extractors.extract_json(text=data, expect=pydantic_model, fallback=partial_pydantic_model(**fallback_data).model_dump(), allow_partial=OBJ)
            chunk['message']['content'] = jsonable_encoder(valid_data) #custom_encoder=Dict[Any, Any]
            chunk['message']['validation_error'] = str(e.errors(include_url=False))
        except Exception as e:
            ic()
            print('Exception', e)
            parsed_chunk = loads(json_string=data, allow_partial=OBJ)
            chunk['message']['content'] = jsonable_encoder(parsed_chunk)
            chunk['message']['validation_error'] = str(e)
        return chunk
