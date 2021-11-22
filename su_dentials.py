import os
import json
import robocrypt

from typing import Any
from addict import Dict


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
        self._creds_path = credentials_file
        self._locked_path = f"{credentials_file}.robo"
        self._salt_file = '/var/secure/robocrypt.salt'

        if not os.path.exists(credentials_file) and not os.path.exists(self._locked_path):
            raise FileNotFoundError(f'Neither a locked or unlocked credentials file could be found.')

        self.__password = password
        self.__store = Dict()

    def state(self):
        if os.path.exists(self._creds_path) and not os.path.exists(self._locked_path):
            return 'unlocked'
        else:
            return 'locked'

    def set_password(self, new_password: str):
        if self.__password is None:
            self.__password = new_password
        else:
            print('please use change_password instead.')

    def change_password(self, old_password: str, new_password: str):
        try:
            self.unlock(password=old_password)
            self.__password = new_password
            self.lock()
        except AttributeError:
            raise InvalidPassword('The old password specified is not correct.')

    def forget_password(self):
        self.__password = None

    def lock(self, password: str = None):
        if self.state() == 'locked':
            return
        robocrypt.encrypt_file(filepath=self._creds_path, password=password if password else self.__password, shift=17)

    def unlock(self, password: str = None):
        if self.state() == 'unlocked':
            return
        try:
            robocrypt.decrypt_file(filepath=self._locked_path, password=password if password else self.__password, shift=17)
        except robocrypt.DecryptionError:
            raise CredentialsLockedError('Unable to unlock credentials with the provided password.')

    def change_salt(self, salt_length: int):
        self.unlock()
        with open(self._salt_file, 'wb') as sf:
            sf.write(os.urandom(salt_length))
        self.lock()

    def engage(self):
        self.unlock()
        with open(self._creds_path, 'r') as cf:
            creds = json.load(cf)
        self.__store = Dict(env=creds['ENV'], globs=creds['GLOBAL'])
        self.lock()
        for key, value in self.__store.env.items():
            os.environ[key] = value

    def disengage(self):
        for key in self.__store.env.keys():
            del os.environ[key]
        self.__store.clear()

    def write(self):
        self.unlock()
        data = {
            "ENV": {k: v for k, v in self.__store.env.items()},
            "GLOBAL": {k: v for k, v in self.__store.globs.items()}
        }
        with open(self._creds_path, 'wb') as of:
            json.dump(data, of, indent=4)
        self.lock()

    def update_item(self, key, new_value, scope: str = 'env'):
        if scope.lower() == 'env':
            self.__store.env[key] = new_value
        elif scope.lower() == 'global':
            self.__store.globs[key] = new_value
        self.write()

    def add_item(self, key, value, scope: str = 'env'):
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
