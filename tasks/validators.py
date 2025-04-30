from django.core.exceptions import ValidationError
from rest_framework import serializers

def validate_color(value):
    if not value.startswith("#") or len(value) != 7:
        raise serializers.ValidationError(
            "Color must be a valid hex code (e.g., #FFFFFF)."
        )
    return value