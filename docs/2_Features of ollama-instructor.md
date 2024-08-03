# Features of ollama-instructor

`ollama-instructor` uses the `chat` method of `Ollama` to request the LLM on the `Ollama` server for a response to a prompt. `ollama-instructor`'s `chat_completion` and `chat_completion_with_stream` extend the `chat` method to support the following features:

- `pydantic_model`: This arguments is a [Pydantic BaseModel](https://docs.pydantic.dev/latest/concepts/models/). As Pydantic brings type checking and validation to Python, it is a great way to define the wanted output of your model and provide a `JSON` schema to instruct the LLM on what and how to structure its output to pass validation.

- `retries`: With nested Pydantic models or smaller LLMs you may run into issue getting a valid response in the first try. Therefore, and to support smaller LLMs `ollama-instructor` provides the `retries` argument. This argument is an integer that defines how many times the LLM should be retried if it fails to return a valid response. With each retry the LLM will be confronted with the `ValidationError` to return a new response.

- `allow_partial`: Can be either `True` or `False`. If set to `True`, the LLM will return a partial response if it fails to return a valid response (even after all retries). This is useful for smaller LLMs that may not be able to handle all the information in the prompt/context. All wrongly set values in the response will be set to `None` or its default value (if set in the Pydantic BaseModel).

- `format` = '': This argument is a native argument of the `chat` method of `Ollama` but was not supported until verion `0.4.0` in with `ollama-instructor`, as `format`= 'json' was forcing the LLM to respond in JSON, what made the outputs reliable. With the release of version `0.4.0` you can use '' as value for the argument `format`. With this set the LLM will be instructed to reason step by step before responding the final JSON in a code block. The code block will be extracted from the response and validated against the Pydantic model.

> **Note 1**: You can have an overview of all available arguments of `Ollama`'s `chat` method by looking into the documentation: [Ollama API](https://github.com/ollama/ollama/blob/main/docs/api.md) and [Ollama Python Client](https://github.com/ollama/ollama-python/blob/main/ollama/_client.py).


> **Note 2**: For more information about the "**WHY?**", the idea and concept of `ollama-instructor` see the [README](/docs/README.md) in the docs folder.


## The methods: `chat_completion` and `chat_completion_with_stream`

You may already figured out that there are two methods available for `ollama-instructor`: `chat_completion` and `chat_completion_with_stream`. The difference between the two is that the first one returns a single response, while the second one returns a stream of the response. With `Ollama`'s `chat` method your are able to set the argument `stream` to `True` or `False`. 
I wasn't able to find a way to set the `stream` argument in the `chat_completion` method. Therefore, I decided to create two methods that are very similar but with different names.

In most of the cases I will use `chat_completion` for examples but you can use `chat_completion_with_stream` if you want to get a stream of the response as both methods have the same arguments and above mentioned features of `ollama-instructor`.

## Reasoning

The `chat_completion` method of ollama-instructor is able to receive the value `''` for the argument `format`. This enables the reasoning capabilities of LLMs and can be used for more complex tasks or JSON schemas. Especially for smaller models this could be beneficial.

### How is this done?
By setting `format` = '' the LLM is not forced to respond within JSON. Therefore, the instructions are crucial, to get a JSON anyway. But with `format` = '' the capabilities of LLMs to reason step by step before answering can be used. When you set `format` = '' the LLM will be instructed differently (have a look into the code in file 'prompt_manager.py'). After the step by step reasoning the LLM is instructed to respond within a code block starting with ```´´´json and ending with ´´´```. The content of this code block will be extracted and validated against the Pydantic model. When comments within the JSON code block occur, the code tries to delete them.

### Example:
Here is an example for the usage:
```Python
import rich.markdown
from ollama_instructor.ollama_instructor_client import OllamaInstructorClient
from pydantic import BaseModel
from typing import List
from enum import Enum
import rich

class Gender(Enum):
    male = "male"
    female = "female"
    other = "other"

class User(BaseModel):
    name: str
    email: str
    age: int
    gender: Gender
    friends: List[str]


client = OllamaInstructorClient(
    host='http://localhost:11434',
    debug=True
)

response = client.chat_completion(
    pydantic_model=User,
    model='mistral',
    messages=[
        {
            'role': 'user',
            'content': 'Extract the name, email and age from this text: "My name is Jane Smith. I am 25 years old. My email is jane@example.com. My friends are Karen and Becky."'
        },
    ],
    format='',
    allow_partial=False
)

rich.print(response)

from rich.console import Console
from rich.markdown import Markdown
console = Console()
md = Markdown(response['raw_message']['content'])
console.print(md)
```

Output of the reasoning which is stored in response['raw_message']['content']:
```
Task Description: Given a JSON schema, extract the named properties 'name', 'email', 'age' and 'gender' from the provided text and return a valid JSON response adhering to the schema.

Reasoning:

 1 'name': The name is mentioned as "My name is Jane Smith".
 2 'email': The email is mentioned as "My email is jane@example.com".
 3 'age': The age is mentioned as "I am 25 years old".
 4 'gender': According to the text, 'Jane' is a female, so her gender would be represented as 'female' in the JSON response.
 5 'friends': The friends are mentioned as "Her friends are Karen and Becky", but according to the schema, 'friends' should be an array of strings, not an object with a title. However, the schema does not explicitly state that each friend must have a unique name, so both 'Karen' and 'Becky' could be included in the 'friends' list.

JSON response:
´´´json
 {
   "name": "Jane Smith",
   "email": "jane@example.com",
   "age": 25,
   "gender": "female",
   "friends": ["Karen", "Becky"]
 }
´´´
```

Output of the extracted JSON within response['message']['content']:
```
 {                                                            
   "name": "Jane Smith",                                    
   "email": "jane@example.com",
   "age": 25,
   "gender": "female",
   "friends": ["Karen", "Becky"]
 }
```

> *Note*: This feature is currently not available for `chat_completion_with_stream`. I try to make this happen.