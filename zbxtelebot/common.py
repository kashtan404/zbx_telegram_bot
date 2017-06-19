import requests
import json
import configparser


def conf(save=False, token=''):
    config = configparser.ConfigParser()
    config.read('.\.\settings.py')
    if save:
        config.set('Zabbix', 'auth', token)
        with open('.\.\settings.py', 'w') as configfile:
            config.write(configfile)
        return True
    else:
        zabbix_user = config.get('Zabbix', 'user')
        zabbix_pass = config.get('Zabbix', 'password')
        zabbix_url = config.get('Zabbix', 'url')
        zabbix_auth = config.get('Zabbix', 'auth')
        telegram_auth = config.get('Telegram', 'telegram_token')
        botan_auth = config.get('Telegram', 'botan_token')
        return zabbix_auth, zabbix_url, zabbix_user, zabbix_pass, telegram_auth, botan_auth
