import yaml
import json


def yaml_to_karabiner(yaml_file_path):
    """
    Convert YAML configuration to Karabiner JSON.

    :param yaml_file_path: Path to the YAML configuration file
    :return: A dictionary representing Karabiner JSON structure
    """
    with open(yaml_file_path, 'r') as file:
        yaml_data = yaml.safe_load(file)

    karabiner_config = {
        "description": "KBKeyboard",
        "manipulators": []
    }

    layers = yaml_data.get('layers', {})

    for layer_num, layer_data in layers.items():
        for key, value in layer_data.items():
            manipulator = {
                "from": {
                    "key_code": key.split(',')[0]
                    # Handle the first key in case of multi-key config
                },
                "to": [],
                "type": "basic"
            }

            # Check if the key is of type 'single'
            if value['type'] == 'single':
                manipulator['to'].append({
                    "key_code": value['data']
                })

            # Handle app-specific conditions
            if 'app' in value:
                app_condition = {
                    "bundle_identifiers": [f"^{app}$" for app in value['app']]
                }
                if value.get('app_mode') == 'inclusive':
                    app_condition["type"] = "frontmost_application_if"
                elif value.get('app_mode') == 'exclusive':
                    app_condition["type"] = "frontmost_application_unless"

                manipulator['conditions'] = [app_condition]

            # Add to the list of manipulators
            karabiner_config['manipulators'].append(manipulator)

    return karabiner_config


# Example usage:
yaml_file = 'config.yaml'
karabiner_json = yaml_to_karabiner(yaml_file)

# Output the Karabiner JSON (could be saved to a file)
print(json.dumps(karabiner_json, indent=4))