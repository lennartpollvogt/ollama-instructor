# Enhanced prompting within Pydantic's BaseModel

The reason why I have chosen Pydantic for `ollama-instructor` are the following:
- Pydantics BaseModel not only let's you create a class to create a `JSON` schema for your data, but also lets you validate the data by this given schema. So, any response from the LLM can be validated to meet the schemas definitions. This validation is a built-in method of `BaseModel`.
- With a specified `JSON` schema you can pass the schema as text to the LLM to instruct it on how to generate a response. This method is used within `ollama-instructor`.
- If validation fails you can get a proper and clear error message on the `ValidationError` with all the details of the error. With this error message you can easily ask the LLM to fix the error and create a new response. If you set `retries` in `chat_completion` or `chat_completion_with_stream` to >1 this feature will be used after a malformed response created a `ValidationError`.

> **Note**: I highly recommend to read the [Pydantic documentation](https://docs.pydantic.dev/latest/) to understand how the BaseModel class (and Pydantic) works. As `ollama-instructor` lets you use your own system prompts without overwriting it, you can benefit from creating customs instructions for you specific use case to gain the best results. With a little bit of practice you will get a feeling for that ;-)

Nevertheless, as `ollama-instructor` will instruct the LLM with the `JSON` schema you can pass additional information within this schema by using several features of Pydantic. This can enrich the LLMs instructions and response by...
- adding addtional information about the specified schema, the fields and data types.
- by setting (advanced) defaults if the LLM does not provide a (correct) value for a field.
- adding docs to the class to explain the purpose of the schema and enriching the context for the LLM.

But be careful with giving to much information and context to the LLM. Sometimes less is better while it is always important to be clear and concise. Sometimes a customized system prompt enhances the performance of the LLM better than a complex enriched `BaseModel`.

> **Tip**: Just like us humans LLMs tend to perform better when they first "think" about the task/context/response before they start to generate the final response. So, I figured out to enhance the LLM response it can be helpful to specify an addtional field within the schema where the LLM can reason about or summarize the context. But that's only beneficial if this field is the first specified field in the schema. See the example below to get an idea of how to use this approach.


## Example

> This is a step by step example with addtional explanation. If you want to get the final script you can skip it by scrolling down to the bottom of this page.

Let's say we want to extract data from a text. For instance we want the LLM to extract several persons from a given text. That means in the end we would expect a list of persons with their name, age, gender and maybe role. To make the code easily readable we can create a `Person` class and some `Enums` but firstly import the necessary libraries:

```Python
from pydantic import BaseModel, Field, ConfigDict
from typing import List
from enum import Enum
```

Let's start with the `Enums`.

One for the gender:

```Python
class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
```

And a second one for the role of the person within the context. Here the context will be text about a family. Therefore, we create a specific enum for that

> **Note**: this is using the capability of LLMs to reason about the context and make a decision on probabilities.

```Python
class Role(Enum):
   WIFE = "wife" 
   HUSBAND = "husband"
   CHILD = "child"
```

With that set we can create the `Person` class with Pydantics `BaseModel` class. And to enrich the prompting for better results we make use of `Field` and `ConfigDict`.
For more information about the `Field` and the `ConfigDict` see the Pydantic documentation on [Field](https://docs.pydantic.dev/latest/concepts/fields/) and [ConfigDict](https://docs.pydantic.dev/latest/concepts/config/).

```Python
class Person(BaseModel):
    name: str = Field(..., description="The name of the person")
    age: int = Field(..., description="The age of the person")
    gender: Gender = Field(default='other', description="The gender of the person")
    role: Optional[Role] = Field(default=None, description="The role of the person within the context")

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'name':'John Doe',
                    'age': 55,
                    'gender': 'male',
                    'role': 'husband'
                }
            ]
        }
    )
```

As you can see we use the `ConfigDict` class to provide an example of a person.

The last class we need is the `Family` class. This class will be used to structure the information about the family (from given text). We make use of a list of `Person` objects. And as I mentioned above we can help the LLM by letting it enrich the context and task by itself. Therefore, I will add a field called `taskDescription` to the `Family` class.

```Python
class ListOfPerson(BaseModel):
    taskDescription: str = Field(..., description='A brief description about the context and necessary data to extract.')
    persons: List[Person]
```

Now let's make use of `ollama-instructor` to extract the data from the following text:

```
'Marion is a 42 years old woman. She lives with her husband Mario (45 years) and her son Daniel (15) in a small house.'
```

## Final script

The final script

```Python
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

from typing import List, Optional

from ollama_instructor.ollama_instructor_client import OllamaInstructorClient

class Role(Enum):
    WIFE = 'wife'
    HUSBAND = 'husband'
    CHILD = 'child'

class Gender(Enum):
    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'

class Person(BaseModel):
    name: str = Field(..., description="The name of the person")
    age: int = Field(..., description="The age of the person")
    gender: Gender = Field(default='other', description="The gender of the person")
    role: Optional[Role] = Field(default=None, description="The role of the person within the context")

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'name':'John Doe',
                    'age': 55,
                    'gender': 'male',
                    'role': 'husband'
                }
            ]
        }
    )

class ListOfPerson(BaseModel):
    taskDescription: str = Field(..., description='A brief description about the context and necessary data to extract.')
    persons: List[Person]


client = OllamaInstructorClient(
    host='https://localhost:11434'
)

response = client.chat_completion(
    pydantic_model=ListOfPerson,
    model='phi3:instruct',
    retries=3,
    messages=[
        {
            'role': 'user',
            'content': 'Marion is a 42 years old woman. She lives with her husband Mario (45 years) and her son Daniel (15) in a small house.'
        }
    ]
)

print(response['message']['content'])
```

**Output**:
```
{
    'taskDescription': 'Marion, her husband Mario, and their son Daniel live together.',
    'persons': [
        {'name': 'Marion', 'age': 42, 'gender': 'female', 'role': 'wife'},
        {'name': 'Mario', 'age': 45, 'gender': 'male', 'role': 'husband'},
        {'name': 'Daniel', 'age': 15, 'gender': 'other', 'role': 'child'}
    ]
}
```

