import json
import threading
import time
import os

"""
Simple Modification structure:
{
    "from": {
        "key_code": "caps_lock"
    },
    "to": [
        {
            "key_code": "left_control"
        }
    ]
}

Complex Modification structure:
{
    "description": "Change option+;",
    "manipulators": [
        {
            "from": {
                "key_code": "semicolon",
                "modifiers": {
                    "mandatory": [
                        "option"
                    ]
                }
            },
            "to": [
                {
                    "key_code": "hyphen"
                }
            ],
            "type": "basic"
        }
    ]
}
"""
class Overrides:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Overrides, cls).__new__(cls)
            cls._instance.config_file_path = '~/.config/karabiner/karabiner.json'

            # Structure {from: {'modifiers': [], 'key': ''}, to: {'modifiers': [], 'key': 'escape'}}
            cls._instance.modifications = []

            cls._instance.load_overrides()
            cls._instance.start_watching()
        return cls._instance

    def load_overrides(self):
        """Load the overrides from the Karabiner configuration file."""
        try:
            with open(os.path.expanduser(self.config_file_path), 'r') as file:
                self.modifications = []
                config = json.load(file)
                # Assuming the overrides are in a specific structure in the config
                complex_modifications = config['profiles'][0]['complex_modifications']['rules']
                simple_modifications = config['profiles'][0]['simple_modifications']
                for mod in simple_modifications:
                    to_add = {
                        'from': {
                            'modifiers': [],
                            'key': mod['from']['key_code']
                        },
                        'to': {
                            'modifiers': [],
                            'key': mod['to'][0]['key_code']
                        }
                    }
                    self.modifications.append(to_add)
                for mod in complex_modifications:
                    transform = mod['manipulators'][0] # TODO: take more than just one
                    to_add = {
                        'from': {
                            'modifiers': transform['from'].get('modifiers', {}).get('mandatory', {}),
                            'key': transform['from']['key_code']
                        },
                        'to': {
                            'modifiers': transform['to'][0].get('modifiers', {}),
                            'key': transform['to'][0]['key_code']
                        }
                    }
                    self.modifications.append(to_add)
        except FileNotFoundError:
            print(f"Config file not found: {self.config_file_path}")
        except json.JSONDecodeError:
            print(f"Error decoding JSON from the config file: {self.config_file_path}")

    def start_watching(self):
        """Start a new thread to watch the file for changes."""
        def watch_file():
            last_modified = os.path.getmtime(os.path.expanduser(self.config_file_path))
            while True:
                try:
                    current_modified = os.path.getmtime(os.path.expanduser(self.config_file_path))
                    if current_modified != last_modified:
                        self.load_overrides()
                        last_modified = current_modified
                except FileNotFoundError:
                    pass  # Handle file not found error
                time.sleep(1)  # Check every second

        threading.Thread(target=watch_file, daemon=True).start()

    def write_overrides(self):
        """Stub for writing back to the config file."""
        pass  # To be implemented later
