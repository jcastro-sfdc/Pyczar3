import json
import logging
from base64 import urlsafe_b64decode
from typing import Tuple

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from keyczar.errors import KeyNotFoundError
from keyczar.keyczar import Crypter

__author__ = "Jason Schroeder"
__email__ = "jschroeder@salesforce.com"


class Pyczar3:
    """
    A class to access Secret Service secrets.
    """

    def __init__(self, server_url='https://ops-vaultczar1-1-crz.ops.sfdc.net', server_port='8443'):
        self.logger = logging.getLogger(__name__)
        self.base_url = server_url
        self.port = server_port
        self.api = "vaultczar/api"
        self.version = "1.0"
        self.endpoint = "getSecret"
        self._vault_name = None
        self._private_key_path = None
        self._certificate_key_path = None

    @property
    def vault(self) -> str:
        """
        The name of the vault.
        :return: The name of the vault.
        """
        return self._vault_name

    @vault.setter
    def vault(self, vault: str):
        """
        Set the vault name.
        :param vault: Name of the vault
        :return: None
        """
        self._vault_name = vault

    @property
    def private_key_path(self) -> str:
        """
        The path to the private keys.
        :return: Path to the private keys.
        """
        return self._private_key_path

    @private_key_path.setter
    def private_key_path(self, key_path: str):
        """
        A file on disk.

        :param key_path: Path to the keys.
        :return: None
        """
        self._private_key_path = key_path

    @property
    def certificate_key_path(self) -> str:
        """
        The path to the private keys.
        :return: Path to the private keys.
        """
        return self._certificate_key_path

    @certificate_key_path.setter
    def certificate_key_path(self, key_path: str):
        """
        A file on disk.

        :param key_path: Path to the keys.
        :return: None
        """
        self._certificate_key_path = key_path


    def get_secret(self, secret_name: str) -> str:
        """
        Get a secret value.
        :param secret_name: The name of the secret
        :return: the secret value
        """
        if self._vault_name is None:
            raise RuntimeError('Please set a vault name first')
        url = "%s:%s/%s/%s/%s" % (self.base_url, self.port, self.api, self.version, self.endpoint)
        self.logger.debug(url)
        body = {'vaultName': self._vault_name,
                'secretName': secret_name}
        self.logger.debug('Fetching secret "%s" from vault "%s"', secret_name, self._vault_name)

        # You can also specify a local cert to use as client side certificate, as a single file
        # (containing the private key and the certificate) or as a tuple of both file's path:

        # >>> requests.get('https://kennethreitz.com', cert=('/path/client.cert', '/path/client.key'))
        # <Response [200]>

        # or persistent:
        # s = requests.Session()
        # s.cert = '/path/client.cert'

        req = requests.post(url, json=body, cert=(self.certificate_key_path, self.private_key_path))

        if req.status_code == 200:
            resp = req.json()
            if 'Status' in resp and resp['Status'] == 'success':
                # Key is an AES key which in turn is encrypted
                # using vault's public key.
                (symmetric_key, iv) = self._get_aes_key(resp['Key'])
                secretbytes = urlsafe_b64decode(resp['Secret'])
                plainbytes = self._aes_decrypt(secretbytes, symmetric_key, iv)
                plainjson = json.loads(plainbytes.decode('utf-8'))
                cleartext_secret = plainjson['Secret']
                # returned_vault_name = plainjson["vaultName"]
                # returned_secret_name = plainjson["secretName"]

                return cleartext_secret
            elif resp['Status'] != 'Success':
                raise RuntimeError(resp['sStatus'])

    def _get_aes_key(self, key_1: str) -> Tuple[bytes, bytes]:
        """

        :param key_1:
        :return: Tuple of (symmetric key, initialization vector)
        """
        crypter = self._get_crypter()
        try:
            aes_key = crypter.Decrypt(key_1)  # type: str
        except KeyNotFoundError as knfe:
            self.logger.error('The key set has keys with following hashe(s) ')
            # print(Pyczar.get_hash_id(key_location))
            raise knfe
        key_dictionary = json.loads(aes_key)
        symmetric_key = urlsafe_b64decode(key_dictionary['Key'])
        iv = urlsafe_b64decode(key_dictionary['IV'])
        return symmetric_key, iv

    def _get_crypter(self) -> Crypter:
        """
        :return: Crypter object of the active primary private key
        """
        crypter = Crypter.Read(self.key_location)
        if len(crypter.versions) == 0:
            raise RuntimeError('You have no keys, this isn\'t going to work.')
        if not crypter.primary_version:
            # A primary version is needed for encrypting locally.
            versions = [i for i in crypter.versions if str(i.status) != 'INACTIVE']
            crypter.primary_version = sorted(versions, key=lambda x: x.version_number)[-1]
        return crypter

    @staticmethod
    def _aes_decrypt(msg: bytes, symm_key: bytes, iv: bytes) -> bytes:
        """
        Decrypt some bytes.
        :param msg:
        :param_type msg: bytes
        :param symm_key: Symmetric Key
        :param iv: Initialization Vector
        :return: plain text
        """
        cipher = Cipher(algorithms.AES(symm_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(msg) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        return data

