# TODO: create streaming tests. Provide complex models

import rich

from tests.llm_tests.test_create_character import test_stream_create_game_character, test_stream_create_game_characters
from tests.llm_tests.test_create_todos import test_stream_create_todos
from tests.llm_tests.test_create_person import test_stream_create_person

host = 'http://localhost:11434'
model= 'mistral:7b-instruct'
#model='llama3:8b-instruct-q8_0'
#model='phi3:instruct'

for chunk in test_stream_create_person(host=host, model=model):
    rich.print(chunk, flush=True)

for chunk in test_stream_create_game_character(host=host, model=model):
    rich.print(chunk)

for chunk in test_stream_create_game_characters(host=host, model=model):
    rich.print(chunk)

for chunk in test_stream_create_todos(host=host, model=model):
    rich.print(chunk)

