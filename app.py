import settings
import importlib
import threading

class Bot:
    def __init__(self):
        self.name = getattr(settings, 'NAME', 'No Name')
        self.connectors = getattr(settings, 'CONNECTORS', [])
        self.plugins = getattr(settings, 'PLUGINS', [])

        for connector in self.connectors:
            try:
                connector_package = importlib.import_module("connectors." + connector)
                connector_obj = getattr(connector_package, connector.capitalize() + "Connector")
                connector_thread = threading.Thread(target=connector_obj, args=(self,))
                connector_thread.start()
                print("Init: ", connector)
            except Exception as err:
                print("Error al cargar el conector {name}".format(name=connector), err)

    def process_message(self, message, msg_sender, msg_to, msg_type, connector):
        for plugin in self.plugins:
            try:
                plugin_package = importlib.import_module("plugins." + plugin)
                plugin_obj = getattr(plugin_package, "process_message")
                t = threading.Thread(target=plugin_obj, args=(message, msg_sender, msg_to, msg_type, connector, self,))
                t.start()
            except Exception as err:
                print("Error al llamar al plugin {name}".format(name=plugin), err)

Bot()