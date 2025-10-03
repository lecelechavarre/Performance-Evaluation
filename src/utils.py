import uuid

def next_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"
