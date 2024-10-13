# Running Multiple Requests with Async Operations Using `ollama-instructor`

## Introduction

Asynchronous programming, particularly using Python's `asyncio` library, allows you to run multiple operations concurrently, improving the efficiency and performance of your code. This guide will walk you through an example demonstrating how to use `ollama-instructor` with async operations to make concurrent requests.

## Key Concepts

### AsyncIO
AsyncIO is a library for writing single-threaded concurrent code using coroutines, multiplexing I/O access over sockets and other resources, running network clients and servers, and other related primitives.

### Ollama-Instructor Client
The `ollama-instructor` client allows you to interact with the Ollama model for generating JSON structured outputs based on input messages. By using async operations, you can send multiple requests simultaneously.

## Example Implementation

Let's take a look at an example implementation that demonstrates how to use `ollama-instructor` with async operations to make concurrent requests:

```python
from typing_extensions import Any
from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import List, Dict, Any
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

async def process_request(client, messages):
    response = await client.chat_completion(
        model='qwen2.5:3b',
        pydantic_model=Person,
        messages=messages,
    )
    return response['message']['content']

async def main():
    client = OllamaInstructorAsyncClient()
    await client.async_init()  # Important: must call this before using the client

    requests = [
        process_request(client, [
            {
                'role': 'user',
                'content': 'Jason is 25 years old. Jason loves to play soccer with his friends Nick and Gabriel. His favorite food is pizza.'
            }
        ]),
        process_request(client, [
            {
                'role': 'user',
                'content': 'Alice is 30 years old. Alice enjoys reading books and hiking in her free time. Her favorite season is fall.'
            }
        ]),
        process_request(client, [
            {
                'role': 'user',
                'content': 'Bob is 28 years old. Bob works as a software developer and loves coding and gaming on weekends.'
            }
        ])
    ]

    responses = await asyncio.gather(*requests)
    for response in responses:
        rich.print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

Output:
```
{'name': 'Jason', 'age': 25, 'gender': 'male', 'friends': ['Nick', 'Gabriel']}
{'name': 'Alice', 'age': 30, 'gender': 'female', 'friends': []}
{'name': 'Bob', 'age': 28, 'gender': 'male', 'friends': []}
```

You will recommend that the responses will come more or less simultanousely.

> Ollama is able to handle async operations. By using the same model for all requests this only needs a tiny bit more memory of you machine.

## Explanation of the Code

Let's break down the key components of this implementation:

1. **Classes**: We define an Enum `Gender` and a Pydantic model `Person` to represent a person with attributes like name, age, gender, and friends.

2. **Async Function**: The `process_request` function is defined as an async function that takes a client and messages, makes a chat completion request using the client, and returns the content of the response.

3. **Main Function**:
   - We initialize the OllamaInstructorClient and call `async_init()` to set up the client.
   - We create a list of tasks (`requests`), where each task is an async call to `process_request` with different user messages.
   - We use `asyncio.gather(*requests)` to run all the tasks concurrently and wait for them to complete.
   - Finally, we print each response using `rich.print`.

## Tips for Effective Async Operations

To ensure effective and efficient asynchronous operations:

1. **Concurrency**: Use `asyncio.gather` or other concurrency mechanisms provided by asyncio to perform multiple operations concurrently.
2. **Error Handling**: Implement error handling within the tasks to manage exceptions that may occur during execution.
3. **Resource Management**: Be mindful of resource usage, especially when dealing with network requests, to avoid overwhelming the server or system.
4. **Testing and Performance**: Test your implementation under load conditions to ensure it scales well and handles concurrency effectively.

## Conclusion

Using `ollama-instructor` in conjunction with async operations allows you to efficiently handle multiple requests concurrently. This approach can lead to significant performance improvements in applications that require handling of multiple tasks simultaneously. By following the principles outlined in this guide, you can effectively implement asynchronous operations for your `ollama-instructor` clients and improve overall system efficiency.
