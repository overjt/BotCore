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
        self.files_cache_group = "$020000008f6192120000000000000000"
        self.receiver = tg.receiver
        self.sender = tg.sender
        try:
            print(self.sender.get_self())
            self.own_id = self.sender.get_self()["id"]
        except:
            self.own_id = None
        self.receiver.start()
        self.receiver.message(self.main_loop)

    def main_loop(self, msg):
        try:
            if msg.event != "message":
                return
            
            if self.files_cache_group == msg.receiver.id and msg.sender.id == self.own_id:
                if msg.media.type == "document":
                    file_path = msg.media.caption
                    if not file_path:
                        return
                    try:
                        self.bot.mongoDB.telegram_file_cache.insert_one({
                            "path": file_path,
                            "message_id": msg.id
                        })
                        records = self.bot.mongoDB.telegram_uploading_file.find({
                            "path": file_path,
                            "sent": False
                        })
                        for record in records:
                            self.bot.mongoDB.telegram_uploading_file.find_one_and_update({"_id": record["_id"]}, 
                                 {"$set": {"sent": True}})
                            self.sender.fwd_media(record["peer_id"], msg.id)
                    except Exception as err:
                        print("[Telegram][send_file][main_loop]", err)

            if msg.own:
                return # we don't want to process this message.
            if not hasattr(msg, "text"):
                return
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

    def _send_file(self, to, file_path, caption = None):
        port = getOpenPort()
        """tgSendFile = Telegram(
            telegram=settings.CONNECTORS_CONFIG['telegram']['bin_path'],
            pubkey_file=settings.CONNECTORS_CONFIG['telegram']['pub_path'], port=port)
        rec = tgSendFile.receiver
        sen = tgSendFile.sender
        #rec.start()"""
        try:
            self.sender.send_file(to, file_path, caption)
        except Exception as err:
            traceback.print_exc()
            print("[Telegram][_send_file]", err)
        finally:
            try:
                #tgSendFile.stop_cli()
                pass
            except:
                pass
            
        
    def send_file(self, to, file_path, is_reply = False):
        try:
            record = self.bot.mongoDB.telegram_file_cache.find_one({"path": file_path})
            if record:
                try:
                    self.sender.fwd_media(to["params"].cmd, record["message_id"])
                except Exception as err:
                    self.bot.mongoDB.telegram_file_cache.remove({ "path": file_path })
                    traceback.print_exc()
                    print("[Telegram][send_file][message_id ]", err)
                    self.bot.mongoDB.telegram_uploading_file.insert_one({
                        "path": file_path,
                        "peer_id": to["params"].cmd,
                        "sent": False
                    })
                    self._send_file(self.files_cache_group, file_path, file_path)
            else:
                self.bot.mongoDB.telegram_uploading_file.insert_one({
                    "path": file_path,
                    "peer_id": to["params"].cmd,
                    "sent": False
                })
                self._send_file(self.files_cache_group, file_path, file_path)
        except Exception as err:
            traceback.print_exc()
            print("[Telegram][send_file]", err)



        
