# ollama-instructor

`ollama-instructor` is a lightweight Python library that provides a convenient wrapper around the Client of the renowned Ollama repository, extending it with validation features for obtaining valid JSON responses from a Large Language Model (LLM). Utilizing Pydantic, `ollama-instructor` allows users to specify models for JSON schemas and data validation, ensuring that responses from LLMs adhere to the defined schema.

[![Downloads](https://static.pepy.tech/badge/ollama-instructor/month)](https://pepy.tech/project/ollama-instructor)

> **Note 1**: This library has a native support for the Ollamas Python client. If you want to have more flexibility with other providers like Groq, OpenAI, Perplexity and more, have a look into the great library of [instrutor](https://github.com/jxnl/instructor) of Jason Lui.

> **Note 2**: This library depends on having [Ollama](https://ollama.com) installed and running. For more information, please refer to the official website of Ollama.

---

### Documentation and guides
- [Why ollama-instructor?](/docs/1_Why%20ollama-instructor.md)
- [Features of ollama-instructor](/docs/2_Features%20of%20ollama-instructor.md)
- [The concept of ollama-instructor](/docs/3_The%20concept%20of%20ollama-instructor.md)
- [Enhanced prompting with Pydantics BaseModel](/docs/4_Enhanced%20prompting%20within%20Pydantics%20BaseModel.md)
- [Best practices](/docs/5_Best%20practices.md)

### Examples
- [Image Captioning](/examples/images/image_captioning.md)
- [Todos from Conversation](/examples/todos/todos_from_chat.md)
- [Multiple async operations](examples/async/async_operations.md)

### Blog
- [How to use ollama-instructor best](/blog/How%20to%20use%20ollama-instructor%20best.md)
- [What you can learn from prompting LLMs for you relationships](/blog/What%20you%20can%20learn%20from%20prompting%20LLMs%20for%20your%20relationships.md)
- [May the BaseModel be with you](/blog/May%20the%20BaseModel%20be%20with%20you.md)


## Features

- Easy **integration with the Ollama** repository for running open-source LLMs locally. See:
    - https://github.com/ollama/ollama
    - https://github.com/ollama/ollama-python
- Data **validation** using **Pydantic BaseModel** to ensure the JSON response from a LLM meets the specified schema. See:
    - https://docs.pydantic.dev/latest/
- **Retries with error guidance** if the LLM returns invalid responses. You can set the maxium number of retries.
- **Allow partial responses** to be returned by setting the `allow_partial` flag to True. This will try to clean set invalid data within the response and set it to `None`. Unsetted data (not part of the Pydantic model) will be deleted from the response.
- **Reasoning** for the LLM to enhance the response quality of an LLM. This could be useful for complex tasks and JSON schemas to adhere and help smaller LLMs to perform better. By setting `format` to '' instead to 'json' (default) the LLM can return a string with a step by step reasoning. The LLM is instructed to return the JSON response within a code block (```json ... ```) which can be extracted from ollama-instructor (see [example](/docs/2_Features%20of%20ollama-instructor.md)).

`ollama-instructor` can help you to get structured and reliable JSON from local LLMs like:
- llama3 & llama3.1
- phi3
- mistral
- gemma
- ...

`ollama-instructor` can be your starting point to build agents by your self. Have full control over agent flows without relying on complex agent framework.

## Concept

![Concept.png](/Concept.png)

> Find more here: [The concept of ollama-instructor](/docs/3_The%20concept%20of%20ollama-instructor.md)

# Quick guide

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
    await client.async_init()  # Important: must call this before using the client

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

**(!) Currently broken due to dependency issues with new version of `ollama` (!)**
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

The classes `OllamaInstructorClient` and `OllamaInstructorAsyncClient` are the main class of the `ollama-instructor` library. They are the wrapper around the `Ollama` (async) client and contain the following arguments:
- `host`: the URL of the Ollama server (default: `http://localhost:11434`). See documentation of [Ollama](https://github.com/ollama/ollama)
- `debug`: a `bool` indicating whether to print debug messages (default: `False`).

> **Note**: Until versions (`v0.4.2`) I was working with `icecream` for debugging. I switched to the `logging` module.

### chat_completion & chat_completion_with_stream

The `chat_completion` and `chat_completion_with_stream` methods are the main methods of the library. They are used to generate text completions from a given prompt.

`ollama-instructor` uses `chat_completion` and `chat_completion_with_stream` to expand the `chat` method of `Ollama`. For all available arguments of `chat` see the [Ollama documentation](https://github.com/ollama/ollama).

The following arguments are added to the `chat` method within `chat_completion` and `chat_completion_with_stream`:
- `pydantic_model`: a class of Pydantic's `BaseModel` class that is used to firstly instruct the LLM with the JSON schema of the `BaseModel` and secondly to validate the response of the LLM with the built-in validation of [Pydantic](https://docs.pydantic.dev/latest/).
- `retries`: the number of retries if the LLM fails to generate a valid response (default: `3`). If a LLM fails the retry will provide the last response of the LLM with the given `ValidationError` and insructs it to generate a valid response.
- `allow_partial`: If set to `True` `ollama-instructor` will modify the `BaseModel` to allow partial responses. In this case it makes sure to provide the correct instance of the JSON schema but with default or None values. Therefore, it is useful to provide default values within the `BaseModel`. With the improvement of this library you will find examples and best practice guides on that topic in the [docs](/docs/) folder.
- `format`: In fact this is an argument of `Ollama` already. But since version `0.4.0` of `ollama-instructor` this can be set to `'json'` or `''`. By default `ollama-instructor` uses the `'json'` format. Before verion `0.4.0` only `'json'` was possible. But within `chat_completion` (**NOT** for `chat_completion_with_stream`) you can set `format` = `''` to enable the reasoning capabilities. The default system prompt of `ollama-instructor` instructs the LLM properly to response in a ```json ...``` code block, to extract the JSON for validation. When coming with a own system prompt an setting `format`= `''`, this has to be considered. See an [example here](/docs/2_Features%20of%20ollama-instructor.md).


## Documentation and examples
- It is my goal to have a well documented library. Therefore, have a look into the repositorys code to get an idea how to use it.
- There will be a bunch of guides and examples in the [docs](/docs/) folder (work in progress).
- If you need more information about the library, please feel free to open a discussion or write an email to lennartpollvogt@protonmail.com.


## License

`ollama-instructor` is released under the MIT License. See the [LICENSE](LICENSE) file for more details.


## Support and Community

If you need help or want to discuss `ollama-instructor`, feel free to open an issue, a discussion on GitHub or just drop me an email (lennartpollvogt@protonmail.com).
I always welcome new ideas of use cases for LLMs and vision models, and would love to cover them in the examples folder. Feel free to discuss them with me via email, issue or discussion section of this repository. 😊
