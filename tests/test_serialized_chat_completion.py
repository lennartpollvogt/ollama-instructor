'''
This test series is for testing serializing requests to the ollama chat 
endpoint using ollama-instructor.

In version 0.4.1 the chat_history, validation_error und retries of the clients
(OllamaInstructorClient & OllamaInstructorAsyncClient) where not resetted if 
you would use the same client instance. 
This was causing error of "TypeError: 'NoneType' object is not subscriptable"
'''
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

    model_config = ConfigDict(
        extra='forbid'
    )

list_of_text = [
    "Jason is a young man (25)",
    "Jane is a young lady of 18 years.",
    "Bob is an old man of 85 years, living in Chicago."
]

# ASYNCHRONOUS
@pytest.mark.asyncio
async def test_serializing_request_async():
    client = OllamaInstructorAsyncClient(
        host='http://localhost:11434',
        debug=False
    )
    await client.async_init()

    list_of_responses = []
    for text in list_of_text:
        response = await client.chat_completion(
            pydantic_model=Person,
            model='llama3.1:latest',
            messages=[
                {
                    'role': 'user',
                    'content': text
                }
            ],
        )
        list_of_responses.append(response['message']['content'])

    assert len(list_of_responses) == 3
    for response in list_of_responses:
        assert isinstance(response, dict)
        assert set(response.keys()) == {'name', 'age', 'gender'}
        assert isinstance(response['name'], str)
        assert isinstance(response['age'], int)
        assert response['gender'] in [Gender.MALE.value, Gender.FEMALE.value]

# SYNCHRONOUS
def test_serializing_request():
    client = OllamaInstructorClient(
        host='http://localhost:11434',
        debug=False
    )

    list_of_responses = []
    for text in list_of_text:
        response = client.chat_completion(
            pydantic_model=Person,
            model='llama3.1:latest',
            messages=[
                {
                    'role': 'user',
                    'content': text
                }
            ],
        )
        list_of_responses.append(response['message']['content'])

    assert len(list_of_responses) == 3
    for response in list_of_responses:
        assert isinstance(response, dict)
        assert set(response.keys()) == {'name', 'age', 'gender'}
        assert isinstance(response['name'], str)
        assert isinstance(response['age'], int)
        assert response['gender'] in [Gender.MALE.value, Gender.FEMALE.value]
    


# pytest test_serialized_chat_completion.py

'''
Expected output:
[{'name': 'Jason', 'age': 25, 'gender': 'male'}, {'name': 'Jane', 'age': 18, 'gender': 'female'}, {'name': 'Bob', 'age': 85, 'gender': 'male'}]
'''