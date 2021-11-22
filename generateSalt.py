#!/usr/bin/python3

import sys
from os import urandom


def regen_salt(salt_file: str, length: int):
    with open(salt_file, 'wb') as sf:
        sf.write(urandom(length))


if __name__ == '__main__':
    try:
        leng = int(sys.argv[1])
        regen_salt(salt_file='/var/secure/robocrypt.salt', length=leng)
    except IndexError:
        print("USAGE: \n\tgenerateSalt <length>")
    except ValueError:
        print("Salt length must be an integer")
