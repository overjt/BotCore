from libs.pytg import Telegram
from libs.pytg.utils import coroutine
from settings import CONNECTORS_CONFIG

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
            self.sender.status_online()
            self.bot.process_message(msg,"2","3","4")

    def send_msg(self, to, message):
        telegram_to = to.params
        self.sender.send_msg(telegram_to.peer.cmd, message)
