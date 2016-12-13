import argparse
from pyczar3 import Pyczar3


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--keypair', required=True, help='Path to the keypair')
    parser.add_argument('--vault', required=True, help='The name of the Secret Service Vault')
    parser.add_argument('--secret_name', required=True, help='The name of the secret')

    args = parser.parse_args()

    p = Pyczar3()
    p.key_location = args.keypair
    p.vault = args.vault
    s = p.get_secret(args.secret_name)
    print(s)
