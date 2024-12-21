import pytest
from pydantic import BaseModel
from src.ollama_instructor import OllamaInstructor
from ollama import ChatResponse

class FriendInfo(BaseModel):
    name: str
    age: int
    is_available: bool

class FriendList(BaseModel):
    friends: list[FriendInfo]

@pytest.fixture
def client():
    """Fixture to create an OllamaInstructor client."""
    return OllamaInstructor(enable_logging=True, log_level='DEBUG')

@pytest.fixture
def user_prompt():
    """Fixture for the test prompt."""
    return '''I have two friends. The first is Ollama 22 years old busy saving
    the world, and the second is Alonso 23 years old and wants to hang out.
    Return a list of friends in JSON format'''

@pytest.mark.integration  # Mark as integration test since it requires Ollama server
class TestOllamaInstructor:
    def test_chat_completion(self, client, user_prompt):
        """Test the chat completion functionality."""
        response = client.chat_completion(
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

    def test_chat_stream(self, client, user_prompt):
        """Test the chat stream functionality."""
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

        # collect all chunks
        chunks: list = []
        # add all chunks
        expanded_chunk: str = ''
        for chunk in iterator_response:
            expanded_chunk += chunk.message.content
            chunk.message.content = expanded_chunk
            chunks.append(chunk)

        # Assertions
        #assert len(expanded_chunk) > 0  # Should receive at least one chunk
        assert all(isinstance(chunk, ChatResponse) for chunk in chunks)

        # Check the final chunk
        final_chunk = chunks[-1]
        assert final_chunk.done  # Last chunk should be marked as done

        # Validate the final content
        friend_list = FriendList.model_validate_json(final_chunk.message.content)
        assert len(friend_list.friends) == 2

        # Check specific friend details
        ollama = next(f for f in friend_list.friends if f.name == "Ollama")
        alonso = next(f for f in friend_list.friends if f.name == "Alonso")

        assert ollama.age == 22
        assert isinstance(ollama.is_available, bool)
        assert alonso.age == 23
        assert isinstance(alonso.is_available, bool)
