from pydantic import BaseModel
from ollama_instructor import OllamaInstructor

# Define your Pydantic models
class FriendInfo(BaseModel):
    name: str
    age: int
    is_available: bool

class FriendList(BaseModel):
    friends: list[FriendInfo]

# Create the client
client = OllamaInstructor()

# Common prompt
user_prompt = '''I have two friends. The first is Ollama 22 years old busy saving
the world, and the second is Alonso 23 years old and wants to hang out.
Return a list of friends in JSON format'''


client = OllamaInstructor(enable_logging=True, log_level='DEBUG')

#####

iterator_response = client.chat_stream(
    format=FriendList,
    model='llama3.2:latest',
    messages=[
        {
            'role': 'user',
            'content': user_prompt
        }
    ]
)

for chunk in iterator_response:
    print(chunk)
