# How to use ollama-instructor "best"

This blog article is here to give you a guide of best practice, but it may not be what you expect. It is a guide on how to look on and interpret the [docs](/docs/) and [examples](/examples/) of this library rather than a guide on how to write the code. In summary, a guide to encourage you to use your own creativity and imagination when building with ollama-instructor.

## What we know

As already explained in the library's description and README.md file, ollama-instructor is here to gain validated structured outputs from open source large language models (LLMs) and vision models with Ollama. Next to Ollama's Python client it is using Pydantic as core feature to define the schema, instruct the models and validate the outputs. 

Let's look at the following example of the README.md to review an idea of the usage:
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

The output should be:
```JSON
{"name": "Jason", "age": 30}
```

The use case here is extracting predefined personal information out of an unstructured text. For sure, this is a strong use case but there are a lot more, like image captioning, todo lists, etc. Some you can find already in the docs and examples folders of this library. And combining different approaches like tool use (alias *function calling*) with structured outputs, there is even more to find. But can I fully cover them within the library's documentation? The answer is "no".

## Limitations?

You could say: "ollama-instructor is limited to make structured outputs from LLMs and vision models reliable". And that's correct! This is indeed what ollama-instructor is meant for. But what you are able to do with "reliable" structured outputs is something the docs can't fully cover and we do not completely know.

Let's see this library as a tool. A tool to generate structured outputs with LLMs, but not that kind of tool which is limited to one use case within a certain scenario (e.g. use a knife to cut an apple). It's a tool you can use for different scenarios and maybe for some scenarios which it is not intentionally designed for (e.g. use a knife like a wedge to split firewood).

If I am honest, the docs are somehow limited to what I have experienced (professional and private) and what I know. That - and my lack of time - is why the examples folder has its limitations in giving you examples for possible use cases or how to do things. This doesn't mean I am not eager of providing you with new examples as I love digging into new topics and making something out of it. But I can't cover and discover them all. Therefore, I started to write blog articles like this one you read, to provide you with my thoughts and experiences on different topics related to ollama-instructor. 

So, there is much we know but there is much more we don't know when it comes to use cases for this library.
``
## Who's in charge?

Everyone of us has experienced something different and has a different knowledge base. Therefore, everyone is its own expert and in charge for what they could use ollama-instructor. And coming back to the tool analogy everyone can be a craftsman and discover new ways of using a tool. Sure, many ways are already discovered by someone but I am confident still many are waiting to be discovered or rediscovered differently.

## Real limitations

The real limitations you will discover are the limits of LLMs and vision models themselves. Therefore, it will be one of your jobs to choose a suitable model for your task and know about its limitations.

Here are some examples what to consider:
- If you want to have outputs in a certain language you will need a model which is able to respond in this language. But this model may struggle in responding in JSON format.
- If you need tool use you will need to choose a model which knows how to use tools but this model has not vision capabilities.
- If you need to process images you need to use a vision model which is also capable to respond structured outputs but the language capabilities are limited to English only.

## Discover together

What I try - and that's why I created this article to emphasize - is to give everyone an idea that this library is not only limited to the use cases provided in the docs and examples folders, but use this as a starting point to develop new use cases for your own projects.
As already said, this is not the kind of best practice guide you might expect, this is something different and tries to take you into responsibility what you are crafting with LLMs and this library.

As this library may will experience some increase in usage, my honest wish is to have a supportive community. With that said I'd like to welcome everyone to participate and contribute to this library with code, examples, questions and discussions (here on GitHub).

Let's use our creativity and discover together new use cases and make development with ollama-instructor as easy as possible for beginners and experienced developers by enriching with questions and discussions.