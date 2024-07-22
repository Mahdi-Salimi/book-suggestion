import re
from django.core.exceptions import ValidationError

def validate_password_length(password):
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")

def validate_password_uppercase(password):
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Password must contain at least one uppercase letter.")

def validate_password_lowercase(password):
    if not re.search(r'[a-z]', password):
        raise ValidationError("Password must contain at least one lowercase letter.")

def validate_password_digit(password):
    if not re.search(r'[0-9]', password):
        raise ValidationError("Password must contain at least one digit.")

def validate_password_special_char(password):
    if not re.search(r'[\W_]', password):
        raise ValidationError("Password must contain at least one special character.")

def validate_password(password):
    validators = [
        validate_password_length,
        validate_password_uppercase,
        validate_password_lowercase,
        validate_password_digit,
        validate_password_special_char,
    ]
    
    for validator in validators:
        validator(password)