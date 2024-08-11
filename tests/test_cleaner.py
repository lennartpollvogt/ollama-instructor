from pydantic import BaseModel
from typing import Optional, List
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



# NESTED MODEL
class Address(BaseModel):
    street: str
    city: str
    zip_code: int

class Person(BaseModel):
    name: str
    age: int
    email: Optional[str] = None
    addresses: List[Address]

def test_clean_nested_data_with_complex_structure():
    data = {
        "name": "John Doe",
        "age": "invalid",
        "email": "john@example.com",
        "addresses": [
            {"street": "123 Main St", "city": "Springfield", "zip_code": 12345},
            {"street": "456 Elm St", "city": "Shelbyville", "zip_code": "invalid"},
            {"street": "789 Oak Rd", "city": "Capital City", "zip_code": 67890}
        ]
    }

    PartialPerson = create_partial_model(Person)
    cleaned_data = clean_nested_data_with_error_dict(data, PartialPerson)

    assert cleaned_data == {
        "name": "John Doe",
        "age": None,
        "email": "john@example.com",
        "addresses": [
            {"street": "123 Main St", "city": "Springfield", "zip_code": 12345},
            {"street": "456 Elm St", "city": "Shelbyville", "zip_code": None},
            {"street": "789 Oak Rd", "city": "Capital City", "zip_code": 67890}
        ]
    }

    # Additional assertions to check specific aspects
    assert cleaned_data["age"] is None
    assert len(cleaned_data["addresses"]) == 3
    assert cleaned_data["addresses"][1]["zip_code"] is None
    assert cleaned_data["addresses"][0]["zip_code"] == 12345
    assert cleaned_data["addresses"][2]["zip_code"] == 67890

def test_clean_nested_data_with_invalid_nested_object():
    data = {
        "name": "Jane Doe",
        "age": 30,
        "addresses": [
            {"street": "123 Main St", "city": "Springfield", "zip_code": 12345},
            {"street": 123, "city": "Shelbyville", "zip_code": 54321},  # Invalid street
            {"street": "789 Oak Rd", "city": "Capital City", "zip_code": 67890}
        ]
    }

    PartialPerson = create_partial_model(Person)
    cleaned_data = clean_nested_data_with_error_dict(data, PartialPerson)

    assert cleaned_data == {
        "name": "Jane Doe",
        "age": 30,
        "addresses": [
            {"street": "123 Main St", "city": "Springfield", "zip_code": 12345},
            {"street": None, "city": "Shelbyville", "zip_code": 54321},
            {"street": "789 Oak Rd", "city": "Capital City", "zip_code": 67890}
        ]
    }

    assert cleaned_data["addresses"][1]["street"] is None
    assert cleaned_data["addresses"][1]["city"] == "Shelbyville"
    assert cleaned_data["addresses"][1]["zip_code"] == 54321

def test_clean_nested_data_with_missing_fields():
    data = {
        "name": "Alice Smith",
        "addresses": [
            {"street": "123 Main St", "city": "Springfield"},  # Missing zip_code
            {"street": "456 Elm St", "city": "Shelbyville", "zip_code": 54321}
        ]
    }

    PartialPerson = create_partial_model(Person)
    cleaned_data = clean_nested_data_with_error_dict(data, PartialPerson)

    assert cleaned_data == {
        "name": "Alice Smith",
        "addresses": [
            {"street": "123 Main St", "city": "Springfield", "zip_code": None},
            {"street": "456 Elm St", "city": "Shelbyville", "zip_code": 54321}
        ]
    }

    assert "age" not in cleaned_data
    assert cleaned_data["addresses"][0]["zip_code"] is None

# pytest test_cleaner.py