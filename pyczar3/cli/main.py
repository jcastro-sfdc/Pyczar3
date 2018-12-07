"""
Command-line parser to use this library as a stand-alone app.
"""
import argparse
import os
from pyczar3 import Pyczar3


def main():
    """
    Command-line entry point, declared in ``setup.py``.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--certificate',
                        default=os.environ['SECRETSERVICE_CERT'],
                        help='Path to client-side TLS certificate (PEM format)')
    parser.add_argument('--private_key',
                        default=os.environ['SECRETSERVICE_KEY'],
                        help='Path to the client-side TLS secret (PEM format)')
    parser.add_argument('--vault', required=True, help='The name of the Secret Service Vault')
    parser.add_argument('--secret_name', required=True, help='The name of the secret')

    args = parser.parse_args()

    pyczar = Pyczar3()
    pyczar.certificate_path = args.certificate
    pyczar.private_key_path = args.private_key
    pyczar.vault = args.vault
    secret = pyczar.get_secret(args.secret_name)
    print(secret)
