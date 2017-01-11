
import responses
import pyczar3
import pytest


class TestPyczar3:

    def test_get_password_without_vault(self):
        p = pyczar3.Pyczar3()
        with pytest.raises(RuntimeError):
            p.get_secret('MySecret')

    @responses.activate
    def test_get_password(self):
        responses.add(responses.POST,
                      'https://ops-vaultczar1-1-crz.ops.sfdc.net:8443/vaultczar/api/1.0/getSecret',
                      body='{"Status":"success","Key":"AH8yt_LAWvwRR2kgNuGCg9lgfoSRCb_0_6NPUemksCedeAxYoi06E24vWA2L8AUsrU67Oqrj9RLZq0Kc-HPrW4QdVVM12LtWlPwYJt0jJHtOMFQKfTp3ucd3VN3eneVmFQeYa2Exw5xLZ8QAtpLsIhNpNV346Zs1jCmPPVZ1u3Fzvtbx5fZv2pyL3CHot2460nt__-PdTXDULUC23KLzMtSf8x6GvNENnzbcuQdzoKyB3rwSPgRGUHomu4yIkRGwCBjEo1Frh7O8ZK7MLEfggOUtRKZhknYJdLYWJtQnubw2BUjo7lu15dYQGFxo6B4L2XcOMm-L1QYXJmZuCenUY_Ih_mFZyZRfTbSdSUs_nnv12A1RF-1Cfs9M8op2thLQFnDD67JgAkfHcdQNyYYxgOcBgQjZjEsLw4l9lE_F53OOkNGEP9Rj8VwVgi3evIBwaB1IzGr1H9Wjya9uinm1hl4Gn93StdoMtP1cyI_p3RkEYBmmlGkgu0sxBRtEhQYDjoOfqxYz2fAQ8CNsdITfcp1l1nuvivZ82P0r0jxuCLImakYp9ECm311-o6ydmNmEiCA2RotzG14UzyV9edEi0RyyCsVINWkr9vYLn34hzNw097grCum3XPA31PbO4uI-rLIbaKhDyeqM0IfeQfqxun1d7Yc-QRo7x-HvlFr5x9-U0UQSxg==","Secret":"ONkuB8FDKfrdBBvKQ6w29hD_keWeq05Gnf_0MX6XUhsgKBVWHG6A0ro0xe8SBs-qz9dOvM5wDNYGQt7Ohok9LYaJWpr79YOVtAQLyKbJ5sCA4RhMWqq-YqY7d0eEJSbBYY0tT64Na1UrxGuXEFVmTEcLRQ90SUqkK_CTuUbOK1M8ve9S-RieiKIpS_bK-tv-"}',
                      status=200,
                      content_type='application/json')

        p = pyczar3.Pyczar3()
        p.vault = 'PYCZAR_TEST_ONLY'
        p.key_location = 'tests/test_keypair'
        assert 'SFDC123' == p.get_secret('test_password')

    def test_properties(self):
        p = pyczar3.Pyczar3()
        assert p.key_location is None
        assert p.vault is None

        p.vault = 'Vault'
        assert p.vault == 'Vault'

        p.key_location = './keys'
        assert p.key_location == './keys'
