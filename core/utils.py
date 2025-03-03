"""
Utility functions for Kingdom Chronicles
"""

def format_error_message(error_dict):
    """
    Formats error dictionary into a more readable format
    """
    formatted_errors = {}
    for field, errors in error_dict.items():
        if isinstance(errors, list):
            formatted_errors[field] = errors[0] if errors else ""
        else:
            formatted_errors[field] = errors
    return formatted_errors

def generate_unique_code(length=8):
    """
    Generates a unique alphanumeric code of specified length
    """
    import random
    import string
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))