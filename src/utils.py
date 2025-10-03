import uuid

def next_id(prefix: str) -> str:
    """
    Generate a unique ID with the given prefix.
    Example: next_id("usr") -> 'usr-9f1c2d7e-12a4'
    """
    if not prefix or not isinstance(prefix, str):
        raise ValueError("Prefix must be a non-empty string")
    unique_part = uuid.uuid4().hex[:12]  # 12 chars for better uniqueness
    return f"{prefix}-{unique_part}"
