# ollama-instructor

`ollama-instructor` is a lightweight Python library that provides a convenient wrapper around the Client of the renowned Ollama repository, extending it with validation features for obtaining valid JSON responses from a Large Language Model (LLM). Utilizing Pydantic, `ollama-instructor` allows users to specify models for JSON schemas and data validation, ensuring that responses from LLMs adhere to the defined schema.

> **Note 1**: This library has a native support for the Ollamas Python client. If you want to have more flexibility with other providers like Groq, OpenAI, Perplexity and more, have a look into the great library of [instrutor](https://github.com/jxnl/instructor) of Jason Lui.

> **Note 2**: This library depends on having [Ollama](https://ollama.com) installed and running. For more information, please refer to the official website of Ollama.

## Features

- Easy integration with the Ollama repository for running open-source LLMs locally. See: 
    - https://github.com/ollama/ollama
    - https://github.com/ollama/ollama-python
- Data validation using Pydantic models to ensure the JSON response from a LLM meets the specified schema. See:
    - https://docs.pydantic.dev/latest/
- Retries with error guidance if the LLM returns invalid responses. You can set the maxium number of retries.
- Allow partial responses to be returned by setting the `allow_partial` flag to True. This will try to clean set invalid data within the response and set it to `None`. Unsetted data (not part of the Pydantic model) will be deleted from the response.

`ollama-instructor` can help you to get structured and reliable JSON from local LLMs like:
- llama3
- phi3
- mistral
- gemma
- ...

`ollama-instructor` can be your starting point to build agents by your self. Have full control over agent flows without relying on complex agent framework.


## Installation

To install `ollama-instructor`, run the following command in your terminal:

```
pip install ollama-instructor
```


## Quick Start

Here are quick examples to get you started with `ollama-instructor`:

**chat completion**:
```python
from ollama_instructor.ollama_instructor_client import OllamaInstructorClient
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int

client = OllamaInstructorClient(...)
response = client.chat_completion(
    model='phi3', 
    pydantic_model=Person, 
    messages=[
        {
            'role': 'user',
            'content': 'Jason is 30 years old.'
        }
    ]
)

print(response['message']['content'])
```
Output:
```json
{"name": "Jason", "age": 30}
```

**asynchronous chat completion**:
```python
from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import List
import rich
import asyncio

from ollama_instructor.ollama_instructor_client import OllamaInstructorAsyncClient

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

async def main():
    client = OllamaInstructorAsyncClient(...)
    await client.async_init()  # Wichtig: Die asynchrone Initialisierung aufrufen

    response = await client.chat_completion(
        model='phi3:instruct',
        pydantic_model=Person,
        messages=[
            {
                'role': 'user',
                'content': 'Jason is 25 years old. Jason loves to play soccer with his friends Nick and Gabriel. His favorite food is pizza.'
            }
        ],
    )
    rich.print(response['message']['content'])

if __name__ == "__main__":
    asyncio.run(main())
```

**chat completion with streaming**:
```python
from ollama_instructor.ollama_instructor_client import OllamaInstructorClient
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int

client = OllamaInstructorClient(...)
response = client.chat_completion_with_stream(
    model='phi3', 
    pydantic_model=Person, 
    messages=[
        {
            'role': 'user',
            'content': 'Jason is 30 years old.'
        }
    ]
)

for chunk in response:
    print(chunk['message']['content'])
```

## OllamaInstructorClient and OllamaInstructorAsyncClient

The classes `OllamaInstructorClient` and `OllamaInstructorAsyncClient` are the main class of the `ollama-instructor` library. They are the wrapper around the `Ollama` client and contain the following arguments:
- `host`: the URL of the Ollama server (default: `http://localhost:11434`). See documentation of [Ollama](https://github.com/ollama/ollama)
- `debug`: a `bool` indicating whether to print debug messages (default: `False`). 

> **Note**: I am currently working with `iceream` for the debug messages. Will try to improve that in further development of this library.

### chat_completion & chat_completion_with_stream

The `chat_completion` and `chat_completion_with_stream` methods are the main methods of the library. They are used to generate text completions from a given prompt.

`ollama-instructor` uses `chat_completion` and `chat_completion_with_stream` to expand the `chat` method of `Ollama`. For all available arguments of `chat` see the [Ollama documentation](https://github.com/ollama/ollama).

The following arguments are added to the `chat` method within `chat_completion` and `chat_completion_with_stream`:
- `pydantic_model`: a class of Pydantic's `BaseModel` class that is used to firstly instruct the LLM with the JSON schema of the `BaseModel` and secondly to validate the response of the LLM with the built-in validation of [Pydantic](https://docs.pydantic.dev/latest/).
- `retries`: the number of retries if the LLM fails to generate a valid response (default: `3`). If a LLM fails the retry will provide the last response of the LLM with the given `ValidationError` and insructs it to generate a valid response.
- `allow_partial`: If set to `True` `ollama-instructor` will modify the `BaseModel` to allow partial responses. In this case it makes sure to provide the correct instance of the JSON schema but with default or None values. Therefore, it is useful to provide default values within the `BaseModel`. With the improvement of this library you will find examples and best practice guides on that topic in the [docs](/docs/) folder.


## Documentation and examples
- It was always my goal to have a well documented library. Therefore, have a look into the repositorys code to get an idea how to use it.
- There will be a great bunch of how-to-use guides and examples in the [docs](/docs/) folder (coming soon).
- If you need more information about the library, please feel free to open an issue.


## License

`ollama-instructor` is released under the MIT License. See the [LICENSE](LICENSE) file for more details.


## Support and Community

If you need help or want to discuss `ollama-instructor`, feel free to open an issue on GitHub.
