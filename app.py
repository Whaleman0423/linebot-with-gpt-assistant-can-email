# https://github.com/line/line-bot-sdk-python/blob/master/README.rst
import os
from flask import Flask, request, abort
from dotenv import load_dotenv
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
from openai_helper import deal_with_user_text_request_and_return_text_response

# 載入 .env 檔案
load_dotenv()
line_channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
line_channel_secret = os.getenv('LINE_CHANNEL_SECRET')


app = Flask(__name__)

configuration = Configuration(access_token=line_channel_access_token)
handler = WebhookHandler(line_channel_secret)


@app.route('/ping')
def hello_world():
    return 'pong'


@app.route("/callback", methods=['POST'])
def callback():
    # 獲取 X-Line-Signature header 的值
    signature = request.headers['X-Line-Signature']

    # 獲取請求主體作為文字
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info(
            "Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    @handler.add(MessageEvent, message=TextMessageContent)
    def handle_message(event):
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            return_msgs = deal_with_user_text_request_and_return_text_response(event.source.user_id,
                                                                               event.message.text)

            line_messages = [TextMessage(text=msg) for msg in return_msgs]

            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=line_messages
                )
            )
    return 'OK'


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
