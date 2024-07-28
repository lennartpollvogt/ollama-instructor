from pydantic import BaseModel
from enum import Enum
from typing import List

from ollama_instructor.ollama_instructor_client import OllamaInstructorClient

class Gender(Enum):
    MALE = 'male'
    FEMALE = 'female'

class Weapon(Enum):
    SWORD = 'sword'
    AXE = 'axe'
    BOW = 'bow'

class GameCharacter(BaseModel):
    '''
    This model defines a character of a game.
    A single character has a name, an age, a gender and a weapon.
    The weapon is defined by the Weapon enum and the gender is defined by the Gender enum.s
    '''
    name: str
    age: int
    gender: Gender
    weapon: Weapon

    class Config:
        extra = 'forbid'

class ListOfCharacter(BaseModel):
    '''
    This model defines an array of characters of a game.
    A single character is defined by the GameCharacter model.
    Regarding GameCharacter, a single character has a name, an age, a sex, and a weapon.
    '''
    characters: List[GameCharacter]

    class Config:
        extra = 'forbid'


def test_create_game_character(host: str, model: str, **kwargs):
    client = OllamaInstructorClient(
        host=host,
        debug=True
    )
    response = client.chat_completion(
        model=model,
        pydantic_model=GameCharacter,
        messages=[
            {
                'role': 'user',
                'content': 'Create a character for a game. The name is John, age 25, male, and uses a sword.'
            }
        ],
        **kwargs,
    )

    return response

def test_stream_create_game_character(host: str, model: str, **kwargs):
    client = OllamaInstructorClient(
        host=host,
    )
    response = client.chat_completion_with_stream(
        model=model,
        pydantic_model=GameCharacter,
        messages=[
            {
                'role': 'system',
                'content': 'You are a helpful assistant!'
            },
            {
                'role': 'user',
                'content': 'Create a character for a game. The name is John, age 25, male, and uses a sword.'
            }
        ],
        **kwargs,
    )

    for chunk in response:
        yield chunk

def test_create_game_characters(host: str, model: str, **kwargs):
    client = OllamaInstructorClient(
        host=host,
    )
    response = client.chat_completion(
        model=model,
        pydantic_model=ListOfCharacter,
        messages=[
            {
                'role': 'user',
                'content': 'Create a list of characters for a game. The name is John, age 25, male, and uses a sword. The name is Jane, age 26, female, and uses a bow.'
            }
        ],
        **kwargs,
    )

    return response


def test_stream_create_game_characters(host: str, model: str, **kwargs):
    client = OllamaInstructorClient(
        host=host,
    )
    response = client.chat_completion_with_stream(
        model=model,
        pydantic_model=ListOfCharacter,
        messages=[
            {
                'role': 'user',
                'content': 'Create a list of characters for a game. The name is John, age 25, male, and uses a sword. The name is Jane, age 26, female, and uses a bow.'
            }
        ],
        **kwargs,
    )

    for chunk in response:
        yield chunk