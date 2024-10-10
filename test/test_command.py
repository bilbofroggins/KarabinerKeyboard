from abc import ABC, abstractmethod

# Command interface with execute and undo methods
class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def undo(self):
        pass

# Invoker class to execute and manage the history of commands
class CommandManager:
    def __init__(self):
        self.history = []

    def execute_command(self, command):
        command.execute()
        self.history.append(command)

    def undo(self):
        if self.history:
            command = self.history.pop()
            command.undo()
        else:
            print("No commands to undo!")



class GenericChangeCommand(Command):
    def __init__(self, config, key, new_data):
        self.layer = key['layer']
        self.code = key['code']
        self.config = config
        self.prev_type = config['layers'][self.layer][self.code]['type']
        self.prev_data = config['layers'][self.layer][self.code]['data']
        self.new_data = new_data

    def execute(self):
        config['layers'][self.layer][self.code]['type'] = self.new_data['type']
        config['layers'][self.layer][self.code]['data'] = self.new_data['data']

    def undo(self):
        config['layers'][self.layer][self.code]['type'] = self.prev_type
        config['layers'][self.layer][self.code]['data'] = self.prev_data

class ChangeAppSpecificCommand(Command):
    def __init__(self, config, key, new_apps):
        self.layer = key['layer']
        self.code = key['code']
        self.config = config
        if 'app' not in config['layers'][self.layer][self.code]:
            self.prev_apps = []
        else:
            self.prev_apps = config['layers'][self.layer][self.code]['app']
        self.new_apps = new_apps

    def execute(self):
        if len(self.new_apps):
            config['layers'][self.layer][self.code]['app'] = self.new_apps
        else:
            config['layers'][self.layer][self.code].pop('app')

    def undo(self):
        if len(self.prev_apps):
            config['layers'][self.layer][self.code]['app'] = self.prev_apps
        else:
            config['layers'][self.layer][self.code].pop('app')


import yaml

# Load configuration from a YAML file
def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Save configuration back to the YAML file
def save_config(file_path, config_data):
    with open(file_path, 'w') as file:
        yaml.dump(config_data, file)

# Initialize config and command manager
config_file = 'test/test_config.yaml'
config = load_config(config_file)
command_manager = CommandManager()

key_to_change = {"layer": 0, "code": "tab"}
data_to_change = {"type": "single", "data": "delete_or_backspace"}
# Create and execute commands
# change_theme_command = GenericChangeCommand(config, key_to_change, data_to_change)
# command_manager.execute_command(change_theme_command)

key_to_change = {"layer": 0, "code": "left_cmd"}
app_list = ['Lens', 'Chrome']
# app_list = []
change_theme_command = ChangeAppSpecificCommand(config, key_to_change, app_list)
command_manager.execute_command(change_theme_command)

# Save updated config to file
save_config(config_file, config)

# # Undo the theme change
# command_manager.undo()
#
# # Save reverted config to file
# save_config(config_file, config)