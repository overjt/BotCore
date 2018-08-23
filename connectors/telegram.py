from libs.pytg import Telegram
from libs.pytg.utils import coroutine
import threading
import settings
import os
import traceback
from utils import stringToBase64, base64ToString, getOpenPort

class TelegramConnector:
    
    def __init__(self, bot):
        self.bot = bot
        tg = Telegram(
            telegram=settings.CONNECTORS_CONFIG['telegram']['bin_path'],
            pubkey_file=settings.CONNECTORS_CONFIG['telegram']['pub_path'])
        self.receiver = tg.receiver
        self.sender = tg.sender
        self.receiver.start()
        self.receiver.message(self.main_loop())
    
    @coroutine
    def main_loop(self):
        try:
            while True:
                msg = (yield)
                try:
                    self.sender.mark_read(msg.receiver.id)
                except:
                    pass
                if msg.event != "message":
                    continue
                
                if msg.own:
                    continue # we don't want to process this message.
                if not hasattr(msg, "text"):
                    continue

                msg_sender = {
                    "id": msg.sender.id,
                    "name": msg.sender.name,
                    "params": msg.sender,
                    "message_id": msg.id,
                    "is_admin": True if str(msg.sender.peer_id) in settings.CONNECTORS_CONFIG['telegram']['admin_list'] else False
                }

                msg_to = {
                    "id": msg.peer.id,
                    "name": msg.peer.name,
                    "params": msg.peer,
                    "message_id": msg.id,
                }

                try:
                    self.sender.status_online()
                except:
                    pass
                t = threading.Thread(target=self.bot.process_message, args=(msg.text,msg_sender,msg_to,msg.peer.type, self,))
                t.start()
        except Exception as err:
            traceback.print_exc()
            print("Error al enviar TG", err)

    def send_message(self, to, message, is_reply = False):
        if is_reply:
            self.sender.reply(to["message_id"], message)
        else:
            self.sender.send_msg(to["params"].cmd, message)
    
    def send_image(self, to, img_path, caption=None, is_reply = False):
        if is_reply:
            self.sender.reply_photo(to["message_id"], img_path, caption)
        else:
            self.sender.send_photo(to["params"].cmd, img_path, caption)

    def send_file(self, to, file_path, is_reply = False):
        pass


        
