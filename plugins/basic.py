def process_message(message, msg_sender, msg_to, msg_type, connector, bot):
    if message.lower() == "hola {bot_name}".format(bot_name=bot.name.lower()) or message.lower() == "hola":
        connector.send_message(msg_to, "Hola {sender_name}".format(sender_name=msg_sender["name"]))