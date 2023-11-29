from cryptography.fernet import Fernet

def generate_key():
    return Fernet.generate_key()

def encrypt(value, key):
    return Fernet(key).encrypt(value.encode())

def decrypt(value, key):
    return Fernet(key).decrypt(value).decode()
