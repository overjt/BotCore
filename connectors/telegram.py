from libs.pytg import Telegram
from libs.pytg.utils import coroutine
import sqlite3 as lite
import threading
import settings
import os
import traceback
from utils import stringToBase64, base64ToString

class TelegramConnector:
    
    def __init__(self, bot):
        self.bot = bot
        try:
            con = lite.connect(getattr(settings, 'DB_NAME', "botcore.db"))
            cur = con.cursor()    
            cur.execute('CREATE TABLE IF NOT EXISTS telegram_file_cache (id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT, message_id TEXT);')
            cur.execute('CREATE TABLE IF NOT EXISTS telegram_uploading_file (id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT, peer_id TEXT, sent INTEGER DEFAULT 0);')
        except Exception as err:
            pass
        finally:
            if con:
                con.close()
        tg = Telegram(
            telegram=settings.CONNECTORS_CONFIG['telegram']['bin_path'],
            pubkey_file=settings.CONNECTORS_CONFIG['telegram']['pub_path'])
        self.receiver = tg.receiver
        self.sender = tg.sender
        try:
            print(self.sender.get_self())
            self.own_id = self.sender.get_self()["id"]
        except:
            self.own_id = None
        self.receiver.start()
        self.receiver.message(self.main_loop())


    @coroutine 
    def main_loop(self):
        while True:
            msg = (yield)
            try:

                if msg.event != "message":
                    continue
                
                if msg.sender.id == msg.receiver.id and msg.sender.id == self.own_id:
                    if msg.media.type == "document":
                        file_path = msg.media.caption
                        if not file_path:
                            continue
                        try:
                            con = lite.connect(getattr(settings, 'DB_NAME', "botcore.db"))
                            cur = con.cursor()    
                            cur.execute("INSERT INTO telegram_file_cache VALUES(null,?,?)", [file_path, msg.id])
                            con.commit()
                            cur.execute("SELECT peer_id FROM telegram_uploading_file WHERE path = ? and sent = ?", [file_path, '0'])
                            records = cur.fetchall()
                            for peer_id in records:
                                cur.execute("UPDATE telegram_uploading_file set sent = '1' where path = ? and peer_id = ?", [file_path, peer_id[0]])
                                con.commit()
                                self.sender.fwd_media(peer_id[0], msg.id)
                        except Exception as err:
                            print("[Telegram][send_file][main_loop]", err)
                        finally:
                            if con:
                                con.close()

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

                self.sender.status_online()
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
        try:
            con = lite.connect(getattr(settings, 'DB_NAME', "botcore.db"))
            cur = con.cursor()    
            cur.execute("SELECT message_id FROM telegram_file_cache WHERE path = ?", [file_path])
            message_id = cur.fetchone()
            if message_id:
                try:
                    self.sender.fwd_media(to["params"].cmd, message_id[0])
                except Exception as err:
                    cur.execute("INSERT INTO telegram_uploading_file VALUES(null,?,?, '0')", [file_path, to["params"].cmd])
                    con.commit()
                    self.sender.send_file(self.own_id, file_path, file_path)
            else:
                cur.execute("INSERT INTO telegram_uploading_file VALUES(null,?,?, '0')", [file_path, to["params"].cmd])
                con.commit()
                self.sender.send_file(self.own_id, file_path, file_path)
        except Exception as err:
            traceback.print_exc()
            print("[Telegram][send_file]", err)
        finally:
            if con:
                con.close()



        
