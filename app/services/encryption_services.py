import os
from cryptography.fernet import Fernet
import hashlib

# Path where you want to store the key
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
KEY_PATH = os.path.join(BASE_DIR, 'master.key')

def generate_and_store_master_key():
    """Generate a master key and store it only if it doesn't already exist."""
    if not os.path.exists(KEY_PATH):
        key = Fernet.generate_key()
        with open(KEY_PATH, 'wb') as f:
            f.write(key)

def load_master_key():
    """Load the stored master key from file."""
    if not os.path.exists(KEY_PATH):
        raise FileNotFoundError("Master key file not found. Did you forget to generate it?")
    with open(KEY_PATH, 'rb') as f:
        return f.read()

def get_fernet():
    """Returns a Fernet instance using the loaded master key."""
    key = load_master_key()
    return Fernet(key)

def hash_password(password: str) -> str:
    sha256 = hashlib.sha256()
    sha256.update(password.encode('utf-8'))
    return sha256.hexdigest()