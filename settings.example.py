CONNECTORS = ['telegram', 'whatsapp']
CONNECTORS_CONFIG = {
    "telegram": {
        "bin_path": "/usr/bin/telegram-cli",
        "pub_path": "/etc/telegram-cli/server.pub",
        "admin_list": []
    },
    "whatsapp": {
        "admin_list": []
    }
}

PLUGINS = ["basic", "google", "terminal", "wolfram"]

NAME = "Kari"


CREDENTIALS = {
    "google": "CHANGE_ME",
    "wolframalpha": "CHANGE_ME",
}