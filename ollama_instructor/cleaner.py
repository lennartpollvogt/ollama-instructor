from typing import Type, Dict, Any, Tuple, Optional
from pydantic import BaseModel, ValidationError, create_model
from pydantic.fields import FieldInfo
from copy import deepcopy
import json

from icecream import ic

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
    ic()
    def make_field_optional(field: FieldInfo, default: Any = None) -> Tuple[Any, FieldInfo]:
        ic()
        new = deepcopy(field)
        new.default = default
        new.annotation = Optional[field.annotation] # type: ignore
        return new.annotation, new
    return create_model(
        f'Partial{pydantic_model.__name__}',
        __base__=pydantic_model,
        __module__=pydantic_model.__module__,
        **{
            field_name: make_field_optional(field=field_info)
            for field_name, field_info in pydantic_model.model_fields.items()
        }
    )

def clean_nested_data_with_error_dict(data: Any, pydantic_model: Type[BaseModel]) -> Dict[str, Any]:
    '''
    This function takes the LLM response (data), validates it against the Pydantic model, trys to clean the data and returns the cleaned data.

    This works best with a partial model, as the unvalid data will be removed or set to None.
    To make the Pydantic model partial use the function `partial_model` of the `ValidationManager` class.

    Args:
       data (Any): The data that should be validated or cleaned.
       pydantic_model (Type[BaseModel]): The Pydantic model that should be used for validation.

    Returns:
        Dict[str, Any]: A dictionary with the cleaned data.
    '''
    if isinstance(data, str):
        data = json.loads(data)
    
    try:
        try:
            # Parse the data through the Pydantic model, which validates and constructs a model instance
            model_instance = pydantic_model.model_validate(data)
            ic()
            # Convert the validated model instance back to a dictionary, excluding any undefined model fields
            cleaned_data = model_instance.model_dump(exclude_unset=True)
            ic()
            return cleaned_data
        except ValidationError as e:
            error_dict = e.errors(include_url=False)
            ic()
            # Recursive function to navigate through the nested data structure and set values to None or remove them
            def set_nested_value(data: Any, loc: tuple, error_type: str):
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
            ic()
            # Iterate over each error and handle it
            for item in error_dict:
                loc = item['loc']
                error_type = item['type']
                set_nested_value(data, loc, error_type)
            ic()
            return data
    except Exception as e:
        ic()
        raise e
    