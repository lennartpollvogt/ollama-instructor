# ollama-instructor

`ollama-instructor` is a lightweight Python library that provides a convenient wrapper around the Ollama Client, extending it with validation features for obtaining valid JSON responses from Large Language Models (LLMs). Utilizing Pydantic, `ollama-instructor` ensures that responses from LLMs adhere to defined schemas.

[![Downloads](https://static.pepy.tech/badge/ollama-instructor/month)](https://pepy.tech/project/ollama-instructor)

> **Note**: This library depends on having [Ollama](https://ollama.com) installed and running. For more information, please refer to the official website of Ollama.

## Breaking Changes in Version 1.0.0

Version 1.0.0 introduces significant changes from version 0.5.2:
- Complete refactoring to directly inherit from Ollama's official Client classes
- Simplified API that aligns more closely with Ollama's native interface
- Improved logging system using Python's built-in logging module
- Streamlined validation process using Pydantic
- Removal of partial validation features to focus on core functionality
- New method names: `chat_completion` and `chat_stream` (previously `chat_completion_with_stream`)

## Features

- **Direct Integration**: Inherits directly from Ollama's official client for seamless integration
- **Schema Validation**: Uses Pydantic BaseModel to ensure valid JSON responses
- **Retry Mechanism**: Automatically retries failed validations with configurable attempts
- **Logging**: Comprehensive logging system with configurable levels
- **Async Support**: Full async/await support through `OllamaInstructorAsync`

## Installation

```bash
pip install ollama-instructor
```

## Quick Start

For streaming examples click [here](examples/)

### Synchronous Usage:
```python
from pydantic import BaseModel
from ollama_instructor import OllamaInstructor

class FriendInfo(BaseModel):
    name: str
    age: int
    is_available: bool

class FriendList(BaseModel):
    friends: list[FriendInfo]

# Create client with logging enabled
client = OllamaInstructor(enable_logging=True, log_level='DEBUG')

# Chat completion
response = client.chat_completion(
    format=FriendList,
    model='llama2:latest',
    messages=[
        {
            'role': 'user',
            'content': 'I have two friends: John (25, available) and Mary (30, busy)'
        }
    ]
)
```

### Asynchronous Usage:
```python
import asyncio
from pydantic import BaseModel
from ollama_instructor import OllamaInstructorAsync

class FriendInfo(BaseModel):
    name: str
    age: int
    is_available: bool

async def main():
    client = OllamaInstructorAsync(enable_logging=True)

    response = await client.chat_completion(
        format=FriendInfo,
        model='llama2:latest',
        messages=[
            {
                'role': 'user',
                'content': 'John is 25 years old and available to hang out'
            }
        ]
    )

if __name__ == "__main__":
    asyncio.run(main())
```

## Logging

The library includes comprehensive logging capabilities. You can enable and configure logging when initializing the client:

```python
client = OllamaInstructor(
    enable_logging=True,
    log_level="DEBUG",  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

## Support and Community

If you need help or want to discuss `ollama-instructor`, feel free to:
- Open an issue on GitHub
- Start a discussion in the GitHub repository
- Contact via email: lennartpollvogt@protonmail.com

Contributions and feedback are always welcome! 😊

## License

`ollama-instructor` is released under the MIT License. See the [LICENSE](LICENSE) file for more details.
