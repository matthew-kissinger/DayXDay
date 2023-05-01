from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


def generate_key(password, salt):
  kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100000,
  )
  key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
  return key, salt


def encrypt(message, password, salt):
  key, salt = generate_key(password, salt)
  f = Fernet(key)
  encrypted_message = f.encrypt(message.encode())
  return encrypted_message, salt


def decrypt(encrypted_message, password, salt):
  key, _ = generate_key(password, salt)
  f = Fernet(key)
  decrypted_message = f.decrypt(encrypted_message).decode()
  return decrypted_message
