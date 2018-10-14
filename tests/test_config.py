import pytest
import logging
from cfddns_updater.config import *
from cfddns_updater.config import normalize_domains, load_file


def test__normalize_domains(caplog):
    given = [
        'example.org',
        'www.example.org',
        {'domain': 'server.example.org', 'proxied': False},
        {'domain': 'ssh.example.org'},
        [1, 2, 3]
    ]
    expected = [
        {'domain': 'example.org', 'proxied': True},
        {'domain': 'www.example.org', 'proxied': True},
        {'domain': 'server.example.org', 'proxied': False},
        {'domain': 'ssh.example.org', 'proxied': True}
    ]
    with caplog.at_level(logging.INFO):
        assert normalize_domains(given) == expected
    assert "Domain entry is not a str or dict, so it is ignored ([1, 2, 3])." in caplog.messages
    assert "Domain 'example.org' will be proxied by Cloudflare." in caplog.messages
    assert "Domain 'www.example.org' will be proxied by Cloudflare." in caplog.messages
    assert "Domain 'ssh.example.org' will be proxied by Cloudflare." in caplog.messages


def test__normalize_domains__no_domain():
    given = [
        'example.org',
        'www.example.org',
        {'foo': 'bar'}
    ]
    with pytest.raises(ValueError, match="No domain specified in the entry"):
        normalize_domains(given)


def test__load_file(tmpdir):
    p = tmpdir.join("test.yml")
    expected = {
        'email': 'username@example.org',
        'api_key': 'qP5EZa648oCRm6qlIDmbIOy37RbmLVRX7jpso',
        'periodicity': 60,
        'domains': [
            {'domain': 'example.org', 'proxied': True},
            {'domain': 'www.example.org', 'proxied': True},
            {'domain': 'ssh.example.org', 'proxied': False}
        ]
    }

    p.write("""email: username@example.org
api_key: qP5EZa648oCRm6qlIDmbIOy37RbmLVRX7jpso
domains:
  - example.org
  - www.example.org
  - domain: ssh.example.org
    proxied: false
""")
    assert load_file(p) == expected

    p.write("""email: username@example.org
api_key: qP5EZa648oCRm6qlIDmbIOy37RbmLVRX7jpso
domains: [example.org, www.example.org, {domain: ssh.example.org, proxied: false}]
""")
    assert load_file(p) == expected


def test__load_file__with_periodicity(tmpdir):
    p = tmpdir.join("test.yml")
    expected = {
        'email': 'username@example.org',
        'api_key': 'qP5EZa648oCRm6qlIDmbIOy37RbmLVRX7jpso',
        'periodicity': 120,
        'domains': [
            {'domain': 'example.org', 'proxied': True},
            {'domain': 'www.example.org', 'proxied': True},
            {'domain': 'ssh.example.org', 'proxied': False}
        ]
    }

    p.write("""email: username@example.org
api_key: qP5EZa648oCRm6qlIDmbIOy37RbmLVRX7jpso
periodicity: 120
domains:
  - example.org
  - www.example.org
  - domain: ssh.example.org
    proxied: false
""")
    assert load_file(p) == expected


def test__load_file__only_domains(tmpdir):
    p = tmpdir.join("test.yml")
    p.write("""domains:
      - example.org
      - www.example.org
      - domain: ssh.example.org
        proxied: false
    """)
    with pytest.raises(ValueError, match="Specify both 'email' and 'api_key' for Cloudflare API!"):
        load_file(p)


def test__load_file__only_credentials(tmpdir):
    p = tmpdir.join("test.yml")
    p.write("""email: username@example.org
api_key: qP5EZa648oCRm6qlIDmbIOy37RbmLVRX7jpso
""")
    with pytest.raises(ValueError, match="Domain entries must be specified as a list under the 'domains' key."):
        load_file(p)


def test__load_file__list_as_root(tmpdir):
    p = tmpdir.join("test.yml")
    p.write("""- email: username@example.org
- api_key: qP5EZa648oCRm6qlIDmbIOy37RbmLVRX7jpso
- domains:
    - example.org
    - www.example.org
    - domain: ssh.example.org
      proxied: false
""")
    with pytest.raises(ValueError, match="Invalid configuration file: the root element must be a dictionary!"):
        load_file(p)


def test__load(tmpdir):
    p = tmpdir.join("test.yml")
    expected = Config("username@example.org", "qP5EZa648oCRm6qlIDmbIOy37RbmLVRX7jpso", 60, [
        DomainEntry("example.org", True),
        DomainEntry("www.example.org", True),
        DomainEntry("ssh.example.org", False)
    ])

    p.write("""email: username@example.org
api_key: qP5EZa648oCRm6qlIDmbIOy37RbmLVRX7jpso
domains:
  - example.org
  - www.example.org
  - domain: ssh.example.org
    proxied: false
""")
    assert load(p) == expected

    p.write("""email: username@example.org
api_key: qP5EZa648oCRm6qlIDmbIOy37RbmLVRX7jpso
domains: [example.org, www.example.org, {domain: ssh.example.org, proxied: false}]
""")
    assert load(p) == expected


def test__load__with_periodicity(tmpdir):
    p = tmpdir.join("test.yml")
    expected = Config("username@example.org", "qP5EZa648oCRm6qlIDmbIOy37RbmLVRX7jpso", 120, [
        DomainEntry("example.org", True),
        DomainEntry("www.example.org", True),
        DomainEntry("ssh.example.org", False)
    ])

    p.write("""email: username@example.org
api_key: qP5EZa648oCRm6qlIDmbIOy37RbmLVRX7jpso
periodicity: 120
domains:
  - example.org
  - www.example.org
  - domain: ssh.example.org
    proxied: false
""")
    assert load(p) == expected
