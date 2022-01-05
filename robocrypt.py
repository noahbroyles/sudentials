
#     ____        __             __ __
#    / __ \____  / /_  ____     / // /
#   / /_/ / __ \/ __ \/ __ \   / // /_
#  / _, _/ /_/ / /_/ / /_/ /  /__  __/
# /_/ |_|\____/_.___/\____/     /_/

import os
import base64

from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def get_salt(salt_file='/var/secure/robocrypt.salt'):
    with open(salt_file, 'rb') as sf:
        salt = sf.read()
    return salt


def cipher(message: bytes, shift: int):
    message = message.decode()
    cipher_string = ''
    for i in range(len(message)):
        pos = ord(message[i]) + shift + i
        while pos > 1114110:
            pos -= 1114111
        cipher_string += chr(pos)

    return cipher_string.encode()


def decipher(message: bytes, shift: int):
    message = message.decode()
    cipher_string = ''
    for i in range(len(message)):
        pos = ord(message[i]) - shift - i
        while pos < 0:
            pos = pos + 1114111
        cipher_string += chr(pos)

    return cipher_string.encode()


def get_kdf():
    return PBKDF2HMAC(
        algorithm=hashes.SHA512_224(),
        length=32,
        salt=get_salt(),
        iterations=724,
        backend=default_backend()
    )


def encrypt(message: bytes, password: bytes, shift: int = None):
    key = base64.urlsafe_b64encode(get_kdf().derive(password))
    f = Fernet(key)
    encrypted_bytes = f.encrypt(message)

    if shift is not None:
        return cipher(encrypted_bytes, shift)
    return encrypted_bytes


class DecryptionError(Exception):
    def __init__(self):
        super(DecryptionError, self).__init__()


def decrypt(message: bytes, password: bytes, shift: int = None):
    key = base64.urlsafe_b64encode(get_kdf().derive(password))
    f = Fernet(key)

    if shift is not None:
        message = decipher(message, shift)
    try:
        return f.decrypt(message)
    except InvalidToken:
        raise DecryptionError


def encrypt_file(filepath: str, password: str, shift: int = 17):
    chunks = filepath.split('/')
    path = '/'.join(chunks[:-1])
    filename, ext = chunks[-1].split('.')

    with open(filepath, 'rb') as f:
        content = f.read()

    encrypted_content = encrypt(content, password.encode(), shift=shift)

    with open(f"{path}/{filename}.{ext}.robo", 'wb') as enc_f:
        enc_f.write(encrypted_content)

    os.remove(filepath)


def decrypt_file(filepath: str, password: str, shift: int = 17):
    chunks = filepath.split('/')
    path = '/'.join(chunks[:-1])
    filename, ext, _ = chunks[-1].split('.')

    with open(filepath, 'rb') as f:
        encrypted_content = f.read()

    try:
        decrypted_content = decrypt(encrypted_content, password=password.encode(), shift=shift)
    except AttributeError:
        raise DecryptionError

    with open(f"{path}/{filename}.{ext}", 'wb') as dcrp_f:
        dcrp_f.write(decrypted_content)

    os.remove(filepath)


def read_encrypted_file(filepath: str, password: str, shift: int = 17) -> bytes:
    with open(filepath, 'rb') as f:
        encrypted_content = f.read()

    try:
        decrypted_content = decrypt(encrypted_content, password=password.encode(), shift=shift)
    except AttributeError:
        raise DecryptionError

    return decrypted_content
