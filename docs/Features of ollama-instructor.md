# Features of ollama-instructor

`ollama-instructor` uses the `chat` method of `Ollama` to request the LLM on the `Ollama` server for a response to a prompt. `ollama-instructor`'s `chat_completion` and `chat_completion_with_stream` extend the `chat` method to support the following features:

- `pydantic_model`: This arguments is a [Pydantic BaseModel](https://docs.pydantic.dev/latest/concepts/models/). As Pydantic brings type checking and validation to Python, it is a great way to define the wanted output of your model and provide a `JSON` schema to instruct the LLM on what and how to structure its output to pass validation.


- `retries`: With nested Pydantic models or smaller LLMs you may run into issue getting a valid response in the first try. Therefore, and to support smaller LLMs `ollama-instructor` provides the `retries` argument. This argument is an integer that defines how many times the LLM should be retried if it fails to return a valid response. With each retry the LLM will be confronted with the `ValidationError` to return a new response.


- `allow_partial`: Can be either `True` or `False`. If set to `True`, the LLM will return a partial response if it fails to return a valid response (even after all retries). This is useful for smaller LLMs that may not be able to handle all the information in the prompt/context. All wrongly set values in the response will be set to `None` or its default value (if set in the Pydantic BaseModel).

> **Note 1**: You can have an overview of all available arguments of `Ollama`'s `chat` method by looking into the documentation: [Ollama API](https://github.com/ollama/ollama/blob/main/docs/api.md) and [Ollama Python Client](https://github.com/ollama/ollama-python/blob/main/ollama/_client.py).


> **Note 2**: For more information about the "**WHY?**", the idea and concept of `ollama-instructor` see the [README](/docs/README.md) in the docs folder.


## The methods: `chat_completion` and `chat_completion_with_stream`

You may already figured out that there are two methods available for `ollama-instructor`: `chat_completion` and `chat_completion_with_stream`. The difference between the two is that the first one returns a single response, while the second one returns a stream of the response. With `Ollama`'s `chat` method your are able to set the argument `stream` to `True` or `False`. 
I wasn't able to find a way to set the `stream` argument in the `chat_completion` method. Therefore, I decided to create two methods that are very similar but with different names.

In most of the cases I will use `chat_completion` for examples but you can use `chat_completion_with_stream` if you want to get a stream of the response as both methods have the same arguments and above mentioned features of `ollama-instructor`.

