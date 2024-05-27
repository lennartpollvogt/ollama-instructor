'''
Create tests for the functions in cleaner.py
'''

# TODO: test for the functions in cleaner.py

from pydantic import BaseModel, Field, ConfigDict, ValidationError, field_validator
from enum import Enum
import json
from typing import List, Optional, Type, Any, Dict
import rich
from icecream import ic


def extract_defaults_from_schema_for_none(data: Dict[str, Any], pydantic_model: Type[BaseModel]) -> Dict[str, Any]:
    '''
    This function takes the data and looks for "None" values within the data.
    With the help of the JSON schema of the Pydantic model, it will figure out the default values for the "None" fields.

    Args:
        data (Any): The data to be validated.
        pydantic_model (Type[BaseModel]): The Pydantic model.

    Returns:
        Dict[str, Any]: data with the default values for the "None" fields.
    '''
    # Get the JSON schema from the Pydantic model
    schema = pydantic_model.model_json_schema()
    definitions = schema.get('$defs', {})

    def resolve_ref(ref: str) -> Dict[str, Any]:
        ref = ref.split('/')[-1]
        return definitions.get(ref, {})

    def replace_none_with_defaults(data: Any, schema: Dict[str, Any]) -> Any:
        if isinstance(data, dict):
            for key, value in data.items():
                if value is None:
                    if 'properties' in schema and key in schema['properties']:
                        prop_schema = schema['properties'][key]
                        if '$ref' in prop_schema:
                            prop_schema = resolve_ref(prop_schema['$ref'])
                        default = prop_schema.get('default')
                        if default is not None:
                            data[key] = default
                    else:
                        continue
                elif isinstance(value, dict):
                    if 'properties' in schema and key in schema['properties']:
                        prop_schema = schema['properties'][key]
                        if '$ref' in prop_schema:
                            prop_schema = resolve_ref(prop_schema['$ref'])
                        data[key] = replace_none_with_defaults(value, prop_schema)
                elif isinstance(value, list):
                    if 'properties' in schema and key in schema['properties']:
                        prop_schema = schema['properties'][key]
                        if 'items' in prop_schema:
                            item_schema = prop_schema['items']
                            if '$ref' in item_schema:
                                item_schema = resolve_ref(item_schema['$ref'])
                            data[key] = [replace_none_with_defaults(item, item_schema) for item in value]
        elif isinstance(data, list):
            if 'items' in schema:
                item_schema = schema['items']
                if '$ref' in item_schema:
                    item_schema = resolve_ref(item_schema['$ref'])
                for index, item in enumerate(data):
                    data[index] = replace_none_with_defaults(item, item_schema)
        return data

    return replace_none_with_defaults(data, schema)
    

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

            # Iterate over each error and handle it
            for item in error_dict:
                loc = item['loc']
                error_type = item['type']
                set_nested_value(data, loc, error_type)
            try:
                valid_data = pydantic_model.model_validate(data)
                ic()
                return valid_data
            except ValidationError as e:
                ic(data)
                return data
                
    except Exception as e:
        raise e

class Role(Enum):
    WIFE = 'wife'
    HUSBAND = 'husband'
    CHILD = 'child'

class Gender(Enum):
    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'

class Address(BaseModel):
    street: Optional[str] = Field(None, title='Street address')
    city: Optional[str] = Field(None, title='City')
    state: Optional[str] = Field(None, title='State')

class Person(BaseModel):
    '''
    This schema describes a person.
    '''
    name: str = Field(..., description='The name of the person')
    age: int = Field(..., description='The age of the person')
    gender: Gender = Field(default='other')
    role: Role
    address: Optional[Address] = None

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'name': 'John Doe',
                    'age': 55,
                    'gender': 'male',
                    'role': 'husband',
                    'address': {
                        'street': '123 Main Street',
                        'city': 'Anytown',
                        'state': 'CA'
                    }
                }
            ]
        }
    )

    @field_validator('gender', mode='before')
    @classmethod
    def validate_gender(cls, value):
        return value if value is not None else 'other'

class ListOfPerson(BaseModel):
    description_of_relationship: str = Field(default='Missing description')
    persons: List[Person]

example_data = {
    "description_of_relationship": None,
    "persons": [
        {
            "name": "John Doe",
            "age": 55,
            "gender": "mother",
            "role": "husband",
            'address': {
                "street": "123 Main Street",
                "city": "Anytown",
                "state": 7645
            }
        },
        {
            "name": "Jane Doe",
            "age": 48,
            "gender": "female",
            "role": "wife",
            'address': {
                "street": "123 Main Street",
                "city": "Anytown",
                "state": "CA"
            }
        },
        {
            "name": "Jimmy Doe",
            "age": 12,
            "gender": None,
            "role": "child",
            'address': {
                "street": "123 Main Street",
                "city": "Anytown",
                "state": "CA"
            }
        },
    ]
}

rich.print(ListOfPerson.model_json_schema())

cleaned_data = clean_nested_data_with_error_dict(data=example_data, pydantic_model=ListOfPerson)
defaulted_data = extract_defaults_from_schema_for_none(data=cleaned_data, pydantic_model=ListOfPerson)
rich.print(cleaned_data)
print('----------')
rich.print(defaulted_data)
