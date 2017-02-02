"""
A VaultCzar/Secret Service client.
"""
import json
import logging
from base64 import urlsafe_b64decode
from typing import Tuple

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.padding import OAEP, MGF1
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class Pyczar3:
    """
    A class to access Secret Service secrets.
    """

    def __init__(self, server_url='https://ops-vaultczar1-1-crz.ops.sfdc.net', server_port='8271'):
        self.logger = logging.getLogger(__name__)
        self.base_url = server_url
        self.port = server_port
        self._vault_name = None
        self._private_key_path = None
        self._certificate_path = None

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
    def certificate_path(self) -> str:
        """
        The path to the private keys.
        :return: Path to the private keys.
        """
        return self._certificate_path

    @certificate_path.setter
    def certificate_path(self, key_path: str):
        """
        A file on disk.

        :param key_path: Path to the keys.
        :return: None
        """
        self._certificate_path = key_path

    def get_secret(self, secret_name: str) -> str:
        """
        Get a secret value.
        :param secret_name: The name of the secret
        :return: the secret value
        """
        if self._vault_name is None:
            raise RuntimeError('Please set a vault name first')
        url = "%s:%s/%s" % (self.base_url, self.port, "vaultczar/api/1.0/getSecretBySubscriber")
        self.logger.debug(url)
        body = {'vaultName': self._vault_name,
                'secretName': secret_name}
        self.logger.debug('Fetching secret "%s" from vault "%s"', secret_name, self._vault_name)

        req = requests.get(url, params=body, cert=(self.certificate_path, self.private_key_path))

        if req.status_code == 200:
            resp = req.json()
            # Returns: JSON formatted response that includes:
            # Status - String indicating “success” or “failure”
            # Key - Base64Url(Encryptpubkey(JSONString)) - JSON string containing two fields:
            #     Key - The randomly generated symmetric key, base64Urled
            #     IV - The randomly generated IV for symmetric encryption, base64Urled
            # Secret - Base64Url(EncryptSymmetricKey(JSONString)) JSON string contains the
            #          following fields:
            #     secretID - The URI of the requested secret
            #     Secret - The secret
            #     vaultName - Name of the vault returned by the server
            #     secretName - Name of the secret returned by the server
            if 'Status' in resp and resp['Status'].lower() == 'success':
                # Key is an AES key which in turn is encrypted
                # using mutual TLS's public key.
                (symmetric_key, initialization_vector) = self._get_aes_key(resp['Key'])
                secretbytes = urlsafe_b64decode(resp['Secret'])
                plainbytes = self._aes_decrypt(secretbytes, symmetric_key, initialization_vector)
                plainjson = json.loads(plainbytes.decode('utf-8'))
                cleartext_secret = plainjson['Secret']
                # returned_vault_name = plainjson["vaultName"]
                # returned_secret_name = plainjson["secretName"]

                return cleartext_secret
            elif resp['Status'].lower() != 'success':
                raise RuntimeError(resp['status'])

    def _get_aes_key(self, key_1: str) -> Tuple[bytes, bytes]:
        """

        :param key_1:
        :return: Tuple of (symmetric key, initialization vector)
        """
        with open(self.private_key_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )

        ciphertext = urlsafe_b64decode(key_1)
        plaintext = private_key.decrypt(
            ciphertext,
            OAEP(
                mgf=MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        key_dictionary = json.loads(plaintext.decode('ascii'))
        symmetric_key = urlsafe_b64decode(key_dictionary['Key'])
        initialization_vector = urlsafe_b64decode(key_dictionary['IV'])
        return symmetric_key, initialization_vector

    @staticmethod
    def _aes_decrypt(msg: bytes, symm_key: bytes, initialization_vector: bytes) -> bytes:
        """
        Decrypt some bytes.
        :param msg:
        :param_type msg: bytes
        :param symm_key: Symmetric Key
        :param initialization_vector: Initialization Vector
        :return: plain text
        """
        logging.debug('initializing AES-%d key with IV of %d bytes',
                      len(symm_key*8),
                      len(initialization_vector))
        cipher = Cipher(algorithms.AES(symm_key),
                        modes.CBC(initialization_vector),
                        backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(msg) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        return data
