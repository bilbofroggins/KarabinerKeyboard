import json
import shutil
import threading
import time
import os

from src.logic.condition import Condition
from src.logic.modification import Modification
from src.logic.modification_pair import ModificationPair
from src.config import config, DiggableWrapper


class KarabinerConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KarabinerConfig, cls).__new__(cls)
            cls._instance.config_file_path = os.path.expanduser(config.karabiner_file)
            cls._instance.backup_config_file_path = os.path.expanduser('~/.config/karabiner/karabiner_back.json')

            cls._instance.modification_pairs = {}
            cls._instance.config = None

            cls._instance.supported_keys = {'type', 'from', 'to', 'conditions'}
            cls._instance.complex_unsupported_blocks = []
            cls._instance.complex_unsupported_data = {} # i: data

            cls._instance.load_overrides()
            cls._instance.start_watching()
        return cls._instance

    def load_overrides(self):
        """Load the overrides from the Karabiner configuration file."""
        try:
            i = 0
            with open(self.config_file_path, 'r') as file:
                self.modification_pairs = {} # {id: mod_pair}
                self.complex_unsupported_blocks = []
                self.config = DiggableWrapper(json.load(file))
                # Assuming the overrides are in a specific structure in the config
                complex_modifications = self.config.dig('profiles', 0, 'complex_modifications', 'rules', default=[])
                simple_modifications = self.config.dig('profiles', 0, 'simple_modifications', default=[])
                for mod in simple_modifications:
                    mod_pair = ModificationPair(
                        Modification([], mod['from']['key_code']),
                        Modification([], mod['to'][0]['key_code']),
                        None
                    )
                    self.modification_pairs[i] = mod_pair
                    i += 1
                for mod in complex_modifications:
                    if len(mod['manipulators']) > 1:
                        self.complex_unsupported_blocks.append(mod)
                        continue
                    if len(mod['manipulators'][0]['to']) > 1:
                        self.complex_unsupported_blocks.append(mod)
                        continue
                    transform = mod['manipulators'][0] # TODO: take more than just one
                    conditions = transform.dig('conditions', default=[])
                    if conditions:
                        bundle_identifiers = conditions[0].get('bundle_identifiers', {})
                        include_type_str = conditions[0].get('type', {})
                    else:
                        bundle_identifiers = []
                        include_type_str = ''

                    if 'key_code' not in transform['from'] or 'key_code' not in transform.dig('to', 0, default=''):
                        self.complex_unsupported_blocks.append(mod)
                        continue

                    mod_pair = ModificationPair(
                        Modification(transform['from'].get('modifiers', {}).get('mandatory', {}), transform['from']['key_code']),
                        Modification(transform['to'][0].get('modifiers', {}), transform['to'][0]['key_code']),
                        Condition(
                            bundle_identifiers,
                            include_type_str
                        )
                    )
                    self.modification_pairs[i] = mod_pair
                    i += 1

        except FileNotFoundError:
            print(f"Config file not found: {self.config_file_path}")
        except json.JSONDecodeError:
            print(f"Error decoding JSON from the config file: {self.config_file_path}")

    def start_watching(self):
        """Start a new thread to watch the file for changes."""
        def watch_file():
            last_modified = os.path.getmtime(self.config_file_path)
            while True:
                try:
                    current_modified = os.path.getmtime(self.config_file_path)
                    if current_modified != last_modified:
                        self.load_overrides()
                        last_modified = current_modified
                except FileNotFoundError:
                    pass  # Handle file not found error
                time.sleep(1)  # Check every second

        threading.Thread(target=watch_file, daemon=True).start()

    def backup_exists(self):
        return os.path.exists(self.backup_config_file_path)

    def help_blow_away_config(self):
        if self.backup_exists():
            shutil.copyfile(self.backup_config_file_path, self.config_file_path)
            os.remove(self.backup_config_file_path)

    def write_overrides(self, modification_pairs):
        for i, modification_pair in modification_pairs.items():
            self.modification_pairs[i] = modification_pair

        """Write back to the config file."""
        if not os.path.exists(self.backup_config_file_path):
            shutil.copyfile(self.config_file_path, self.backup_config_file_path)

        self.config['profiles'][0]['simple_modifications'] = []
        self.config['profiles'][0]['complex_modifications']['rules'] = [mod.to_json() for _, mod in self.modification_pairs.items()]

        for block in self.complex_unsupported_blocks:
            self.config['profiles'][0]['complex_modifications']['rules'].append(block)

        with open(self.config_file_path, 'w') as file:
            json.dump(self.config, file, indent=4)

    def remove_override(self, id):
        del self.modification_pairs[id]

        """Write back to the config file."""
        self.write_overrides(self.modification_pairs)