import wolframalpha
import re
from settings import CREDENTIALS
from utils import evalRegex
from utils import downloadImage
client = wolframalpha.Client(CREDENTIALS["wolframalpha"])

def process_message(message, msg_sender, msg_to, msg_type, connector, bot):
    regex = "^=(.*)$"
    found = evalRegex(regex, message)
    if found:
        res = client.query(found)
        for pod in res.pods:
            if pod.primary or pod.title in ["Result"] or re.search('plot', pod.title, re.IGNORECASE):
                for sub in pod.subpods:
                    send_text = True
                    for img in sub.img:
                        if img.src:
                            file = downloadImage(img.src)
                            if file:
                                send_text = False
                                connector.send_image(msg_to, file, sub.plaintext)
                    if send_text and sub.plaintext:
                        connector.send_message(msg_to, str(sub.plaintext))