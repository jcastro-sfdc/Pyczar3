import json
import os
from base64 import urlsafe_b64encode

import pytest
import responses
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.padding import OAEP, MGF1
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers import algorithms, modes

import pyczar3


class TestPczr3WithCertificates:

    def __init__(self):
        self.cert_path = 'tests/test_rsa.cer'
        self.key_path = 'tests/test_rsa.key'
        self.vault = 'FakeVault'
        self.secret_name = 'Secret'
        self.secret_value = 'abra cadabra'
        self.server_response = None

    def make_test_files(self):
        # Key - Base64Url(Encrypt_pubkey(JSONString)) - JSON string containing two fields:
        #     Key - The randomly generated symmetric key, base64Urled
        #     IV - The randomly generated IV for symmetric encryption, base64Urled
        # Secret - Base64Url(Encrypt_SymmetricKey(JSONString)) JSON string contains the following fields:
        #     secretID - The URI of the requested secret
        #     Secret - The secret
        #     vaultName - Name of the vault returned by the server
        #     secretName - Name of the secret returned by the server
        secret = {
            'secretID': '',
            'Secret': self.secret_value,
            'vaultName': self.vault,
            'secretName': self.secret_name
        }
        # Asymmetric RSA-2048 private key:
        private_key = rsa.generate_private_key(public_exponent=65537,
                                               key_size=2048,
                                               backend=default_backend())  # type: rsa.RSAPrivateKey
        public_key = private_key.public_key()  # type: rsa.RSAPublicKey
        asymmetric_padding = OAEP(mgf=MGF1(algorithm=hashes.SHA256()),
                                  algorithm=hashes.SHA256(),
                                  label=None)

        # Symmetric AES key:
        iv = os.urandom(16)
        aes_key = os.urandom(32)  # 128, 192, or 256 bits (16, 24, or 32 bytes)
        symmetric_cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        symmetric_encryptor = symmetric_cipher.encryptor()
        padder = padding.PKCS7(256).padder()

        # 1. encrypt `secret` json with the symmetric key.
        padded_secret = padder.update(json.dumps(secret).encode('ascii')) + padder.finalize()
        encrypted_secret = symmetric_encryptor.update(padded_secret) + symmetric_encryptor.finalize()

        # 2. encrypt `key` json with the RSA public key.
        key = {
            'Key': urlsafe_b64encode(aes_key).decode('ascii'),
            'IV': urlsafe_b64encode(iv).decode('ascii')
        }
        encrypted_key = public_key.encrypt(json.dumps(key).encode('ascii'), asymmetric_padding)

        server_response = {
            'Secret': urlsafe_b64encode(encrypted_secret).decode('ascii'),
            'Key': urlsafe_b64encode(encrypted_key).decode('ascii'),
            'Status': 'success'
        }

        private_pem = private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                                format=serialization.PrivateFormat.PKCS8,
                                                encryption_algorithm=serialization.NoEncryption())
        public_pem = public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                             format=serialization.PublicFormat.SubjectPublicKeyInfo)

        return public_pem.decode('ascii'), private_pem.decode('ascii'), server_response

    def setup_method(self):
        public_pem, private_pem, self.server_response = self.make_test_files()
        with open(self.cert_path, 'w') as cert_file:
            cert_file.write(public_pem)
        with open(self.key_path, 'w') as private_key_file:
            private_key_file.write(private_pem)

    def teardown_method(self):
        os.remove(self.cert_path)
        os.remove(self.key_path)

    @responses.activate
    def test_get_password(self):

        responses.add(responses.GET,
                      'https://ops-vaultczar1-1-crz.ops.sfdc.net:8271/vaultczar/api/1.0/'
                      'getSecretBySubscriber?secretName={0}&vaultName={1}'.format(self.secret_name, self.vault),
                      match_querystring=True,
                      json=self.server_response,
                      status=200,
                      content_type='application/json')
        p = pyczar3.Pyczar3()
        p.vault = self.vault
        p.certificate_path = self.cert_path
        p.private_key_path = self.key_path

        assert self.secret_value == p.get_secret(self.secret_name)


class TestPyczar3:

    def test_get_password_without_vault(self):
        p = pyczar3.Pyczar3()
        with pytest.raises(RuntimeError):
            p.get_secret('MySecret')

    def test_properties(self):
        """
        Test the public properties for Pyczar3
        """
        p = pyczar3.Pyczar3()
        assert p.certificate_path is None
        assert p.private_key_path is None
        assert p.vault is None

        p.vault = 'Vault'
        assert p.vault == 'Vault'

        p.key_location = './keys'
        assert p.key_location == './keys'
