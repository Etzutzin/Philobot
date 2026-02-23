import re


UNSAFE_PATTERNS = [
    r"(hate|attack|harm|violence|suicide|self-harm)",
    # Add more as needed
]

def is_low_quality(text: str) -> bool:
    """Check if input is low quality or unsafe."""
    
    if len(set(text)) < 5:
        return True
    if re.fullmatch(r"[a-zA-Z\s]+", text) and len(text.split()) < 3:
        return True
    
    text_lower = text.lower()
    for pattern in UNSAFE_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    
    return False
    
def validate_quote(user_quote: str) -> dict:
    if not user_quote or not user_quote.strip():
        return {"error": "Empty input"}

    cleaned = user_quote.strip()

    if len(cleaned) < 5:
        return {"error": "Quote too short (min 5 chars)"}

    if len(cleaned) > 500:
        return {"error": "Quote too long (max 500 chars)"}

    if is_low_quality(cleaned):
        return {"error": "Input doesn't appear to be a meaningful quote"}

    return {"valid": True, "cleaned": cleaned}


def is_low_quality(text: str) -> bool:
    if len(set(text)) < 5:
        return True

    if re.fullmatch(r"[a-zA-Z\s]+", text) and len(text.split()) < 3:
        return True


    return False

