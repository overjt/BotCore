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

        #self.wa.subscribe_new_messages(NewMessageObserver(self))
        while True:
            try:
                group_messages = self.wa.get_unread()
                for group_msgs in group_messages:
                    for message in group_msgs.messages:
                        msg_sender = {
                            "id": message.sender.id,
                            "name": getattr(message.sender, 'push_name', message.sender.formatted_name),
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

                        t = threading.Thread(target=self.bot.process_message, args=(message.content,msg_sender,msg_to,"chatWIP", self,))
                        t.start()
            except Exception as err:
                print("[WhatsappConnector][NewMessages]", err)
            time.sleep(0.05)

    def send_message(self, to, message, is_reply = False):
        self.wa.send_message_to_id(to["id"], message)
    
    def send_image(self, to, img_path, caption="", is_reply = False):
        self.wa.send_media(img_path, to["id"], caption)