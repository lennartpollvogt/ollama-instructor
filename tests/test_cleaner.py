from pydantic import BaseModel
from typing import Optional
import pytest
import json

from ollama_instructor.cleaner import create_partial_model, clean_nested_data_with_error_dict

class TestModel(BaseModel):
    __test__ = False
    name: str
    age: int
    optional: str = None

def test_create_partial_model():
    PartialModel = create_partial_model(TestModel)
    assert PartialModel.model_fields['name'].default is None
    assert PartialModel.model_fields['age'].default is None
    assert PartialModel.model_fields['optional'].default is None
    assert PartialModel(name='Jason', age=20, optional='test')


class SampleModel(BaseModel):
    name: str
    age: Optional[int] = None
    email: str

def test_clean_data_valid_input():
    input_data = json.dumps({"name": "John Doe", "age": 30, "email": "john@example.com"})
    expected_output = {"name": "John Doe", "age": 30, "email": "john@example.com"}
    
    cleaned_data = clean_nested_data_with_error_dict(input_data, SampleModel)
    assert cleaned_data == expected_output, "The cleaned data should match the expected valid output."

def test_clean_data_missing_field():
    input_data = json.dumps({"name": "John Doe", "email": "john@example.com"})
    expected_output = {"name": "John Doe", "email": "john@example.com"}
    
    cleaned_data = clean_nested_data_with_error_dict(input_data, SampleModel)
    assert cleaned_data == expected_output, "The cleaned data should handle optional missing fields."

def test_clean_data_with_extra_field():
    input_data = json.dumps({"name": "John Doe", "age": 30, "email": "john@example.com", "extra": "unexpected"})
    expected_output = {"name": "John Doe", "age": 30, "email": "john@example.com"}
    
    cleaned_data = clean_nested_data_with_error_dict(input_data, SampleModel)
    assert cleaned_data == expected_output, "The cleaned data should not contain extra fields."

def test_clean_data_with_invalid_type():
    input_data = json.dumps({"name": "John Doe", "age": "thirty", "email": "john@example.com"})
    expected_output = {"name": "John Doe", "age": None, "email": "john@example.com"}
    
    cleaned_data = clean_nested_data_with_error_dict(input_data, SampleModel)
    assert cleaned_data == expected_output, "The cleaned data should set invalid types to None."


# pytest test_cleaner.py