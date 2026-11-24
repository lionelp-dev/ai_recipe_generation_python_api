"""Small presentation helpers for Pydantic form errors."""

from pydantic import ValidationError


_FRENCH_MESSAGES = {
    "missing": "Ce champ est obligatoire.",
    "string_too_short": "La valeur est trop courte.",
    "string_too_long": "La valeur est trop longue.",
    "string_type": "Saisissez du texte.",
    "int_parsing": "Saisissez un nombre entier.",
    "int_type": "Saisissez un nombre entier.",
    "greater_than": "La valeur doit être supérieure à zéro.",
    "greater_than_equal": "La valeur ne peut pas être négative.",
    "decimal_parsing": "Saisissez un nombre valide.",
    "decimal_type": "Saisissez un nombre valide.",
    "decimal_max_digits": "Le nombre comporte trop de chiffres.",
    "decimal_max_places": "Le nombre comporte trop de décimales.",
    "list_type": "Saisissez une liste valide.",
    "json_invalid": "Les données de la recette sont invalides.",
}


def form_errors(error: ValidationError) -> dict[str, str]:
    """Convert Pydantic locations to the dotted keys consumed by the React form."""

    return {
        ".".join(map(str, detail["loc"])) or "recipe": _message(detail)
        for detail in error.errors()
    }


def _message(detail: dict[str, object]) -> str:
    error_type = str(detail["type"])
    return _FRENCH_MESSAGES.get(error_type, str(detail["msg"]))
