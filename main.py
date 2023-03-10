from __future__ import unicode_literals
import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import aiohttp
import openai

import configparser

import random

app = Flask(__name__)

# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))
openai.api_key = config.get('line-bot', 'open_ai_key')

# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        print(body, signature)
        handler.handle(body, signature)

    except InvalidSignatureError:
        abort(400)

    return 'OK'


# 學你說話
@handler.add(MessageEvent, message=TextMessage)
def pretty_echo(event):
    if event.message.text.startswith('!clione ') or event.source.type != 'group':
        if event.message.text.startswith('!clione '):
            request_text = event.message.text.replace('!clione ', '')
        else:
            request_text = event.message.text

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=request_text,
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )
        responseMessage = response.choices[0].text
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=responseMessage.lstrip())
        )


if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = "5000")