import json
import asyncio
import aiohttp

MESSAGE_UPDATES = ['message', 'edited_message', 'channel_post', 'edited_channel_post']
RETRY_TIMEOUT = 30
API_TIMEOUT = 60
RETRY_CODES = [429, 500, 502, 503, 504]


class Telegram(object):

    def __init__(self, message, bot):
        self.chat_id = message['chat']['id']
        self.message = message
        self.bot = bot

    def send_msg(self, text, **options):
        return self.bot.send_message(self.chat_id, text, **options)

    def reply(self, text):
        return self.send_msg(text, reply_to_message_id=self.message['message_id'])

    def send_pic(self):
        pass
