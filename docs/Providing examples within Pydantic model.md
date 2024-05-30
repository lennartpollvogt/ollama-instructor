


```Python
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
import rich
from typing import List, Optional

from ollama_instructor.ollama_instructor_client import OllamaInstructorClient

class Role(Enum):
    WIFE = 'wife'
    HUSBAND = 'husband'
    CHILD = 'child'

class Gender(Enum):
    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'

class Person(BaseModel):
    '''
    This schema describes a person.
    '''
    name: str = Field(..., description='The name of the person')
    age: int = Field(..., description='The age of the person')
    gender: Optional[Gender]
    role: Role

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'name':'John Doe',
                    'age': 55,
                    'gender': 'male',
                    'role': 'husband'
                }
            ]
        }
    )


class ListOfPerson(BaseModel):
    description_of_relationship: str
    persons: List[Person]

client = OllamaInstructorClient(
    host='https://localhost:11434'
)

response = client.chat_completion(
    pydantic_model=ListOfPerson,
    #model='mistral:7b-instruct',
    #model='dolphin-llama3',
    model='phi3:instruct',
    retries=3,
    messages=[
        {
            'role': 'user',
            'content': 'Marion is a 42 years old woman. She lives with her husband Mario (45 years) and her son Daniel (15) in a small house.'
        }
    ],
    options={
        "num_ctx": 8192
    },
    allow_partial=True
)

rich.print(response)
```