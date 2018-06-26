from webwhatsapi import WhatsAPIDriver, WhatsAPIException
from settings import CONNECTORS_CONFIG
import threading
import time
import os
class WhatsappConnector:
    
    def __init__(self, bot):
        self.bot = bot
        profile = os.path.join(os.getcwd(), "firefox_cache", self.bot.name.lower())
        try:
            self.wa = WhatsAPIDriver(profile=profile, headless=True)
        except WhatsAPIException as err:
            print("[WhatsappConnector]", err)
            self.wa = WhatsAPIDriver()
            self.wa.wait_for_login()
            self.wa._profile_path = profile
            if not os.path.exists(profile):
                os.makedirs(profile)
            self.wa.save_firefox_profile(True)

        self.wa.subscribe_new_messages(NewMessageObserver(self))
        while True:
            time.sleep(60)

    def send_message(self, to, message, is_reply = False):
        self.wa.send_message_to_id(to["id"], message)
    
    def send_image(self, to, img_path, caption=None, is_reply = False):
        #WIP
        self.wa.send_message_to_id(to["id"], caption)

class NewMessageObserver:
    def __init__(self, connector):
        self.connector = connector
    
    def on_message_received(self, new_messages):
        for message in new_messages:
            try:
                
                msg_sender = {
                    "id": message.sender.id,
                    "name": message.sender.formatted_name,
                    "params": message.sender,
                    "message_id": message.id,
                    "is_admin": True if str(message.sender.id) in CONNECTORS_CONFIG['whatsapp']['admin_list'] else False
                }
                msg_to = {
                    "id": message.chat_id,
                    "name": message.chat_id,
                    "params": {},
                    "message_id": message.id,
                }

                t = threading.Thread(target=self.connector.bot.process_message, args=(message.content,msg_sender,msg_to,"chatWIP", self.connector,))
                t.start()
            except Exception as err:
                print("Error al enviar WA", err)