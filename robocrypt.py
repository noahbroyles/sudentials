#!/usr/bin/python3

#        ____        __             _____
#       / __ \____  / /_  ____     |__  /
#      / /_/ / __ \/ __ \/ __ \     /_ <
#     / _, _/ /_/ / /_/ / /_/ /   ___/ /
#    /_/ |_|\____/_.___/\____/   /____/

import os
import base64

from string import ascii_uppercase
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def get_salt(salt_file='/var/secure/robocrypt.salt'):
    with open(salt_file, 'rb') as sf:
        salt = sf.read()
    return salt


CIPHER_WHEEL_N = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h', 8: 'i', 9: 'j', 10: 'k', 11: 'l', 12: 'm', 13: 'n', 14: 'o', 15: 'p', 16: 'q', 17: 'r', 18: 's', 19: 't', 20: 'u', 21: 'v', 22: 'w', 23: 'x', 24: 'y', 25: 'z'}
CIPHER_WHEEL_L = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8, 'j': 9, 'k': 10, 'l': 11, 'm': 12, 'n': 13, 'o': 14, 'p': 15, 'q': 16, 'r': 17, 's': 18, 't': 19, 'u': 20, 'v': 21, 'w': 22, 'x': 23, 'y': 24, 'z': 25}


def cipher(message: bytes, shift: int):
    message = message.decode()
    cipher_string = ''
    for char in message:
        if char.upper() not in ascii_uppercase:
            cipher_string += char
            continue
        UPPER = True if char in ascii_uppercase else False
        pos = CIPHER_WHEEL_L[char.lower()] + shift
        while pos > 25:
            pos -= 26
        new_char = CIPHER_WHEEL_N[pos]
        cipher_string += new_char if not UPPER else new_char.upper()

    return cipher_string.encode()


def decipher(message: bytes, shift: int):
    message = message.decode()
    cipher_string = ''
    for char in message:
        if char.upper() not in ascii_uppercase:
            cipher_string += char
            continue
        UPPER = True if char in ascii_uppercase else False
        pos = CIPHER_WHEEL_L[char.lower()] - shift
        while pos < 0:
            pos = pos + 26
        new_char = CIPHER_WHEEL_N[pos]
        cipher_string += new_char if not UPPER else new_char.upper()

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
