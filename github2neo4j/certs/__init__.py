import os

from requests import adapters

DEFAULT_CA_BUNDLE_PATH = os.path.join(os.path.dirname(__file__), 'ca-certificates.crt')


def install_intel_certs():
    adapters.DEFAULT_CA_BUNDLE_PATH = DEFAULT_CA_BUNDLE_PATH
