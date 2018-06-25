import wolframalpha
from settings import CREDENTIALS
from utils import evalRegex
client = wolframalpha.Client(CREDENTIALS["wolframalpha"])

def process_message(message, msg_sender, msg_to, msg_type, connector, bot):
    regex = "^=(.*)$"
    found = evalRegex(regex, message)
    if found:
        res = client.query(found)
        msg = ""
        for pod in res.pods:
            if pod.primary or pod.title in ["Result"] or re.search('plot', pod.title, re.IGNORECASE):
                for sub in pod.subpods:
                    for img in sub.img:
                        if img.src:
                            print("send image", img.src) #TODO: enviar imagen
                    if sub.plaintext:
                        connector.send_message(msg_to, str(sub.plaintext))
            else:
                print(pod.title)