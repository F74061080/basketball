import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from fsm import TocMachine
from utils import send_text_message

load_dotenv()


machine = TocMachine(
    states=["user", "enter_player", "add_player", "success_player", "enter_number", "statistic",
            "twopt", "threept", "freept",
            "twoptmade", "twoptmiss", 
            "threeptmade", "threeptmiss",
            "freeptmade", "freeptmiss"],
    transitions=[
        {
            "trigger": "advance", 
            "source": "user", 
            "dest": "enter_player",
            "conditions": "is_going_to_enter_player",
        },
        {
            "trigger": "advance", 
            "source": "enter_player", 
            "dest": "add_player",
            "conditions": "is_going_to_add_player",
        },
        {
            "trigger": "advance", 
            "source": "add_player", 
            "dest": "success_player",
            "conditions": "is_going_to_success_player"
        },
        {
            "trigger": "advance",
            "source": "success_player",
            "dest": "enter_player",
            "conditions": "is_going_to_enter_player2",
        },
        {
            "trigger": "advance",
            "source": "enter_player",
            "dest": "enter_number",
            "conditions": "is_going_to_enter_number",
        },
        {
            "trigger": "advance",
            "source": "enter_number",
            "dest": "statistic",
            "conditions": "is_going_to_statistic",
        },
        {
            "trigger": "advance",
            "source": "statistic",
            "dest": "twopt",
            "conditions": "is_going_to_twopt",
        },
        {
            "trigger": "advance",
            "source": "twopt",
            "dest": "twoptmade",
            "conditions": "is_going_to_twoptmade",
        },
        {
            "trigger": "advance",
            "source": "twopt",
            "dest": "twoptmiss",
            "conditions": "is_going_to_twoptmiss",
        },
        {
            "trigger": "advance",
            "source": "statistic",
            "dest": "threept",
            "conditions": "is_going_to_threept",
        },
        {
            "trigger": "advance",
            "source": "threept",
            "dest": "threeptmade",
            "conditions": "is_going_to_threeptmade",
        },
        {
            "trigger": "advance",
            "source": "threept",
            "dest": "threeptmiss",
            "conditions": "is_going_to_threeptmiss",
        },
        {
            "trigger": "advance",
            "source": "statistic",
            "dest": "freept",
            "conditions": "is_going_to_freept",
        },
        {
            "trigger": "advance",
            "source": "freept",
            "dest": "freeptmade",
            "conditions": "is_going_to_freeptmade",
        },
        {
            "trigger": "advance",
            "source": "freept",
            "dest": "freeptmiss",
            "conditions": "is_going_to_freeptmiss",
        },
        {
            "trigger": "advance",
            "source": ["twoptmade", "twoptmiss", "threeptmade", "threeptmiss", "freeptmade", "freeptmiss"],
            "dest": "enter_number",
            "conditions": "gotit",
        },
    ],
    initial="user",
    auto_transitions=False,
    show_conditions=True,
)

app = Flask(__name__, static_url_path="")


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.message.text)
        )

    return "OK"





@app.route("/webhook", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f"\nFSM STATE: {machine.state}")
        print(f"REQUEST BODY: \n{body}")
        response = machine.advance(event)
        if response == False:
            send_text_message(event.reply_token, "Not Entering any State")

    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
