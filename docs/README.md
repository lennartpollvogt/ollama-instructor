# Introduction

Since **Ollama** gives people the opportunity to run open source LLMs locally, this democratizes AI. Many people are now running open source LLMs on their own hardware and trying to build useful apps and tools without relying on closed source LLMs like **GPT-4**, **Claude3** or **Grok**.

The advantage of LLMs is their knowledge and their capability in understanding context, deducing and guessing. But their response is plain text. This is great for human readability but hard to process in applications, since an LLM will not always produce the exact same response - and more important, not in the same structure - on the same question.

But using the above mentioned capabilities of an LLM can be highly benificial for the users of an app or for a company. However, it would be great to have the LLMs response in a reliable, machine readable and processable format. And that's why already some intelligent people managed to force the LLM to create their output in pure `JSON` bye using grammar, which can be activated with `json`-mode in **Ollama** since version [v0.19](https://github.com/ollama/ollama/releases/tag/v0.1.9).

Here is an example:
```Python
from ollama import Client

client = Client(
    host= "localhost:11434"
)

response = client.generate(
    model="mistral:7b-instruct",
    system="You are a helpful algorithm responding in JSON.",
    prompt="My name is Jason an I am 30 years old. I like to play soccer with my friends.",
    format="json"
)

print(response['response'])

# Output 1:
# {"name": "Jason", "age": 30, "interests": ["soccer"]}

# Output 2:
# {"Name": "Jason", "Age": 30, "Hobbies": [{"Activity": "Soccer", "Description": "Playing soccer with friends"}]}
```

I asked the LLM - with activated `json` mode - two times with the exact same system prompt and user prompt. Both responses are not the same and differ mainly in structure. This will make it hard to process in further code.

## Why `JSON`?

From Wikipedia:
> "`JSON` (JavaScript Object Notation) is an open standard file format and data interchange format that uses human-readable text to store and transmit data objects consisting of attribute-value pairs and arrays (or other serializable values). It is a commonly used data format with diverse uses in electronic data interchange, including that of web applications with servers"

So, `JSON` is one of the most used formats used in applications. And the good thing is, that LLMs understand what `JSON` is. And if we can manage LLMs to procude reliable `JSON`, why not take advantage from that?

You need an example? What about a todo app, where you tell the app - backed by a LLM - what todos you will have or which todos you already completed? The LLM would use your prompt to create new and search for existing todos.

Let's have this todo app in mind and come back to it later.


## Why `ollama-instructor`?

I love experimenting with LLMs and love running LLMs on my local machine with **Ollama**, since this framework brings a lot of simplicity to run open source LLMs on effordable hardware. But why `ollama-instructor`?

