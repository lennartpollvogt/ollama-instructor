from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

from ollama_instructor.ollama_instructor_client import OllamaInstructorClient


conversation = '''
Amy: "Hey Monika, how was your vacation?"
Monika: "Hi Amy, thank you for asking! It was so great! How are you?"
Amy: "I am good. And it's nice to have you back. There was a lot going on the last week. Nick came up with some new ideas."
Monika: "Thanks! Okay, let me hear, what Nick came up with."
Amy: "He would like to have a weekly report of the sale of our webshop by email. He asked, if you could set that up. Could you?"
Monika: "Sure! Should be quite easy to do. I will do this on Monday 16-06-2024. After that he will receive a automatic report every Monday."
Amy: "Great! I was sure you could do that. Do you think Bob will as well be interested into that kind of report?"
Monika: "I think so, but can you ask him and let me know?"
Amy: "Yes, I will ask him and have you in copy within the request."
Monika: "Okay, thank you! There came just a question regarding the weekly sales report in my mind. Did Nick mention any crucial information he wants to have in the report?"
Amy: "Yes, he wants to have all sales and earnings listed for each item and a summary of everything, like having the total numbers of sales and earnings."
Monika: "Good to know. Thank you!"
'''


class Person(Enum):
    NICK = 'Nick'
    BOB = 'Bob'
    MONIKA = 'Monika'
    KEN = 'Ken'
    AMY = 'Amy'

class Status(Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in progress'
    DONE = 'done'
    CANCELED = 'canceled'

class Todo(BaseModel):
    '''
    This schema describes a single Todo object.
    '''
    task_description: str = Field(..., description='A more detailed description of the todo to have more context for the assigned person.')
    title: str = Field(..., description='One to three keywords as a title for the todo. Brief and precise!')
    assigned_to: Person = Field(..., description='The person assigned to the Todo.')
    due_date: Optional[str] = Field(None, description='The due date of the Todo. Format of dates it DD-MM-YYYY')
    status: Optional[Status] = Field(default='pending', description='The status of the Todo.')

class ListOfTodos(BaseModel):
    '''
    This schema is used for meetings. It describes a conversation summary, lists the participants and the todos discussed in the meeting.
    '''
    conversation_summary: str = Field(..., description='A detailed description of what the conversation is about. Who was participating and what are the topics?')
    participants: List[Person] = Field(..., description='An arry of the participants of the conversation.')

    tasks: List[Todo] = Field(..., description='This an array of Todos. Each todo is an instance of the Todo object.')


def test_create_todos(host: str, model: str, **kwargs):
    client = OllamaInstructorClient(
        host=host,
    )
    response = client.chat_completion(
        model=model,
        options={"temperature": 0.4},
        pydantic_model=ListOfTodos,
        messages=[
            {
                'role': 'user',
                'content': f'List all task from the following conversation: {conversation}'
            }
        ],
        **kwargs
    )
    return response


def test_stream_create_todos(host: str, model: str, **kwargs):
    client = OllamaInstructorClient(
        host=host,
    )
    response = client.chat_completion_with_stream(
        model=model,
        pydantic_model=ListOfTodos,
        options={"temperature": 0.4},
        messages=[    
            {
                'role': 'user',
                'content': f'List all task from the following conversation: {conversation}'
            }
        ],
        **kwargs
    )

    for chunk in response:
        yield chunk