import uuid


# SQlite doesn't support UUID, that's why we fake it
def fake_uuid():
    return str(uuid.uuid4())
