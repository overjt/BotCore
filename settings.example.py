#CONNECTORS = ['telegram', 'whatsapp']
CONNECTORS = ['telegram']
CONNECTORS_CONFIG = {
    "telegram": {
        "bin_path": "/usr/bin/telegram-cli",
        "pub_path": "/etc/telegram-cli/server.pub",
        "admin_list": ["62362032"]
    }
}

PLUGINS = ["basic", "google", "terminal"]

NAME = "Kari"