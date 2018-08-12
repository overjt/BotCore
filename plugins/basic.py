import datetime
import math
from utils import evalRegex
START = datetime.datetime.now()


def process_message(message, msg_sender, msg_to, msg_type, connector, bot):
    if message.lower() == "hola {bot_name}".format(bot_name=bot.name.lower()) or message.lower() == "hola":
        connector.send_message(msg_to, "Hola {sender_name}".format(
            sender_name=msg_sender["name"]))
    elif message.lower() == "/uptime":
        end = datetime.datetime.now()
        diff = end - START
        seconds = diff.seconds
        minutes = math.floor(seconds / 60)
        hours = math.floor(minutes/60)
        days = diff.days

        hours = hours - (days * 24)
        minutes = minutes - (days * 24 * 60) - (hours * 60)
        seconds = seconds - (days * 24 * 60 * 60) - \
            (hours * 60 * 60) - (minutes * 60)

        msg_time = "Llevo encendida sin reiniciarme:\n{days}\n{hours}\n{minutes}\n{seconds}\nDesde: {start}".format(
            days=str(days) + " día" + ("s" if days > 0 else ""),
            hours=str(hours) + " hora" + ("s" if hours > 0 else ""),
            minutes=str(minutes) + " minuto" + ("s" if minutes > 0 else ""),
            seconds=str(seconds) + " segundo" + ("s" if seconds > 0 else ""),
            start=START.strftime("%Y-%m-%d %H:%M:%S"),
        )
        connector.send_message(msg_to, msg_time)
    elif message.lower() == ".ping":
        connector.send_message(msg_to, "pong")
    elif message.lower() == ".test":
        connector.send_image(msg_to, "media/images/test.png", "Testing, testing...")
    else:
        regex = "(?:^{bot_name} |^\.)di (.*)$".format(bot_name=bot.name.lower())
        found = evalRegex(regex, message)
        if found:
            connector.send_message(msg_to, found)

