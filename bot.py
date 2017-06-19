#!/usr/bin/python
# -*- coding: UTF-8 -*-

import zbxtelebot as zbxbot
import sys
import asyncio
import aiohttp
import re

zabbix_token, zabbix_url, zabbix_user, zabbix_pass, telegram_token, botan_token = zbxbot.common.conf()
if not zabbix_token:
    result = zbxbot.zabbix.auth(zabbix_url, zabbix_user, zabbix_pass)
    try:
        zabbix_token = result['result']
        zbxbot.common.conf(save=True, token=zabbix_token)
    except KeyError:
        print(result['error']['data'])
        sys.exit(2)
telegram_timeout = 60
API_URL = 'https://api.telegram.org/bot' + telegram_token
COMMANDS = [r'(/zabbixapi)', r'(/zabbix)', r'(/shell)']
zabbix_api = zbxbot.zabbix.Zabbix(auth=zabbix_token, url=zabbix_url)
#bot = zbxbot.telegram.Bot(api_token=telegram_token)  # ркн поблочили api.botan.io  , botan_token=botan_token)


class Bot(object):

    _online = False
    _offset = 0

    def __init__(self, telegram_token, telegram_timeout, botan_token=None):
        self.telegram_token = telegram_token
        self.telegram_timeout = telegram_timeout
        self.botan_token = botan_token
        self._session = None

    async def loop(self):
        self._online = True
        while self._online:
            updates = await self.api_call(
                'getUpdates',
                offset=self._offset + 1,
                timeout=self.telegram_timeout
            )
            self._process_updates(updates)

    def run(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.loop())
        except KeyboardInterrupt:
            self.stop()
        finally:
            loop.stop()
            loop.close()

    def stop(self):
        self._online = False

    def _process_updates(self, updates):
        for update in updates['result']:
            self._process_update(update)

    def _process_update(self, update):
        self._offset = max(self._offset, update['update_id'])
        coroutine = None
        for i in ['message', 'channel_post']:
            if i in update:
                coroutine = self.process_message(update[i])
                break
        if coroutine:
            asyncio.ensure_future(coroutine)

    def process_message(self, message):
        telegram = zbxbot.telegram.Telegram(message, bot)
        list_of_result = []
        for command in COMMANDS:
            msg = re.search(command, message['text'], re.I)
            if msg:
                if 'zabbixapi' in msg.group(0):
                    result = zabbix_api.select_command(message['text'])
                    break
                elif 'zabbix' in msg.group(0):
                    result = 'Not ready'
                    break
                elif 'shell' in msg.group(0):
                    result = 'Not ready'
                    break
        else:
            result = 'Invalid command'
        if len(result) > 4096:
            list_of_result = [result[i: i + 4000] for i in range(0, len(result), 4000)]
        for part in list_of_result:
            telegram.reply(part)
        else:
            telegram.reply(result)

    def api_call(self, method, **params):
        coroutine = self._api_call(method, **params)
        return asyncio.ensure_future(coroutine)

    async def _api_call(self, method, **params):
        url = '{0}/{1}'.format(API_URL, method)
        response = await self.session.post(url, data=params)
        print(response)
        if response.status == 200:
            return await response.json()

    @property
    def session(self):
        if not self._session:
            self._session = aiohttp.ClientSession()
        return self._session

    def __del__(self):
        try:
            if self._session:
                self._session.close()
        except:
            pass

    def send_message(self, chat_id, text, **options):
        return self.api_call('sendMessage', chat_id=chat_id, text=text, **options)

bot = Bot(telegram_token, telegram_timeout)
bot.run()
