"""
This module fixes some bugs of the 'cloudflare-ddns' module.
See:
- https://github.com/ailionx/cloudflare-ddns/pull/6
- https://github.com/ailionx/cloudflare-ddns/pull/7
- https://github.com/ailionx/cloudflare-ddns/pull/8
"""
import sys
import socket
import requests
import urllib.parse

import cloudflare_ddns
from cloudflare_ddns.exceptions import RecordNotFound


class CloudFlare(cloudflare_ddns.CloudFlare):
    def __init__(self, email: str, api_key: str, domain: str, proxied: bool):
        """
        Initialization. It will set the zone information of the domain for operation.
        It will also get dns records of the current zone.
        """
        super().__init__(email, api_key, domain, proxied)
        self.headers = {
            'X-Auth-Key': api_key,
            'X-Auth-Email': email
        }

    def request(self, url, method, data=None):
        """The requester shortcut to submit a http request to CloutFlare"""
        method = getattr(requests, method)
        response = method(
            url,
            headers=self.headers,
            json=data
        )
        content = response.json()
        if response.status_code != 200:
            print(content)
            raise requests.HTTPError(content['message'])
        return content

    def create_record(self, dns_type, name, content, **kwargs):
        """Create a dns record"""
        data = {
            'type': dns_type,
            'name': name,
            'content': content
        }
        if kwargs.get('ttl') and kwargs['ttl'] != 1:
            data['ttl'] = kwargs['ttl']
        if kwargs.get('proxied') is True:
            data['proxied'] = True
        else:
            data['proxied'] = False
        content = self.request(
            self.api_url + self.zone['id'] + '/dns_records',
            'post',
            data=data
        )
        self.dns_records.append(content['result'])
        print('DNS record successfully created')
        return content['result']

    def update_record(self, dns_type, name, content, **kwargs):
        """Update dns record"""
        record = self.get_record(dns_type, name)
        data = {
            'type': dns_type,
            'name': name,
            'content': content
        }
        if kwargs.get('ttl') and kwargs['ttl'] != 1:
            data['ttl'] = kwargs['ttl']
        if kwargs.get('proxied') is True:
            data['proxied'] = True
        else:
            data['proxied'] = False
        content = self.request(
            urllib.parse.urljoin(self.api_url, self.zone['id'] + '/dns_records/' + record['id']),
            'put',
            data=data
        )
        record.update(content['result'])
        print('DNS record successfully updated')
        return content['result']

    def delete_record(self, dns_type, name):
        """Delete a dns record"""
        record = self.get_record(dns_type, name)
        content = self.request(
            urllib.parse.urljoin(self.api_url, self.zone['id'] + '/dns_records/' + record['id']),
            'delete'
        )
        cached_record_id = [i for i, rec in enumerate(self.dns_records) if rec['id'] == content['result']['id']][0]
        del self.dns_records[cached_record_id]
        return content['result']['id']

    def sync_dns_from_my_ip(self, dns_type='A'):
        """
        Sync dns from my public ip address.
        It will not do update if ip address in dns record is already same as
        current public ip address.
        """
        ip_address = ''
        for finder in self.public_ip_finder:
            try:
                result = requests.get(finder)
            except requests.RequestException:
                continue
            if result.status_code == 200:
                try:
                    socket.inet_aton(result.text)
                    ip_address = result.text
                    break
                except socket.error:
                    try:
                        socket.inet_aton(result.json().get('ip'))
                        ip_address = result.json()['ip']
                        break
                    except socket.error:
                        continue

        if ip_address == '':
            print('None of public ip finder is working. Please try later')
            sys.exit(1)

        try:
            record = self.get_record(dns_type, self.domain) \
                if len(self.domain.split('.')) == 3 \
                else self.get_record(dns_type, self.domain)
        except RecordNotFound:
            self.create_record(dns_type, self.domain, ip_address, proxied=self.proxied)
            print('Successfully created new record with IP address {new_ip}'
                  .format(new_ip=ip_address))
        else:
            if record['content'] != ip_address:
                old_ip = record['content']
                self.update_record(dns_type, self.domain, ip_address, proxied=record['proxied'])
                print('Successfully updated IP address from {old_ip} to {new_ip}'
                      .format(old_ip=old_ip, new_ip=ip_address))
            else:
                print('IP address on CloudFlare is same as your current address')
