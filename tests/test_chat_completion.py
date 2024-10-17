import pytest
from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import List

from ollama_instructor.ollama_instructor_client import OllamaInstructorAsyncClient, OllamaInstructorClient

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

# ASYNCHRONOUS
@pytest.mark.asyncio
async def test_chat_completion_async():
    client = OllamaInstructorAsyncClient(
        host='http://localhost:11434',
        debug=False
    )
    await client.async_init()

    response = await client.chat_completion(
        model='phi3.5:latest',
        pydantic_model=Person,
        messages=messages
    )

    content: dict = response['message']['content']
    assert 'name' in content
    assert content['name'] == 'Jason'
    assert content['age'] == 25
    assert content['gender'] == Gender.MALE.value
    assert 'Nick' in content['friends']
    assert 'Gabriel' in content['friends']

    expected_keys = {'name', 'age', 'gender', 'friends'}
    assert set(content.keys()) == expected_keys


# SYNCHRONOUS
def test_chat_completion():
    client = OllamaInstructorClient(
        host='http://localhost:11434',
        debug=False
    )

    response = client.chat_completion(
        model='phi3.5:latest',
        pydantic_model=Person,
        messages=messages
    )

    content: dict = response['message']['content']
    assert 'name' in content
    assert content['name'] == 'Jason'
    assert content['age'] == 25
    assert content['gender'] == Gender.MALE.value
    assert 'Nick' in content['friends']
    assert 'Gabriel' in content['friends']

    expected_keys = {'name', 'age', 'gender', 'friends'}
    assert set(content.keys()) == expected_keys

# pytest test_chat_completion.py

# pytest test_chat_completion.py::test_chat_completion_async
# pytest test_chat_completion.py::test_chat_completion
