import re

NAME_RE = r'[a-z][a-z0-9]{4,}$'

def valid_name(n):
    return bool(re.match(NAME_RE, n))
