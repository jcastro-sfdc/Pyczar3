"""
A VaultCzar/Secret Service client.
"""
import logging

import pkg_resources
import requests


class Pyczar3:
    """
    A class to access Secret Service secrets.
    """

    def __init__(self, server_url='https://secretservice.dmz.salesforce.com',
                 server_port='8271'):
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
    def vault(self, vault: str) -> None:
        """
        Set the vault name.

        :param str vault: Name of the vault
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
    def private_key_path(self, key_path: str) -> None:
        """
        Set a path to the private keys

        :param str key_path: Path to the keys.
        :return: None
        """
        self._private_key_path = key_path

    @property
    def certificate_path(self) -> str:
        """
        The path to the public certificate.

        :return: Path to the public certificate.
        """
        return self._certificate_path

    @certificate_path.setter
    def certificate_path(self, key_path: str) -> None:
        """
        Set a path to the public certificate.

        :param str key_path: Path to public certificate.
        :return: None
        """
        self._certificate_path = key_path

    @staticmethod
    def _ca_path() -> str:
        """
        Gets the path to the bundled CA_BUNDLE.
        :return: str
        """
        return pkg_resources.resource_filename(__name__, 'certs/ca_bundle.crt')

    def get_secret(self, secret_name: str) -> str:
        """
        Get a secret value.

        :param str secret_name: The name of the secret
        :return: the secret value
        """
        if self._vault_name is None:
            raise RuntimeError('Please set a vault name first')
        url = "%s:%s/%s" % (self.base_url, self.port,
                            "vaultczar/api/1.0/getSecretBySubscriber")
        self.logger.debug(url)
        body = {'vaultName': self._vault_name,
                'secretName': secret_name,
                'disableEncrypt': 'true'}
        self.logger.debug('Fetching secret "%s" from vault "%s"',
                          secret_name, self._vault_name)

        req = requests.get(url,
                           params=body,
                           cert=(self.certificate_path,  # client cert
                                 self.private_key_path),
                           verify=self._ca_path())  # server cert

        if req.status_code == 200:
            resp = req.json()
            # Returns: JSON formatted response that includes:
            # Status - String indicating “success” or “failure”
            if 'Status' in resp and resp['Status'].lower() == 'success':
                return resp['RawSecret']['Secret']
            raise RuntimeError(resp['Status'])
        raise RuntimeError('non-200 response code ({0})'.format(
                           req.status_code))
