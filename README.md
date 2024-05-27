# ollama-instructor

`ollama-instructor` is a lightweight Python library that provides a convenient wrapper around the Client of the renowned Ollama repository, extending it with validation features for obtaining valid JSON responses from a Large Language Model (LLM). Utilizing Pydantic, `ollama-instructor` allows users to specify models for JSON schemas and data validation, ensuring that responses from LLMs adhere to the defined schema.

> **Note**: This library has a native support for the Ollamas Python client. If you want to have more flexibility with other providers like Groq, OpenAI, Perplexity and more, have a look into the great library of [instrutor](https://github.com/jxnl/instructor) of Jason Lui.


## Features

- Easy integration with the Ollama repository for running open-source LLMs locally. See: 
    - https://github.com/ollama/ollama
    - https://github.com/ollama/ollama-python
- Data validation using Pydantic models to ensure the JSON response from a LLM meets the specified schema. See:
    - https://docs.pydantic.dev/latest/
- Retries with error guidance if the LLM returns invalid responses. You can set the maxium number of retries.
- Allow partial responses to be returned by setting the `allow_partial` flag to True. This will try to clean set invalid data within the response and set it to `None`. Unsetted data (not part of the Pydantic model) will be deleted from the response.

`ollama-instructor` can help you to get structured and reliable JSON from local LLMs like:
- Llama3
- phi3
- mistral
- Gemma

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
from ollama_instructor import OllamaInstructorClient
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

**chat completion with streaming**:
```python
from ollama_instructor import OllamaInstructorClient
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


## Documentation and examples
- It was always my goal to have a well documented library. Therefore, have a look into the repositorys code to get an idea how to use it.
- A great bunch of how-to-use guides and examples can be found in the [docs](/docs/) folder.
- If you need more information about the library, please feel free to open an issue.


## License

`ollama-instructor` is released under the MIT License. See the [LICENSE](LICENSE) file for more details.


## Support and Community

If you need help or want to discuss `ollama-instructor`, feel free to open an issue on GitHub.
