import wolframalpha
import re
client = wolframalpha.Client("8UXPJ5-3VE2YTT4TL")

def process_message(message, msg_sender, msg_to, msg_type, connector, bot):
    regex = "^=(.*)$"
    try:
        found = re.search(regex, message, re.IGNORECASE).group(1)
    except AttributeError:
        found = None
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