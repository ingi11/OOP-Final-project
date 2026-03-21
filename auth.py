import hashlib
import re

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------------- PASSWORD VALIDATION ----------------
def strong_password(password):
    if len(password) < 8:
        return False
    if not re.search("[A-Z]", password):
        return False
    if not re.search("[a-z]", password):
        return False
    if not re.search("[0-9]", password):
        return False
    if not re.search("[@#$%^&*!]", password):
        return False
    return True
