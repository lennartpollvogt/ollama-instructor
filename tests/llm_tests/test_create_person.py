from pydantic import BaseModel
from enum import Enum
from typing import List

from ollama_instructor.ollama_instructor_client import OllamaInstructorClient

class Gender(Enum):
    MALE = 'male'
    FEMALE = 'female'

class Person(BaseModel):
    '''
    This model defines a person.
    '''
    name: str
    age: int
    gender: Gender
    friends: List[str] = []

    class Config: 
        extra = 'forbid' # This will prevent the response to contain additional and not specified properties. Otherwise the response would only be validated if it fits the JSON schema of the pydantic model


def test_create_person(host: str, model: str, **kwargs):
    client = OllamaInstructorClient(
        host=host,
    )
    response = client.chat_completion(
        model=model,
        pydantic_model=Person,
        messages=[
            {
                'role': 'user',
                'content': 'Jason is 25 years old. Jason loves to play soccer with his friends Nick and Gabriel. His favorite food is pizza.'
            }
        ],
        **kwargs
    )
    return response


def test_stream_create_person(host: str, model: str, **kwargs):
    client = OllamaInstructorClient(
        host=host,
    )
    response = client.chat_completion_with_stream(
        model=model,
        pydantic_model=Person,
        messages=[
            {
                'role': 'user',
                'content': 'Jason is 25 years old. Jason loves to play soccer with his friends Nick and Gabriel. His favorite food is pizza.'
            }
        ],
        **kwargs
    )
    
    for chunk in response:
        yield chunk