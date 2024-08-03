import pytest
from pydantic import BaseModel, ValidationError, ConfigDict
from enum import Enum
from typing import List
from ollama_instructor.ollama_instructor_client import OllamaInstructorClient

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

@pytest.fixture
def client():
    return OllamaInstructorClient(host='http://localhost:11434')

def test_handle_response_valid_json(client):
    client.retry_counter = 1
    response = {
        'message': {
            'content': '{"name": "John", "age": 30, "gender": "male", "friends": ["Nick", "Gabriel"]}'
        }
    }

    result = client.handle_response(
        response=response,
        pydantic_model=Person,
        allow_partial=False,
        format='json'
    )

    content = result['message']['content']
    assert content['name'] == 'John'
    assert content['age'] == 30
    assert content['gender'] == Gender.MALE.value
    assert 'Nick' in content['friends']
    assert 'Gabriel' in content['friends']

def test_handle_response_invalid_json(client):
    client.retry_counter = 1
    response = {
        'message': {
            'content': '{"name": "John", "age": "thirty", "gender": "male", "friends": ["Nick", "Gabriel"]}'
        }
    }

    with pytest.raises(ValidationError):
        client.handle_response(
            response=response,
            pydantic_model=Person,
            allow_partial=False,
            format='json'
        )

def test_handle_response_partial_json_allow_partial(client):
    client.retry_counter = 1
    response = {
        'message': {
            'content': '{"name": "John", "age": 30}'
        }
    }

    result = client.handle_response(
        response=response,
        pydantic_model=Person,
        allow_partial=True,
        format='json'
    )

    content = result['message']['content']
    assert content['name'] == 'John'
    assert content['age'] == 30
    assert 'gender' not in content
    assert 'friends' not in content

def test_handle_response_partial_json_disallow_partial(client):
    client.retry_counter = 1
    response = {
        'message': {
            'content': '{"name": "John", "age": 30}'
        }
    }

    with pytest.raises(ValidationError):
        client.handle_response(
            response=response,
            pydantic_model=Person,
            allow_partial=False,
            format='json'
        )

def test_handle_response_with_comments(client):
    client.retry_counter = 1
    response = {
        'message': {
            'content': '''
            Here is a JSON code block with comments:
            ```json
            {
                "name": "John", // This is a comment
                "age": 30, /* Multi-line
                comment */
                "gender": "male", # Another comment
                "friends": ["Nick", "Gabriel"] % Comment
            }
            ```
            '''
        }
    }

    result = client.handle_response(
        response=response,
        pydantic_model=Person,
        allow_partial=False,
        format=''
    )

    content = result['message']['content']
    assert content['name'] == 'John'
    assert content['age'] == 30
    assert content['gender'] == Gender.MALE.value
    assert 'Nick' in content['friends']
    assert 'Gabriel' in content['friends']

# pytest test_response_handling.py
