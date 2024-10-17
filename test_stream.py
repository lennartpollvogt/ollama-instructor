from ollama_instructor.ollama_instructor_client import OllamaInstructorClient
from pydantic import BaseModel, ConfigDict
from typing import List
from enum import Enum

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

    model_config = ConfigDict(
        extra='forbid'
    )

client = OllamaInstructorClient(debug=True)
response = client.chat_completion_with_stream(
    #model='tinyllama:latest',
    model='qwen2.5:3b',
    pydantic_model=Person,
    messages=[
        {
            'role': 'user',
            'content': 'Jason is 25 years old. Jason loves to play soccer with his friends Nick and Gabriel. His favorite food is pizza.'
        }
    ],
    retries=2
)

for chunk in response:
    print(chunk['message']['content'])
