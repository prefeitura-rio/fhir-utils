from unittest import mock
from fhir_utils.utils import (
    json_to_dict,
    xml_to_dict,
    keep_alpha_characters,
    keep_numeric_characters,
    capitalize_each_word,
    remove_wrong_whitespaces,
    is_valid_cpf,
    is_valid_date_format)

def test_json_to_dict():
    mock_open = mock.mock_open(read_data='{"key": "value"}')
    with mock.patch('builtins.open', mock_open):
        result = json_to_dict('test.json')
    assert result == {"key": "value"}

def test_xml_to_dict():
    mock_open = mock.mock_open(read_data='<root><key>value</key></root>')
    with mock.patch('builtins.open', mock_open):
        result = xml_to_dict('test.xml')
    assert result == {"root": {"key": "value"}}

def test_keep_alpha_characters():
    result = keep_alpha_characters('abc 123')
    assert result == 'abc '

def test_keep_numeric_characters():
    result = keep_numeric_characters('abc123')
    assert result == '123'

def test_capitalize_each_word():
    result = capitalize_each_word('hello world')
    assert result == 'Hello World'

def test_remove_wrong_whitespaces():
    result = remove_wrong_whitespaces(' hello   world  ')
    assert result == 'hello world'

def test_is_valid_cpf():
    result = is_valid_cpf('87877669810')
    assert result == True

    result = is_valid_cpf('1234567890')
    assert result == False

def test_is_valid_date_format():
    result = is_valid_date_format('2022-01-01')
    assert result == True

    result = is_valid_date_format('01-01-2022')
    assert result == False