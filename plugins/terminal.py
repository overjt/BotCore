from utils import evalRegex
import subprocess


def process_message(message, msg_sender, msg_to, msg_type, connector, bot):
    regex = "(?:^{bot_name} |^\.)term (.*)$".format(bot_name=bot.name.lower())
    found = evalRegex(regex, message)
    if found and msg_sender.get("is_admin"):
        try:
            response = subprocess.run(
                found, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        except Exception as err:
            print("[Terminal]", err)

        for x in ["stdout", "stderr"]:
            msg = None
            try:
                msg = getattr(response, x).decode("utf-8")
            except Exception as err:
                print("[Terminal][MSG]", err)
            if msg:
                connector.send_message(msg_to, msg)
