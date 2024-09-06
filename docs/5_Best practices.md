# Best practices

This is a collection of best practices for `ollama-instructor` I discovered during the development and use of `ollama-instructor`.

Some of the best practices can as well be found in other parts of the documentation of this library. With time I will try to add more and summarize the existing in this overview.

## 1. Serializing information extraction from lists

You might have a list of common text where you want to extract data from. For instance a list of short texts and each text contains information about a different person. For each text you want to extract `name`, `age` and `gender`. Here is the final code:

```Python
from ollama_instructor.ollama_instructor_client import OllamaInstructorClient
from pydantic import BaseModel
from enum import Enum
from typing import List
import rich

class Gender(Enum):
    MALE = 'male'
    FEMALE = 'female'

class Person(BaseModel):
    name: str
    age: int
    gender: Gender

client = OllamaInstructorClient(host='http://localhost:11434')

list_of_text = [
    "Jason is a 21 years old man.",
    "Jane is a 31 years old womand.",
    "Bob is a 35 years old man."
]

list_of_response = []

for text in list_of_text:
    try:
        response = client.chat_completion(
            model='llama3.1:latest',
            pydantic_model=Person,
            messages=[
                {
                    'role': 'user',
                    'content': text
                }
            ],
            format='json',
        )
        list_of_response.append(response['message']['content'])
    except Exception as e:
       pass

print(list_of_response)
```

This approach serializes the information extraction process for multiple texts efficiently. In case of an exception it passes to not interrupt the iteration process.

## 2. Few-shots prompting mistakes
Few-shots prompting is a common practice which can enhance the LLM performance significantly. But I discovered, that few-shots prompting should be done within a single prompt and not be part as the chat history. Let's imagine a chat history for the request like this:

```Python
[
    {
        'role': 'system',
        'content': "\nYou are the world class algorithm for JSON responses. You will get provided 
a JSON schema of a Pydantic model. Your task is to extract those in this JSON schema specified 
properties out of a given text or image (or its context) and return a VALID JSON response adhering
to the JSON schema.\n    \nHere is the JSON schema: {'$defs': {'Gender': {'enum': ['male', 
'female'], 'title': 'Gender', 'type': 'string'}}, 'properties': {'name': {'title': 'Name', 'type':
'string'}, 'age': {'title': 'Age', 'type': 'integer'}, 'gender': {'$ref': '#/$defs/Gender'}}, 
'required': ['name', 'age', 'gender'], 'title': 'Person', 'type': 'object'}.\n    \n\nYou WILL 
return the instance of the JSON schema with the CORRECT extracted data, NOT the JSON schema 
itself. The instance of the JSON schema has the following fields to extract the data for: ['name',
'age', 'gender'].\n        "
    },
    {'role': 'user', 'content': 'Jane is a 31 years old woman'},
    {'role': 'assistant', 'content': '{"name": "Jane", "age": 31, "gender": "female"}'},
    {'role': 'user', 'content': 'Jason is a 21 year old man'},
    {'role': 'assistant', 'content': '{"name": "Jason", "age": 21, "gender": "man"}'},
    {'role': 'user', 'content': 'Bob is a 35 years old man.'}
]
```

This chat history looks like an approach of few-shots prompting since it is containing previous responses from the LLM. I would expect the LLM to return the following:
```
{"name": "Bobo", "age": 35, "gender": "man"}
```

Unexpectedly, this was not the case. Instead I got this:
```
{"name": "Jane", "age": 31, "gender": "female"}
```

Somehow the LLM sticks to the first response. But, try it yourself with the following code example:

```Python
from ollama_instructor.ollama_instructor_client import OllamaInstructorClient
from pydantic import BaseModel
from enum import Enum
from typing import List

class Gender(Enum):
    MALE = 'male'
    FEMALE = 'female'

class Person(BaseModel):
    name: str
    age: int
    gender: Gender

client = OllamaInstructorClient(host='http://localhost:11434')

chat_history = [
    {'role': 'user', 'content': 'Jane is a 31 years old woman'},
    {'role': 'assistant', 'content': '{"name": "Jane", "age": 31, "gender": "female"}'},
    {'role': 'user', 'content': 'Jason is a 21 year old man'},
    {'role': 'assistant', 'content': '{"name": "Jason", "age": 21, "gender": "man"}'}
]


response = client.chat_completion(
    model='llama3.1:latest',
    pydantic_model=Person,
    messages=chat_history,
    format='json'
)

print(response['message']['content'])
```

Instead you should put the examples in the user prompt.
```Python
from ollama_instructor.ollama_instructor_client import OllamaInstructorClient
from pydantic import BaseModel
from enum import Enum
from typing import List

class Gender(Enum):
    MALE = 'male'
    FEMALE = 'female'

class Person(BaseModel):
    name: str
    age: int
    gender: Gender

client = OllamaInstructorClient(host='http://localhost:11434')

next_request = 'Bob is a 35 years old man.'

few_shots = '''
Here are some example to perform the task well:
- 'Jane is a 31 years old woman' --> {"name": "Jane", "age": 31, "gender": "female"}
- 'Jason is a 21 year old man' --> {"name": "Jason", "age": 21, "gender": "man"}
'''

user_prompt = f'''
{few_shots}

Next request: {next_request}
'''

response = client.chat_completion(
    model='llama3.1:latest',
    pydantic_model=Person,
    messages=[{'role': 'user', 'content': user_prompt}],
    format='json'
)

print(response['message']['content'])
```

And now I got the correct output:
```
{'name': 'Bob', 'age': 35, 'gender': 'male'}
```

