import os

import yaml

from src.config import config


class YAML_Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(YAML_Config, cls).__new__(cls)

            cls._instance.data = None
            cls._instance.overrides = {}
            cls._instance.types = {}
            cls._instance.simultaneous_overrides = {}

            cls._instance.load_yaml()
        return cls._instance

    def load_yaml(self):
        try:
            with open(config.yaml_location, 'r') as file:
                self.data = yaml.safe_load(file)
        except FileNotFoundError:
            self.data = {'layers': {0:{}}}
            self.save_yaml()

    def save_yaml(self):
        # Ensure the parent directory exists
        os.makedirs(os.path.dirname(config.yaml_location), exist_ok=True)

        with open(config.yaml_location, 'w') as file:
            yaml.safe_dump(self.data, file)

    def layers(self):
        return self.data.get('layers', {}).keys()

    def delete_layer(self, layer):
        del self.data['layers'][int(layer)]
        self.save_yaml()

    def save(self, layer, key, type, data):
        cache_key = str(layer) + ':' + key
        if type is None:
            if key in self.data['layers'][int(layer)]:
                del self.data['layers'][int(layer)][key]
        else:
            self.data['layers'][int(layer)][key] = {'type': type, 'data': data}

        if cache_key in self.overrides:
            del self.overrides[cache_key]
        if cache_key in self.types:
            del self.types[cache_key]
        if int(layer) in self.simultaneous_overrides:
            del self.simultaneous_overrides[int(layer)]
        self.save_yaml()

    def key_type(self, layer, key_to_check):
        layer = int(layer)
        cache_key = str(layer) + ':' + key_to_check
        if cache_key in self.types:
            return self.types[cache_key]

        layers = self.data.get('layers', {})
        layer_data = layers[layer]
        if key_to_check in layer_data:
            value = layer_data[key_to_check]
            self.types[cache_key] = value['type']
            return value['type']
        self.types[cache_key] = ""
        return ""

    def key_overriddes(self, layer, key_to_check):
        layer = int(layer)
        cache_key = str(layer) + ':' + key_to_check
        if cache_key in self.overrides:
            return self.overrides[cache_key]

        layers = self.data.get('layers', {})
        layer_data = layers[layer]
        if key_to_check in layer_data:
            value = layer_data[key_to_check]
            if value['type'] == 'single':
                return_data = ('single', value['data'])
                self.overrides[cache_key] = return_data
                return return_data
            else:
                return_data = ('complex', value['data'])
                self.overrides[cache_key] = return_data
                return return_data

        return_data = (None, None)
        self.overrides[cache_key] = return_data
        return return_data

    # Handle cases where multiple keys are specified (e.g., 'j,k')
    def all_simultaneous_overrides(self, layer):
        layer = int(layer)
        if layer in self.simultaneous_overrides:
            return self.simultaneous_overrides[layer]

        ret = {}
        layers = self.data.get('layers', {})
        layer_data = layers[layer]
        for key, value in layer_data.items():
            key_list = key.split(',')
            if len(key_list) > 1:
                ret[key] = value
        self.simultaneous_overrides[layer] = ret
        return ret
