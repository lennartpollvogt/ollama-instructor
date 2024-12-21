import asyncio
from pydantic import BaseModel
from ollama_instructor import OllamaInstructorAsync

# Define your Pydantic models
class FriendInfo(BaseModel):
    name: str
    age: int
    is_available: bool

class FriendList(BaseModel):
    friends: list[FriendInfo]

# Common prompt
user_prompt = '''I have two friends. The first is Ollama 22 years old busy saving
the world, and the second is Alonso 23 years old and wants to hang out.
Return a list of friends in JSON format'''

async def main():
    # Create the async client
    client = OllamaInstructorAsync(enable_logging=True, log_level='DEBUG')

    # Get streaming response
    async for chunk in await client.chat_stream(
        format=FriendList,
        model='llama3.2:latest',
        messages=[
            {
                'role': 'user',
                'content': user_prompt
            }
        ]
    ):
        print(chunk)

if __name__ == "__main__":
    asyncio.run(main())
