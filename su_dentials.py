import os
import json
import robocrypt

from typing import Any
from addict import Dict


__all__ = [
    'CREDS_LOCATION',
    'CredentialsLockedError',
    'InvalidPassword',
    'CredentialOverrideError',
    'Credentials'
]


CREDS_LOCATION = '/var/secure/creds.json'


class CredentialsLockedError(Exception):
    def __init__(self, error_message: str):
        self.error_message = error_message
        super().__init__(error_message)


class InvalidPassword(Exception):
    def __init__(self, error_message):
        self.error_message = error_message
        super().__init__(error_message)


class CredentialOverrideError(Exception):
    def __init__(self, error_message):
        super().__init__(error_message)


class Credentials:
    def __init__(self, password: str = None, credentials_file=CREDS_LOCATION):
        """
Create a Credentials instance.
        :param password: Specifies the decryption password to read the credentials with
        :param credentials_file: Specifies the unencrypted credentials file to base off of (Defaults to '/var/secure/creds.json')
        """
        self._creds_path = credentials_file
        self._locked_path = f"{credentials_file}.robo"
        self._salt_file = '/var/secure/robocrypt.salt'

        if not os.path.exists(credentials_file) and not os.path.exists(self._locked_path):
            raise FileNotFoundError(f'Neither a locked or unlocked credentials file could be found. Make sure you\'re running as sudo!')

        self.__password = password
        self.__store = Dict()

    def state(self) -> str:
        """
Get the state of the credentials file: 'locked' or 'unlocked' if the creds file is unencrypted or decrypted
        :return: 'locked' or 'unlocked'
        """
        if os.path.exists(self._creds_path) and not os.path.exists(self._locked_path):
            return 'unlocked'
        else:
            return 'locked'

    def set_password(self, new_password: str):
        """
Set's a password for the credentials manager to use when locking and unlocking the system files.
If a password has been set already, you will be asked to use change_password() instead.
        :param new_password: The password to set.
        :return: None
        """
        if self.__password is None:
            self.__password = new_password
        else:
            print('please use change_password instead.')

    def change_password(self, old_password: str, new_password: str):
        """
Changes the credentials manager password from the old password to a new password.
        :param old_password: The old password that the credentials are encrypted with
        :param new_password: The password to change to
        :return: None
        """
        try:
            self.unlock(password=old_password)
            self.__password = new_password
            self.lock()
        except AttributeError:
            raise InvalidPassword('The old password specified is not correct.')

    def forget_password(self):
        """
Forgets the local password so that in order to lock or unlock you must specify a password.
        :return:
        """
        self.__password = None

    def lock(self, password: str = None):
        """
Encrypts the credentials file on disk
        :param password: The password to use (Will use the default pw for the current object unless a different one is specified)
        :return: None
        """
        if self.state() == 'locked':
            return
        robocrypt.encrypt_file(filepath=self._creds_path, password=password if password else self.__password, shift=17)

    def unlock(self, password: str = None):
        """
Decrypts the credentials file on disk
        :param password: The password to use (Will use the default pw for the current object unless a different one is specified)
        :return: None
        """
        if self.state() == 'unlocked':
            return
        try:
            robocrypt.decrypt_file(filepath=self._locked_path, password=password if password else self.__password, shift=17)
        except robocrypt.DecryptionError:
            raise CredentialsLockedError('Unable to unlock credentials with the provided password.')

    def change_salt(self, salt_length: int):
        """
Changes the salt used to encrypt the credentials with.
        :param salt_length: any integer length for the new salt
        :return: None
        """
        self.unlock()
        with open(self._salt_file, 'wb') as sf:
            sf.write(os.urandom(salt_length))
        self.lock()

    def engage(self):
        """
Loads the credentials into the environment as environment variables and sets up the global creds as attributes.
        :return: None
        """
        if self.state() == 'locked':
            creds = json.loads(robocrypt.read_encrypted_file(self._locked_path, password=self.__password, shift=17))
        elif self.state() == 'unlocked':
            with open(self._creds_path, 'r') as cf:
                creds = json.load(cf)
            self.lock()
        self.__store = Dict(env=creds['ENV'], globs=creds['GLOBAL'])
        for key, value in self.__store.env.items():
            os.environ[key] = value

    def disengage(self):
        """
Removes the credentials from the environment and the attributes.
        :return: None
        """
        for key in self.__store.env.keys():
            del os.environ[key]
        self.__store.clear()

    def write(self):
        """
Saves the local credentials to the disk.
        :return: None
        """
        self.unlock()
        data = {
            "ENV": {k: v for k, v in self.__store.env.items()},
            "GLOBAL": {k: v for k, v in self.__store.globs.items()}
        }
        with open(self._creds_path, 'wb') as of:
            json.dump(data, of, indent=4)
        self.lock()

    def update_item(self, key, new_value, scope: str = 'env'):
        """
Updates a password or credential in the given scope with a new value.
        :param key: The name of the credential
        :param new_value: The new value
        :param scope: The scope where the credential lives, 'env' for environment variables or 'global' for attributes. Defaults to env.
        :return: None
        """
        if scope.lower() == 'env':
            self.__store.env[key] = new_value
        elif scope.lower() == 'global':
            self.__store.globs[key] = new_value
        self.write()

    def add_item(self, key, value, scope: str = 'env'):
        """
Adds a new item to the credential manager. Will give an error if another key exists in the same scope with the same name.
        :param key: The name of the new key
        :param value: The value of the credential
        :param scope: The scope where the credential lives, 'env' for environment variables or 'global' for attributes. Defaults to env.
        :return: None
        """
        if scope.lower() == 'env':
            if self.__store.env.get(key, False):
                raise CredentialOverrideError(f'{key} already exists in the environment credentials')
            self.__store.env[key] = value
        elif scope.lower() == 'global':
            if self.__store.globs.get(key, False):
                raise CredentialOverrideError(f'{key} already exists in the global credentials')
            self.__store.globs[key] = value
        self.write()

    def __getattr__(self, item) -> Any:
        return self.__store.globs.get(item, None)
