import pytest
from ollama_instructor.ollama_instructor_client import OllamaInstructorClient
from pydantic import BaseModel, ConfigDict
import json
from enum import Enum
from typing import List

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

messages = [
    {
        'role': 'user',
        'content': 'Jason is 25 years old. Jason loves to play soccer with his friends Nick and Gabriel. His favorite food is pizza.'
    }
]

def test_chat_completion():
    client = OllamaInstructorClient(
        host='http://localhost:11434',
        debug=False
    )

    # Capture streamed chunks into a list
    expand_response: dict = {}
    response = client.chat_completion_with_stream(
        model='qwen2.5:3b',
        pydantic_model=Person,
        messages=messages,
        retries=2
    )

    for chunk in response:
        if 'message' in chunk and 'content' in chunk['message']:
            expand_response = chunk['message']['content']

    # Assert the expected values
    assert 'name' in expand_response
    assert expand_response['name'] == 'Jason'
    assert expand_response['age'] == 25
    assert expand_response['gender'] in Gender
    assert 'Nick' in expand_response['friends']
    assert 'Gabriel' in expand_response['friends']

    expected_keys = {'name', 'age', 'gender', 'friends'}
    assert set(expand_response.keys()) == expected_keys

# pytest test_chat_completion_with_stream.py