Firstly, I wanted to have an easy way on how to create JSON from an LLM. Secondly, the produced JSON should be validatable, to make it reliable and predictable in its structure for further processing within an app. After some research and testing of other libraries, I came up with the wish of creating my own open source library, mainly based on **Ollama** to run open source LLMs locally and [**Pydantic**](https://docs.pydantic.dev/latest/) to easily specify JSON schemas and validate the JSON response from the LLMs.

To be honest, `ollama-instructor` is inspired by another open source python library called [**instructor**](https://github.com/jxnl/instructor) by Jason Liu. And like **instructor**, `ollama-instructor` uses **Pydantic** to specify `JSON` schemas, instruct the LLM with it and validate the LLMs response to ensure reliability. 

And to be completly open, since version [v0.1.24](https://github.com/ollama/ollama/releases/tag/v0.1.24) **Ollama** supports the *OpenAI compatibility* and therefore can be used with **instructor** and the **OpenAI** `Client`, too. But as **Ollama** has its native `Client` which is more intuitive for the use of **Ollama** this is not be supported by **instrcutor**.
That's why I tried to create something comparable on my own and came up with `ollama-instructor` and my own approaches on how to get reliable responses from smaller 7b LLMs like **Mistral**, **Llama3** or even the tiny **Phi3**.

## What to consider

Not all LLMs are suitable for the task of producing JSON. Some LLMs are great for having conversations like in a chat, some are great at coding and some are great to follow instructions. You will discover a lot of LLMs that have been created for different task. The last type of mentioned LLMs are those highly recommended when trying to produce reliable `JSON` with `ollama-instructor`. Here are my favorite LLMs I was using during the development of `ollama-instructor`:

**7b models**:
- `mistral:7b-instruct`
- `codellama:7b-instruct`
- `llama3:7b`
- `openhermes`
- `gemma:7b-instruct`

**2b models**:
- `gemma:2b-instruct`
- `phi3`

> Hint: 2b models run on low performing hardware but you will struggle to get a successful response from them. For easy tasks they are good and fast but when the complexity of the **Pydantic** model increases, you will be forced to be really good in prompting. Nevertheless, **Phi3** is a very capable tiny model!

You can get more information and download them all from the [**Ollama** models library](https://ollama.com/library).


## The advantage of **Pydantic** for specifying JSON schemas

Remember the todo app? Let's try this with different approaches without and with `ollama-instructor`.

Imagine we have a text with tasks like this:

```
"My boss wants me to create a presentation on the Asian commodity market. I will have to finish the presentation on Monday, 01.04.2024. Secondly my wife asked me to go to the grocery store and buy here some coffee."
```

As you can see we have two tasks:
- create a presentation about the commodity market in Asia
- buy my wife some coffee from the grocery store

I would like to have the LLM to create its response in `JSON` in the following structure:

```JSON
{
    todos: [
        {
            "title": "Create presentation",
            "taskDescription": "Create a presentation about the commodity markets in Asia for my boss",
            "dueDate": "01.04.2024",
            "status": "open"
        },
        {
            "title": "Buy coffee for wife",
            "taskDescription": "Go to the grocery store and by my wife coffee",
            "dueDate": "",
            "status": "open"
        }
    ]
}
```

Let's try this with **Ollama**:
```python
from ollama import Client

client = Client(
    host= "localhost:11434"
)

response = client.chat(
    model="mistral:7b-instruct",
    messages = [
      {
        "role": "system",
        "content": "You are a helpful algorithm responding in JSON.",
      },
      {
        "role": "user",
        "content": "My boss wants me to create a presentation on the Asian commodity market. I will have to finish the presentation on Monday, 01.04.2024.",
      }
    ],
    format="json"
)

print(response['message']['content'])
```

**Output**:
```JSON
{
  "assistance": {
    "message": "I'd be happy to help you create a presentation on the Asian commodity market with a deadline of Monday, 01.04.2024.",
    "recommendations": [
      {
        "title": "Market Overview",
        "content": [
          "Briefly introduce the Asian commodity market and its significance in the global economy.",
          "Discuss the major commodities traded in Asia (e.g., oil, gas, metals, agricultural products)",
          "Provide statistics on the market size and growth trends"
        ]
      },
      {
        "title": "Key Players and Market Dynamics",
        "content": [
          "Identify the major countries and companies involved in the Asian commodity market.",
          "Discuss the drivers (demand and supply factors) of the market.",
          "Analyze the impact of government policies, regulations, and geopolitical factors on the market."
        ]
      },
      {
        "title": "Market Trends and Challenges",
        "content": [
          "Discuss current trends in the Asian commodity market (e.g., digitalization, sustainability)",
          "Explore challenges facing the market (e.g., price volatility, logistical issues)",
          "Highlight potential solutions or strategies to address these challenges."
        ]
      },
      {
        "title": "Case Studies and Success Stories",
        "content": [
          "Share examples of successful companies or projects in the Asian commodity market.",
          "Analyze the factors contributing to their success.",
          "Discuss potential lessons learned for other players in the market."
        ]
      },
      {
        "title": "Future Outlook and Conclusion",
        "content": [
          "Provide an outlook on the future of the Asian commodity market based on current trends and forecasts.",
          "Summarize key takeaways from the presentation.",
          "Encourage audience engagement and questions."
        ]
      }
    ]
  }
}
```

Uff... this is way to much and not what i wanted. Let' try this again and give the LLM some instrcutions:
```Python
from ollama import Client

client = Client(
    host= "http://192.168.0.171:11434"
)

response = client.chat(
    model="mistral:7b-instruct",
    messages = [
      {
        "role": "system",
        "content": "You are a helpful algorithm responding in JSON. You will be asked to create a JSON response to structure todos. One todo has a title, a task description, a due date and a status."
      },
      {
        "role": "user",
        "content": "My boss wants me to create a presentation on the Asian commodity market. I will have to finish the presentation on Monday, 01.04.2024."
      }
    ],
    format="json"
)

print(response['message']['content'])
```

In the `system prompt` I gave the LLM the instrcution that every todo has a basic strcuture of "title", "task description", a "due date" and a "status". Let`s see what it responses:

**Output**:
```JSON
{
"todos": [
    {
        "title": "Prepare presentation on Asian Commodity Market",
        "description": "Research and gather data on various commodities in the Asian market, create graphs and charts to illustrate trends, write content for slides, and design visuals.",
        "due_date": {
            "year": 2024,
            "month": 4,
            "day": 1
        },
        "priority": 1,
        "status": "In Progress"
    }
]
}
```

Very good! But, not exactly what I wanted, since I didn't asked for an array of todos (not yet).  And even if so, how high is the chance the LLM produces the same strucuture every time and how should I validate?

That's why `ollama-instrcutor` makes advantage of **Pydantic**. With **Pydantic** it is quite convenient for developers to create `JSON` schemas and validate them. It is also possible to add some customized validations to extend **Pydantics** built-in validation functionality. And additionally, you don't have to specify a system prompt, as `ollama-instructor` will you the **Pydantic** model to instruct and validate the LLM.

```Python
from ollama_instructor.ollama_instructor_client import OllamaInstructorClient
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class Status(Enum):
    OPEN = 'open'
    DONE = 'done'

class Priority(Enum):
    LOW = 'low'
    MEDIUM ='medium'
    HIGH = 'high'

class Todo(BaseModel):
    todoDescription: str = Field(description='A brief description of the todo to provide more context for the todo.')
    todoTitle: str = Field(description="The title of the todo.")
    dueDate: str = Field(description=f"The date the task is due. Must be in the format of DD-MM-YYYY. Today is {datetime.now().strftime('%d-%m-%Y')}")
    priority: Priority
    status: Status


client = OllamaInstructorClient(
  host="http://localhost:11434"
)

response = client.chat_completion(
    model="mistral:7b-instruct",
    pydantic_model=Todo,
    messages = [
      {
        "role": "user",
        "content": "My boss wants me to create a presentation on the Asian commodity market. I will have to finish the presentation on Monday, 01.04.2024."
      }
    ],
    format="json"
)

print(response['message']['content'])
```

**Output**:
```JSON
{
    "todoTitle": "Create presentation on Asian commodity market", 
    "todoDescription": "Prepare and deliver a presentation on the current state of the Asian commodity market for an upcoming meeting.", 
    "dueDate": "01-04-2024", 
    "priority": "medium", 
    "status": "open"
}
```

As you may recognized this examples has not system prompt but the class `User` is used as a parameter of the function `chat_completion`. That's because `ollama-instructor` brings its own system prompt where it instructs the LLM with the help of the **Pydantic** model to respond in the correct structure with the asked data. 
And additionally, `ollama-instructor` will validate the response if it fits the given **Pydantic** model. If the validation fails, it will ask the LLM again within a certain number of retries (default is 3) until the LLM gives a valid answer or the maximum number of retries is reached.

## Own system prompts

If you want to use your own system prompts, you can do so. `ollama-instructor` will recognize that you have a system prompt within you `messages` parameter and will not use the default system prompt.

> **Attention**: When instructing the LLM with your own system prompt, make sure you are quite specific and about the desired structure of the response. Best practices are to prompt the LLM to response `JSON` and use **Pydantics** built-in functionality to provide the LLM with the `JSON` schema.

> **Pros**: 
> - You can use your own system prompts and still benefit from `ollama-instrcutors` validation.
> - Your system prompt can be more specific to your needs and can enhance the quality of the LLMs response.
> - For more quality boost, make sure to provide within the `messages` parameter some examples of prompts and responses. This method is called **few-shot prompting** and is very effective.

Here is an example on how you could use your own system prompt to instruct the LLM:
```Python
from ollama_instructor.ollama_instructor_client import OllamaInstructorClient
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class Status(Enum):
    OPEN = 'open'
    DONE = 'done'

class Priority(Enum):
    LOW = 'low'
    MEDIUM ='medium'
    HIGH = 'high'

class Todo(BaseModel):
    todoDescription: str = Field(description='A brief description of the todo to provide more context for the todo.')
    todoTitle: str = Field(description="The title of the todo.")
    dueDate: str = Field(description=f"The date the task is due. Must be in the format of DD-MM-YYYY. Today is {datetime.now().strftime('%d-%m-%Y')}")
    priority: Priority
    status: Status


client = OllamaInstructorClient(
  host="http://localhost:11434"
)

response = client.chat_completion(
    model="mistral:7b-instruct",
    pydantic_model=Todo,
    messages = [
      {
        "role": "system",
        "content": f"You are the ultimate expert in creating todos while adhering to the following JSON schema: {Todo.model_json_schema()}. Your task is give the todo a brief but descriptive title. The description of the task should be enriched by considerable context, to enhance the thinking of the user, when he/she will come back to the work on the todo. Give a rough estimation within the description of the effort in days to complete the task. The due date must be provided in the format of DD-MM-YYYY. The priority of the task must be either low, medium or high. The status of the task must be either open or done. You have to consider to ONLY respond in JSON with the correct instance of the JSON schema and NOT the schema itself."
      },
      {
        "role": "user",
        "content": "My boss wants me to create a presentation on the Asian commodity market. I will have to finish the presentation on Monday, 01.04.2024."
      }
    ],
    format="json"
)

print(response['message']['content'])
```

Output:
```
{'todoTitle': 'Create Asian Commodity Market Presentation',
'todoDescription': 'Prepare an engaging and informative presentation on the current state of the Asian commodity market, including key players, trends, and forecasts. Conduct thorough research to ensure accuracy and relevance. Visual aids such as graphs and charts may be used to enhance understanding. Estimated effort: 3-4 days.',
'dueDate': '01-04-2024', 
'priority': 'medium', 
'status': 'open'}
````





