from transitions.extensions import GraphMachine

from utils import send_text_message
from linebot import *

LineBotApi = LineBotApi("nAOGBdhTa49RFIeaNBZzwFidsSGSd75vgCTo9lkhfndEsG2n58/CPw+oxHqqGMaplpxEzLDGhVtl2J9Hv4MLVbO/erT2WdA5pH0//GzukgUAhvAfxLUAFugC6tG2FNIQuOZJMiu9g8SHRid6yV6zKgdB04t89/1O/w1cDnyilFU=")


class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)
        reply_token = reply_token
        LineBotApi.push_message(reply_token, "請輸入:go to state 1")

    def is_going_to_state1(self, event):
        text = event.message.text
        return text.lower() == "go to state1"

    def is_going_to_state2(self, event):
        text = event.message.text
        return text.lower() == "go to state2"

    def is_going_to_state3(self, event):
        text = event.message.text
        return text.lower() == "go to state3"

    def on_enter_state1(self, event):
        print("I'm entering state1")

        reply_token = event.reply_token
        send_text_message(reply_token, "Trigger state1")
        #self.go_back()

    def on_exit_state1(self, event):
        print("Leaving state1")

    def on_enter_state2(self, event):
        print("I'm entering state2")

        reply_token = event.reply_token
        send_text_message(reply_token, "Trigger state2")
        #self.go_back()


    def on_exit_state2(self,event):
        print("Leaving state2")

    def on_enter_state3(self, event):
        print("I'm entering state3")

        reply_token = event.reply_token
        send_text_message(reply_token, "Trigger state3")
        
        

    def on_exit_state3(self, event):
        print("Leaving state3")
