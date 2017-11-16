import settings
import importlib

class Bot:
    def __init__(self):
        self.name = getattr(settings, 'NAME', 'No Name')
        self.connectors = getattr(settings, 'CONNECTORS', 'No Name')
        for connector in self.connectors:
            try:
                connector_package = importlib.import_module("connectors." + connector)
                connector_obj = getattr(connector_package, connector.capitalize() + "Connector")
                connector_obj(self)
            except Exception as err:
                print("Error al cargar el conector {name}".format(name=connector), err)

    def process_message(self, message, sender, to, type_msg):
        print(message, sender, to, type_msg)

Bot()