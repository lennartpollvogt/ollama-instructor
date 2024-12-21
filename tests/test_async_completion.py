import pytest
import pytest_asyncio  # Note the import change
from pydantic import BaseModel
from src.ollama_instructor import OllamaInstructorAsync
from ollama import ChatResponse

class FriendInfo(BaseModel):
    name: str
    age: int
    is_available: bool

class FriendList(BaseModel):
    friends: list[FriendInfo]

@pytest_asyncio.fixture
async def async_client():
    """Fixture to create an OllamaInstructorAsync client."""
    client = OllamaInstructorAsync(enable_logging=True, log_level='DEBUG')
    #try:
    yield client
    #finally:
        #await client.

@pytest.fixture
def user_prompt():
    """Fixture for the test prompt."""
    return '''I have two friends. The first is Ollama 22 years old busy saving
    the world, and the second is Alonso 23 years old and wants to hang out.
    Return a list of friends in JSON format'''

@pytest.mark.integration
@pytest.mark.asyncio
class TestOllamaInstructorAsyncCompletion:
    async def test_chat_completion(self, async_client, user_prompt):
        """Test the async chat completion functionality."""
        response = await async_client.chat_completion(
            format=FriendList,
            model='llama3.2:latest',
            messages=[
                {
                    'role': 'user',
                    'content': user_prompt
                }
            ]
        )

        # Assertions
        assert isinstance(response, ChatResponse)
        assert response.message.content is not None

        # Validate the response content
        friend_list = FriendList.model_validate_json(response.message.content)
        assert len(friend_list.friends) == 2

        # Check specific friend details
        ollama = next(f for f in friend_list.friends if f.name == "Ollama")
        alonso = next(f for f in friend_list.friends if f.name == "Alonso")

        assert ollama.age == 22
        assert isinstance(ollama.is_available, bool)
        assert alonso.age == 23
        assert isinstance(alonso.is_available, bool)
