"""
Parser of configuration files written in YAML.

Call the 'load(file_path)' function to get an instance of the Config class
containing instances of the DomainEntry class.

The format of configuration files:
    email: <your login to Cloudflare>
    api_key: <Cloudflare API key>
    periodicity: <timeout between checks in seconds>
    domains:
      - <domain record 1>    # 'proxied: true' is implied
      - <domain record 2>
      - domain: <domain record 3>
        proxied: false
      <...>
"""
import logging
import yaml
from pathlib import PurePath, Path
from typing import *


__all__ = ['load', 'Config', 'DomainEntry']
_logger = logging.getLogger(__name__)

#: the default timeout between checks in seconds
DEFAULT_PERIODICITY = 60


class DomainEntry(NamedTuple):
    domain: str
    proxied: bool = True


class Config(NamedTuple):
    email: str
    api_key: str
    periodicity: float
    domains: Iterable[DomainEntry]


def load(file_path: Union[PurePath, str]) -> Config:
    """Return a Config object by parsing and validating data from some YAML file."""
    config_dict = load_file(file_path)
    domains = [DomainEntry(entry['domain'], entry['proxied']) for entry in config_dict['domains']]
    return Config(config_dict['email'], config_dict['api_key'], config_dict['periodicity'], domains)


def load_file(file_path: Union[PurePath, str]) -> dict:
    """
    Read a YAML file, validate the correctness of a produced object, expand the
    short form of domain entries into dicts and return the resulting dict.
    """
    with Path(file_path).open('r') as config_file:
        config_dict = yaml.safe_load(config_file)

    if not isinstance(config_dict, dict):
        raise ValueError("Invalid configuration file: the root element must be a dictionary!")
    if "email" not in config_dict or "api_key" not in config_dict:
        raise ValueError("Specify both 'email' and 'api_key' for Cloudflare API!")
    if "domains" not in config_dict or not isinstance(config_dict['domains'], list):
        raise ValueError("Domain entries must be specified as a list under the 'domains' key.")

    if 'periodicity' not in config_dict:
        config_dict['periodicity'] = DEFAULT_PERIODICITY
    config_dict['domains'] = normalize_domains(config_dict['domains'])
    return config_dict


def normalize_domains(domains: Iterable) -> Iterable[dict]:
    """Expand string domains to {'domain': entry, 'proxied': True}."""
    normalized_domains = []
    for entry in domains:
        if isinstance(entry, dict):
            if "domain" not in entry:
                raise ValueError("No domain specified in the entry '{entry}!'".format(entry=entry))
            if "proxied" not in entry:
                _logger.info("Domain '{domain}' will be proxied by Cloudflare.".format(domain=entry['domain']))
                entry['proxied'] = True
            normalized_domains.append(entry)
        elif isinstance(entry, str):
            _logger.info("Domain '{domain}' will be proxied by Cloudflare.".format(domain=entry))
            normalized_domains.append({'domain': entry, 'proxied': True})
        else:
            _logger.warning("Domain entry is not a str or dict, so it is ignored ({entry}).".format(entry=entry))
    return normalized_domains
