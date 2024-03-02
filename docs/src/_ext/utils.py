import hashlib


def generate_id(name: str):
    return "id-" + hashlib.md5(name.encode()).hexdigest()[:8]
