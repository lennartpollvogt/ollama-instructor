import pytest
from ollama_instructor.ollama_instructor_client import OllamaInstructorClient

def test_extract_code_block_basic_json():
    client = OllamaInstructorClient(host='http://localhost:11434', debug=False)
    content = '''
    Here is a JSON code block:
    ```json
    {
        "name": "John Doe",
        "age": 30
    }
    ```
    '''
    expected = '''
    {
        "name": "John Doe",
        "age": 30
    }
    '''
    assert client.extract_code_block(content).strip() == expected.strip()

def test_extract_code_block_with_single_line_comments():
    client = OllamaInstructorClient(host='http://localhost:11434', debug=False)
    content = '''
    Here is a JSON code block with single line comments:
    ```json
    {
        "name": "John Doe", // This is a comment
        "age": 30 // Another comment
    }
    ```
    '''
    expected = '''
    {
        "name": "John Doe", 
        "age": 30 
    }
    '''
    assert client.extract_code_block(content).strip() == expected.strip()

def test_extract_code_block_with_multiline_comments():
    client = OllamaInstructorClient(host='http://localhost:11434', debug=False)
    content = '''
    Here is a JSON code block with multi-line comments:
    ```json
    {
        "name": "John Doe", /* This is a 
        multi-line comment */
        "age": 30
    }
    ```
    '''
    expected = '''
    {
        "name": "John Doe", 
        "age": 30
    }
    '''
    assert client.extract_code_block(content).strip() == expected.strip()

def test_extract_code_block_with_hash_comments():
    client = OllamaInstructorClient(host='http://localhost:11434', debug=False)
    content = '''
    Here is a JSON code block with hash comments:
    ```json
    {
        "name": "John Doe", # This is a hash comment
        "age": 30 # Another hash comment
    }
    ```
    '''
    expected = '''
    {
        "name": "John Doe", 
        "age": 30 
    }
    '''
    assert client.extract_code_block(content).strip() == expected.strip()

def test_extract_code_block_with_percent_comments():
    client = OllamaInstructorClient(host='http://localhost:11434', debug=False)
    content = '''
    Here is a JSON code block with percent comments:
    ```json
    {
        "name": "John Doe", % This is a percent comment
        "age": 30 % Another percent comment
    }
    ```
    '''
    expected = '''
    {
        "name": "John Doe", 
        "age": 30 
    }
    '''
    assert client.extract_code_block(content).strip() == expected.strip()

def test_extract_code_block_with_mixed_comments():
    client = OllamaInstructorClient(host='http://localhost:11434', debug=False)
    content = '''
    Here is a JSON code block with mixed comments:
    ```json
    {
        "name": "John Doe", // Single-line comment
        "age": 30, /* Multi-line
        comment */ # Hash comment
    }
    ```
    '''
    expected = '''
    {
        "name": "John Doe", 
        "age": 30,  
    }
    '''
    assert client.extract_code_block(content).strip() == expected.strip()

def test_extract_code_block_no_code_block():
    client = OllamaInstructorClient(host='http://localhost:11434', debug=False)
    content = '''
    Here is some text without a JSON code block.
    '''
    assert client.extract_code_block(content) == 'Code block not found'

def test_extract_code_block_incorrect_format():
    client = OllamaInstructorClient(host='http://localhost:11434', debug=False)
    content = '''
    Here is a JSON code block with incorrect format:
    ```json
    {
        "name": "John Doe",
        "age": 30
    '''
    assert client.extract_code_block(content) == 'Code block end not found'

def test_extract_code_block_empty_string():
    client = OllamaInstructorClient(host='http://localhost:11434', debug=False)
    content = ''
    assert client.extract_code_block(content) == 'Code block not found'

def test_extract_code_block_multiple_blocks():
    client = OllamaInstructorClient(host='http://localhost:11434', debug=False)
    content = '''
    Here is the first JSON code block:
    ```json
    {
        "name": "John Doe",
        "age": 30
    }
    ```
    And here is the second JSON code block:
    ```json
    {
        "city": "New York",
        "country": "USA"
    }
    ```
    '''
    expected = '''
    {
        "name": "John Doe",
        "age": 30
    }
    '''
    assert client.extract_code_block(content).strip() == expected.strip()

def test_extract_code_block_with_leading_trailing_text():
    client = OllamaInstructorClient(host='http://localhost:11434', debug=False)
    content = '''
    Some leading text.
    ```json
    {
        "name": "John Doe",
        "age": 30
    }
    ```
    Some trailing text.
    '''
    expected = '''
    {
        "name": "John Doe",
        "age": 30
    }
    '''
    assert client.extract_code_block(content).strip() == expected.strip()

# Add more test cases as needed

# pytest test_extract_code_block.py
