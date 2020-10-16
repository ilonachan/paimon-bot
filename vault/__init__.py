import base64

import logging
import os.path
import sys

import yaml
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

log = logging.getLogger(__name__)

_vault: dict = None
_vault_file_path = os.path.join(__path__[0], 'vault.bin')
_vault_base_path = os.path.join(__path__[0], 'vault_base.yaml')


class _PathChainer:
    def __init__(self, name=None):
        self._name = name

    def __getattr__(self, name):
        return self[name]

    def __call__(self, default=None, include=None):
        if include is not None:
            return include(self._name, include)
        return vault_value(self._name, default)

    def __getitem__(self, name):
        if self._name is None:
            return _PathChainer(str(name))
        return _PathChainer(f'{self._name}.{name}')


vault = _PathChainer()


def _get_from_vault(key):
    if type(key) is _PathChainer:
        key: str = key._name

    cursor = _vault
    for part in key.split('.'):
        cursor = cursor[part]

    return cursor


def _get_base_key(key):
    """
    From an arbitrarily long password, generate a 32 byte hash used
    as a symmetric key to encrypt the Vault
    :param key:
    :return:
    """
    salt = b'\x8dy\xcd\xf3\x1a\xec\xc1n\x94\x12\x82\x9d\xf8\xa1&='
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000)
    return base64.urlsafe_b64encode(kdf.derive(key.encode('utf-8')))


def _load_vault(secret_key):
    global _vault
    try:
        fernet = Fernet(_get_base_key(secret_key))

        with open(_vault_file_path, "rb") as vault_file:
            _vault = yaml.safe_load(fernet.decrypt(vault_file.read()))

    except Exception as e:
        log.error('Could not load Vault', exc_info=e)


def _gen_vault(secret_key):
    """
    Generate an up-to-date vault.bin file from the vault_base.yaml file

    :param secret_key: The secret key to encrypt everything with
    :return:
    """
    try:
        fernet = Fernet(_get_base_key(secret_key))

        with open(_vault_base_path, "rb") as base_file, open(_vault_file_path, "wb") as vault_file:
            vault_file.write(fernet.encrypt(base_file.read()))
    except Exception as e:
        log.error('Could not generate Vault', exc_info=e)


def vault_init(secret_key=None):
    if secret_key is None:
        return vault_ready()
    if os.path.isfile(_vault_base_path):
        _gen_vault(secret_key)
    _load_vault(secret_key)
    return vault_ready()


def vault_ready():
    return _vault is not None


def vault_value(key, default=None):
    """
    Returns the secret referenced by the key supplied.
    If the vault has not been initialized, returns the provided default instead

    :param key:
    :param default:
    :return:
    """
    if not vault_ready():
        return default
    try:
        return _get_from_vault(key)
    except KeyError:
        log.warning(f'The provided key "{key}" was not defined in the vault. '
                    f'This is a programming error, but it will be handled '
                    f'gracefully by using the default value.')
        return default


def _include(key, base):
    if base is None:
        return vault_value(key)

    if isinstance(base, dict):
        vault_lst: dict = vault_value(key, {})
        for k, v in vault_lst.items():
            base[k] = v
        return base

    if isinstance(base, list):
        vault_lst = vault_value(key, [])
        for el in vault_lst:
            base.append(el)
        return base

    return base
