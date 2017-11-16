from libs.pytg import Telegram
from libs.pytg.utils import coroutine
from settings import CONNECTORS_CONFIG
import threading

class TelegramConnector:
    
    def __init__(self, bot):
        self.bot = bot
        tg = Telegram(
            telegram=CONNECTORS_CONFIG['telegram']['bin_path'],
            pubkey_file=CONNECTORS_CONFIG['telegram']['pub_path'])
        self.receiver = tg.receiver
        self.sender = tg.sender
        self.receiver.start()
        self.receiver.message(self.main_loop())

    
    @coroutine 
    def main_loop(self):
        while True:
            msg = (yield)
            try:

                if msg.event != "message":
                    continue  # is not a message.
                if msg.own:  # the bot has send this message.
                    continue # we don't want to process this message.

                msg_sender = {
                    "id": msg.sender.id,
                    "name": msg.sender.name,
                    "params": msg.sender
                }

                msg_to = {
                    "id": msg.peer.id,
                    "name": msg.peer.name,
                    "params": msg.peer
                }

                self.sender.status_online()
                t = threading.Thread(target=self.bot.process_message, args=(msg.text,msg_sender,msg_to,msg.peer.type, self,))
                t.start()
            except Exception as err:
                raise

    def send_message(self, to, message):
        self.sender.send_msg(to["params"].cmd, message)
