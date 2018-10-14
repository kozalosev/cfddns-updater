"""
A script to keep the values in the Cloudflare DDNS service in sync with your
local dynamic IP address.

If you omit the 'config_path' parameter, the following files will be checked
for a user- or system-wide configuration:
    ~/.cloudflare-ddns-config
    /etc/cloudflare-ddns-config (only on POSIX systems)
If none of them exists, the process exits with code -1.

Exemplary content of the configuration file:
    email: username@example.org
    api_key: qP5EZa648oCRm6qlIDmbIOy37RbmLVRX7jpso
    periodicity: 60    # in seconds
    domains:
      - example.org    # 'proxied: true' is implied
      - www.example.org
      - domain: ssh.example.org
        proxied: false
"""
import os
import sys
import argparse
import logging
from time import sleep
from pathlib import Path
from enum import IntEnum
from typing import *

from .fixed_cloudflare_ddns import CloudFlare    # TODO: revert back when the issues will be fixed in the upstream
from . import config, __version__


#: the name of a user- or system-wide configuration file
CONFIG_FILE = "cloudflare-ddns-config"

_logger = logging.getLogger(__name__)


class ExitCodes(IntEnum):
    ConfigFileNotFound = -1
    ConfigValidationFailed = -2


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     epilog="(c) Leonid Kozarin <kozalo@sadbot.ru> (Kozalo.Ru, 2018)",
                                     prog=__package__)
    parser.add_argument("-v", action="count", default=0, dest="verbosity", help="increase verbosity to INFO or DEBUG")
    parser.add_argument("config_path", nargs='?', help="path to a configuration file")
    parser.add_argument("--version", "-version", action="version", version=f"%(prog)s v{__version__}")
    args = parser.parse_args()

    if args.verbosity >= 2:
        logging.basicConfig(level=logging.DEBUG)
    elif args.verbosity >= 1:
        logging.basicConfig(level=logging.INFO)

    config_path = args.config_path or get_global_config_path_if_exists() \
                  or log_and_exit(ExitCodes.ConfigFileNotFound, "The configuration file is not found!")
    conf = load_config_or_exit(config_path)
    instances = [CloudFlare(conf.email, conf.api_key, entry.domain, entry.proxied) for entry in conf.domains]
    while True:
        sync_domains(instances)
        sleep(conf.periodicity)


def get_global_config_path_if_exists() -> Optional[Path]:
    """
    Return the path to a user- or system-wide if either of them exists (the
    former takes precedence).
    """
    file_path = Path("~", f".{CONFIG_FILE}").expanduser()
    if file_path.exists():
        return file_path
    if os.name == 'posix':
        file_path = Path("/", "etc", CONFIG_FILE)
        if file_path.exists():
            return file_path
    return None


def log_and_exit(exit_code: ExitCodes, message: str):
    _logger.critical(message)
    sys.exit(exit_code)


def load_config_or_exit(config_path) -> config.Config:
    """
    Try to read a configuration file and return a Config object. Exit with one
    of ExitCodes values if failed.
    """
    try:
        return config.load(config_path)
    except FileNotFoundError as err:
        log_and_exit(ExitCodes.ConfigFileNotFound, str(err))
    except ValueError as err:
        log_and_exit(ExitCodes.ConfigValidationFailed, str(err))


def sync_domains(instances: Iterable[CloudFlare]) -> None:
    """Synchronize domains with the local IP address using Cloudflare API."""
    for cf in instances:
        print("### {domain} ###".format(domain=cf.domain.upper()))
        cf.sync_dns_from_my_ip()
