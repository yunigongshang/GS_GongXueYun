from hashlib import md5

def create_sign(*args) -> str:
    return md5((''.join(args) + "3478cbbc33f84bd00d75d7dfa69e0daa").encode("utf-8")).hexdigest()