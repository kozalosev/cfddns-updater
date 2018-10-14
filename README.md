cfddns-updater
==============

[![Build Status](https://travis-ci.org/kozalosev/cfddns-updater.svg?branch=master)](https://travis-ci.org/kozalosev/cfddns-updater)

A script to keep the values in the Cloudflare DDNS service in sync with your local
dynamic IP address. It starts an infinite loop that periodically performs checks, using
an external service, whether your IP address has changed or not. If it is so, the script
sends a request to Cloudflare API and updates the DNS records.


Requirements
------------

* Python 3.6+


How to use the script
---------------------

1. **Write a configuration file** in the following format:

    ```yaml
    email: <your login to Cloudflare>
    api_key: <Cloudflare API key>
    periodicity: <timeout between checks in seconds>
    domains:
      - example.org    # 'proxied: true' is implied
      - www.example.org
      - domain: ssh.example.org
        proxied: false
      <...>
    ```
    
    You may place it into your home directory under the name of `.cloudflare-ddns-config`.
    On Linux, a system-wide configuration file is also supported: `/etc/cloudflare-ddns-config`.
    
2. **Install the package**:

    ```bash
    pip install cfddns-updater
    ```
    
3. **Run the script!**

    ```bash
    cfddns_updater
    ```
    
    It's possible to specify the path to any configuration file explicitly as the only
    positional argument:
    
    ```bash
    cfddns_updater config.yml
    ```
    

Exit codes
----------
   
| Exit code | Explanation                                     |
|:---------:| ----------------------------------------------- |
| 2         | invalid command line arguments                  |
| -1        | the configuration file is not found             |
| -2        | validation of the configuration file was failed |
