from unidecode import unidecode


def normalize_text(text: str) -> str:
    """Normalize text by removing accents, special characters and converting to lowercase."""
    return unidecode(
        text,
        errors="preserve",
    ).lower()
