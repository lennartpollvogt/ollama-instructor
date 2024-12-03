# cleaner.py

from typing import Type, Dict, Any, Tuple, Optional
from pydantic import BaseModel, ValidationError, create_model
from pydantic.fields import FieldInfo
from copy import deepcopy
import json

from .log_config import logger


'''
NOTE:
The function "create_partial_model" in the following was created with the research and help of Phind-70b from www.phind.com.
The research of the Phind system discovered concepts from different sources. A first draft of the function was created by Phind-70b.
The function was then improved by iterating over the use cases in collaboration with Phind-70b.

For transparency reasons I want to provide the sources:
- https://github.com/samuelcolvin/pydantic/issues/1673
- https://stackoverflow.com/questions/64045012/pydantic-input-model-for-partial-updates
- https://docs.pydantic.dev/latest/concepts/models/
- https://towardsdatascience.com/write-dry-data-models-with-partials-and-pydantic-b0b13d0eeb3a
- https://docs.pydantic.dev/1.10/usage/types/
- https://www.getorchestra.io/guides/pydantic-partial-update-models-in-fastapi-a-tutorial
- https://fastapi.tiangolo.com/tutorial/response-model/
- https://github.com/team23/pydantic-partial
- https://fastapi.tiangolo.com/tutorial/body-updates/
'''


def create_partial_model(pydantic_model: Type[BaseModel]) -> Type[BaseModel]:
    '''
    Creates a partial Pydantic model that accepts missing fields.
    This is useful when validating streams of JSON data.
    Otherwise, Pydantic would raise an error if a field is missing or JSON is malformed.

    Args:
        model (Type[BaseModel]): The Pydantic model.

    Returns:
        Type[BaseModel]: The partial Pydantic model which now accepts missing fields.
    '''
    # logging
    logger.debug(msg=f"def {create_partial_model.__name__}")
    # functionality
    def make_field_optional(field: FieldInfo) -> Tuple[Type, FieldInfo]:
        new = deepcopy(field)
        new.default = None
        # Make the type Optional
        new_type = Optional[field.annotation] if field.annotation else Any
        return new_type, new

    fields = {
        field_name: make_field_optional(field_info)
        for field_name, field_info in pydantic_model.model_fields.items()
    }

    created_model = create_model(
        f'Partial{pydantic_model.__name__}',
        __base__=pydantic_model,
        **fields
    )

    return created_model

def clean_nested_data_with_error_dict(data: Any, pydantic_model: Type[BaseModel]) -> Dict[str, Any]:
    '''
    This function takes the LLM response (data), validates it against the Pydantic model, trys to clean the data and returns the cleaned data.

    This works best with a partial model, as the unvalid data will be removed or set to None.
    To make the Pydantic model partial use the function `create_partial_model` of cleaner.py file.

    Args:
       data (Any): The data that should be validated or cleaned.
       pydantic_model (Type[BaseModel]): The Pydantic model that should be used for validation.

    Returns:
        Dict[str, Any]: A dictionary with the cleaned data.
    '''
    # logging
    logger.debug(msg=f"def {clean_nested_data_with_error_dict.__name__}")
    # functionality
    if isinstance(data, str):
        data = json.loads(data)

    try:
        try:
            # Parse the data through the Pydantic model, which validates and constructs a model instance
            model_instance = pydantic_model.model_validate(data)
            # Convert the validated model instance back to a dictionary, excluding any undefined model fields
            cleaned_data = model_instance.model_dump(exclude_unset=True)
            return cleaned_data
        except ValidationError as e:
            error_dict = e.errors(include_url=False)
            # Recursive function to navigate through the nested data structure and set values to None or remove them
            def set_nested_value(data: Any, loc: tuple, error_type: str):
                # logging
                logger.debug(msg=f"def {set_nested_value.__name__}")
                # functionality
                for key in loc[:-1]:
                    if isinstance(data, dict):
                        data = data[key]
                    elif isinstance(data, list):
                        data = data[int(key)]
                if error_type == 'extra_forbidden':
                    if isinstance(data, dict):
                        del data[loc[-1]]
                    elif isinstance(data, list):
                        del data[int(loc[-1])]
                else:
                    if isinstance(data, dict):
                        data[loc[-1]] = None
                    elif isinstance(data, list):
                        data[int(loc[-1])] = None
            # Iterate over each error and handle it
            for item in error_dict:
                loc = item['loc']
                error_type = item['type']
                set_nested_value(data, loc, error_type)
            return data
    except Exception as e:
        raise e
