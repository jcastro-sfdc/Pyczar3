import pytest
import responses

import pyczar3


class TestPyczar3WithCertificates:

    @responses.activate
    def test_get_secret(self):
        secret_value = '42'
        secret_name = 'life'
        secret_vault = 'HHGTTG'
        server_response = {
            'RawSecret': {'Secret': secret_value},
            'Status': 'success'
        }

        responses.add(responses.GET,
                      'https://secretservice.dmz.salesforce.com:8271/vaultczar/api/1.0/'
                      'getSecretBySubscriber?secretName={0}&vaultName={1}&disableEncrypt=true'.format(secret_name, secret_vault),
                      match_querystring=True,
                      json=server_response,
                      status=200,
                      content_type='application/json')
        p = pyczar3.Pyczar3()
        p.vault = secret_vault

        assert secret_value == p.get_secret(secret_name)


class TestPyczar3:

    def test_get_secret_without_vault(self):
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
