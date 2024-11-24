# Create todos from chat conversation

## Introduction

Todo list generation is a crucial aspect of project management and personal productivity. It involves creating structured lists of tasks that need to be completed, often with associated deadlines and responsible individuals. In this example, I will demonstrate how to use `ollama-instructor` to generate a todo list based on a conversation between two colleagues discussing a market report project.

## Applications of automated todo list generation

Automated todo list generation has numerous applications in various fields:

1. Project planning: Quickly create initial task lists for new projects
2. Task delegation: Assign responsibilities to team members based on their roles
3. Time management: Generate prioritized lists of tasks for efficient work planning
4. Collaboration tools: Enhance team communication by providing clear, structured task lists

## Challenges in automated todo list generation

While automated todo list generation offers many benefits, it also presents some challenges:

- Extracting relevant information from conversations: Identifying key tasks and deadlines from natural language
- Assigning appropriate due dates: Determining realistic deadlines based on project scope and complexity
- Ensuring completeness of tasks: Capturing all necessary steps for project completion
- Handling ambiguity in natural language: Dealing with unclear or vague instructions in the input conversation

## Example implementation

Let's look at an example of how to use `ollama-instructor` to generate a todo list based on a conversation between two colleagues discussing a market report project:

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from enum import Enum
import rich
from ollama_instructor.ollama_instructor_client import OllamaInstructorClient

# Define the Pydantic models
class AssignedPerson(Enum):
    ALICE = "Alice"
    BOB = "Bob"
    BOTH = "Both"

class Todo(BaseModel):
    title: str = Field(..., description="A brief title for the todo item")
    description: str = Field(..., description="A detailed description of the todo item")
    assigned_person: AssignedPerson = Field(..., description="The person assigned to this todo")
    due_date: Optional[date] = Field(description=f"The due date for this todo item. Today is {date.today()}")

class TodoList(BaseModel):
    todos: List[Todo] = Field(..., description="A list of todo items for the market report project")

# Initialize the OllamaInstructorClient
client = OllamaInstructorClient()

# The conversation to analyze
conversation = """
Alice: Hey Bob, did you hear about the boss's request for a new market report?
Bob: Yeah, I just got the email. Sounds like a big project. Where should we start?
Alice: I'm not sure. There's a lot to cover. We need to gather data, analyze trends, and write up the findings.
Bob: Don't forget about the presentation. The boss wants us to present this to the board next month.
Alice: Right, good point. We should probably start with research and data collection. Then move on to analysis, report writing, and finally the presentation prep.
Bob: Agreed. We should also decide who's going to handle each part. I can take the lead on data collection if you want to focus on the analysis.
Alice: That works for me. Let's use our AI assistant to help us create a structured todo list. It'll make sure we don't forget anything important.
Bob: Great idea! Let's give it a try.
"""

# Generate todos using ollama-instructor
response = client.chat_completion(
    pydantic_model=TodoList,
    model='llama3.1:latest', # or any other model you prefer
    messages=[
        {
            'role': 'user',
            'content': 'You are an AI assistant helping to create a structured todo list for a market report project based on a conversation between two colleagues.'
        },
        {
            'role': 'user',
            'content': f"Based on the following conversation, create a structured todo list for the market report project. Include appropriate titles, descriptions, assigned persons, and due dates for each todo item:\n\n{conversation}"
        }
    ],
    retries=2
)

# Print the generated todos
print("Generated Todo List:")
rich.print(response['message']['content'])
```

## Explanation of the code

Let's break down the key components of this implementation:

1. **Classes**: I defined one Enum and two Pydantic models:
   - `AssignedPerson`: An Enum representing the people who can be assigned tasks
   - `Todo`: Represents a single todo item with title, description, assigned person, and due date
   - `TodoList`: Contains a list of Todo items

2. **Client Initialization**: I created an instance of `OllamaInstructorClient`, specifying the host address.

3. **Conversation Input**: I provided a sample conversation between Alice and Bob discussing their market report project.

4. **Todo List Generation**: I used the `chat_completion` method of the client to generate the todo list.

## Output example

Here's an example of what the output might look like:

```
{
    'todos': [
        {
            'title': 'Review quarterly sales numbers',
            'description': "Compare current quarter's sales with last year's figures and
identify trends.",
            'assigned_person': 'Alice',
            'due_date': '2024-09-12'
        },
        {
            'title': 'Research new market trends',
            'description': 'Analyze recent reports and articles to stay up-to-date on
the latest market developments.',
            'assigned_person': 'Bob',
            'due_date': None
        },
        {
            'title': 'Prepare market report presentation',
            'description': 'Create a visually appealing presentation that summarizes key
findings and recommendations.',
            'assigned_person': 'Both',
            'due_date': '2024-09-15'
        }
    ]
}
```

## Tips for effective todo list generation and potential improvements

To improve the quality of generated todo lists:

1. **Provide clear instructions**: Be specific about the desired output format and content.
2. **Use specific examples**: Include sample todo items in your prompt to guide the AI's understanding.
3. **Adjust model parameters**: Experiment with different temperature settings to balance creativity and consistency.
4. **Reasoning**: Let the LLM first summarize and reason about the conversation, todos and considerations. Then, based on the conversation and the summary let the LLM create the todo items with `ollama-instructor`.
5. Adding more complex task relationships (e.g., dependencies, subtasks)
6. Incorporating external data sources (e.g., project management tools, calendars)
7. Implementing a web interface for easier input and visualization of the generated todo lists
8. Adding a feature to update existing todo lists based on new conversations or changes

## Conclusion

Using `ollama-instructor` for automated todo list generation offers a way to streamline project planning and task management. By leveraging AI to analyze conversations and generate structured task lists, teams can save time and ensure comprehensive project coverage. This example demonstrates how to integrate `ollama-instructor` into your workflow, providing a foundation for further customization and integration into your specific use cases.
