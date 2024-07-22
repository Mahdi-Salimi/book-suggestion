import re
from django.core.exceptions import ValidationError

def validate_rating(rating):
    if not isinstance(rating, int):
        raise ValidationError("Rating must be an integer.")
    if not (0 <= rating <= 5):
        raise ValidationError("Rating must be between 0 and 5.")


