from libs.webwhatsapi import WhatsAPIDriver
from settings import CONNECTORS_CONFIG
import threading

class WhatsappConnector:
    
    def __init__(self, bot):
        self.bot = bot
        self.wa = WhatsAPIDriver()
        self.wa.create_callback(self.main_loop)

    def main_loop(self,messages):
        for message in messages:
            try:
                msg_to = {
                    "id": message["id"],
                    "name": message.get("contact", ""),
                    "params": {}
                }
                for msg_text in message["messages"]:
                    t = threading.Thread(target=self.bot.process_message, args=(msg_text["message"],msg_text["sender"],msg_to,"chatWIP", self,))
                    t.start()
            except Exception as err:
                print("Error al enviar WA", err)

    def send_message(self, to, message):
        print("enviando msg", to, message)
        self.wa.send_to_whatsapp_id(to["id"], message)
