from tests.llm_tests.test_classify_article import test_text_classification
from tests.llm_tests.test_create_character import test_create_game_character, test_create_game_characters
import rich

host = 'http://localhost:11434'
#model= 'mistral:7b-instruct'
#model='phi3:instruct'
model='dolphin-llama3'

rich.print(test_text_classification(host=host,model=model, retries=2, allow_partial=True))

rich.print(test_create_game_character(host=host, model=model, retries=2, allow_partial=True))

rich.print(test_create_game_characters(host=host,model=model, retries=2, allow_partial=True))