from tests.llm_tests.test_classify_article import test_text_classification
from tests.llm_tests.test_create_character import test_create_game_character, test_create_game_characters
from tests.llm_tests.test_create_todos import test_create_todos
import rich

host = 'http://localhost:11434'
model= 'gemma:2b-instruct'

# format == 'json'
rich.print(test_text_classification(host=host,model=model, retries=2, allow_partial=True))

rich.print(test_create_game_character(host=host, model=model, retries=2, allow_partial=True))

rich.print(test_create_game_characters(host=host,model=model, retries=2, allow_partial=False))


# format == ''
print('1. test_text_classification')
rich.print(test_text_classification(host=host,model=model, retries=2, allow_partial=False, format=''))

print('2. test_create_game_character')
rich.print(test_create_game_character(host=host, model=model, retries=2, allow_partial=False, format=''))

print('3. test_create_game_characters')
rich.print(test_create_game_characters(host=host, model=model, retries=2, allow_partial=False, format=''))

print('4. test_create_todos')
rich.print(test_create_todos(host=host, model=model, retries=3, allow_partial=False, format=''))