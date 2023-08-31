import json
import xmltodict
from datetime import datetime


# FILE FUNCTIONS

def json_to_dict(json_file_path):
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"File '{json_file_path}' not found.")
    except json.JSONDecodeError:
        print(f"Unable to parse JSON file: '{json_file_path}'.")
    except Exception as e:
        print(f"An error occurred while importing JSON: {e}")


def xml_to_dict(xml_file_path):
    try:
        with open(xml_file_path, 'r') as file:
            xml_data = file.read()
            return xmltodict.parse(xml_data)
    except FileNotFoundError:
        print(f"Error: XML file not found at '{xml_file_path}'")
        return None
    except Exception as e:
        print(f"Error: Unable to parse XML file. Reason: {str(e)}")
        return None
 
    
def save_to_json(dict, json_path):
    with open(json_path, "w") as file:
        json.dump(dict, file)


# TEXT FUNCTIONS

def keep_alpha_characters(input_string):
    return ''.join(char for char in input_string if char.isalpha() or char.isspace())

def keep_numeric_characters(input_string):
    return ''.join(char for char in input_string if char.isdigit())

def capitalize_each_word(input_string):
    return input_string.title()

def remove_wrong_whitespaces(input_string):
    return " ".join(input_string.split())


def is_valid_cpf(cpf):
    # Remover caracteres não numéricos do CPF
    cpf = ''.join(filter(str.isdigit, cpf))

    # Verificar se o CPF possui 11 dígitos
    if len(cpf) != 11:
        return False

    # Verificar se todos os dígitos são iguais (CPF inválido)
    if cpf == cpf[0] * 11:
        return False

    # Calcular os dígitos verificadores
    total = 0
    for i in range(9):
        total += int(cpf[i]) * (10 - i)
    digit1 = 11 - (total % 11)
    if digit1 > 9:
        digit1 = 0

    total = 0
    for i in range(10):
        total += int(cpf[i]) * (11 - i)
    digit2 = 11 - (total % 11)
    if digit2 > 9:
        digit2 = 0

    # Verificar se os dígitos verificadores calculados coincidem com os dígitos do CPF
    if int(cpf[9]) != digit1 or int(cpf[10]) != digit2:
        return False

    return True

def is_valid_date_format(date_string):
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False
