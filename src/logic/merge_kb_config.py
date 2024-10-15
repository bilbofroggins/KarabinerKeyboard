import json
import os
import sys

from src.logic.key_mappings import modification_keys
from src.logic.yaml_config import YAML_Config


# Function to convert YAML to Karabiner JSON with updated layer handling
def yaml_to_karabiner(yaml_data):
    karabiner_rule = {
        "description": "KBKeyboard",
        "manipulators": []
    }

    # Extract layer numbers and determine the maximum layer
    layers = yaml_data['layers']
    layer_numbers = [int(layer) for layer in layers.keys()]
    max_layer = max(layer_numbers)

    # Process each layer and its keys
    for layer, keys in layers.items():
        layer_num = int(layer)
        for key, details in keys.items():
            key_data = details['data']
            key_type = details['type']
            apps = details.get('app', None)

            # Determine the 'from' part
            from_dict = {}
            if ',' in key:
                from_dict['simultaneous'] = [{"key_code": kc.strip()} for kc in key.split(',')]
            else:
                from_dict['key_code'] = key

            # Make all modifiers optional
            from_dict['modifiers'] = {
                "optional":
                [
                    "left_shift",
                    "left_control",
                    "left_alt",
                    "left_command",
                    "right_shift",
                    "right_control",
                    "right_alt",
                    "right_command"
                ]
            }

            # Build conditions
            conditions = []

            # For layer 0
            if layer_num == 0:
                # All higher layer variables must be 0 (no higher layers active)
                for higher_layer in range(1, max_layer + 1):
                    conditions.append({"type": "variable_if", "name": f"layer{higher_layer}", "value": 0})
            else:
                # Current layer variable must be 1
                conditions.append({"type": "variable_if", "name": f"layer{layer_num}", "value": 1})
                # All higher layer variables must be 0
                for higher_layer in range(layer_num + 1, max_layer + 1):
                    conditions.append({"type": "variable_if", "name": f"layer{higher_layer}", "value": 0})

            # Add app conditions if any
            if apps:
                conditions.append({
                    "type": "frontmost_application_if",
                    "bundle_identifiers": [f".*{app}.*" for app in apps]
                })

            # Handle different key types
            if 'layer|MO' in key_type:  # Momentary layer
                target_layer = int(key_data)
                manipulator = {
                    "type": "basic",
                    "from": from_dict,
                    "to": [
                        {"set_variable": {"name": f"layer{target_layer}", "value": 1}}
                    ],
                    "to_after_key_up": [
                        {"set_variable": {"name": f"layer{target_layer}", "value": 0}}
                    ],
                    "conditions": conditions
                }
                karabiner_rule['manipulators'].append(manipulator)

            elif 'layer|LT' in key_type:  # Momentary layer with tap
                target_layer = int(key_data)
                manipulator = {
                    "type": "basic",
                    "from": from_dict,
                    "to": [
                        {"set_variable": {"name": f"layer{target_layer}", "value": 1}}
                    ],
                    "to_after_key_up": [
                        {"set_variable": {"name": f"layer{target_layer}", "value": 0}}
                    ],
                    "to_if_alone": [
                        {"key_code": key}  # Acts as the normal key if tapped
                    ],
                    "conditions": conditions
                }
                karabiner_rule['manipulators'].append(manipulator)

            elif 'layer|TO' in key_type:  # Toggle layer
                target_layer = int(key_data)
                manipulator = {
                    "type": "basic",
                    "from": from_dict,
                    "to": [
                        {
                            "set_variable": {
                                "name": f"layer{target_layer}",
                                "value": 1
                            }
                        }
                    ],
                    "conditions": conditions
                }
                karabiner_rule['manipulators'].append(manipulator)

            elif key_type == 'single':
                # Split key_data into modifiers and key_code
                key_parts = key_data.split(' + ')
                key_code = key_parts[-1]
                modifiers = key_parts[:-1] if len(key_parts) > 1 else []

                # Filter out any invalid modifiers
                modifiers = [mod for mod in modifiers if mod in modification_keys]

                manipulator = {
                    "type": "basic",
                    "from": from_dict,
                    "to": [{"key_code": key_code, "modifiers": modifiers}],
                    "conditions": conditions
                }
                karabiner_rule['manipulators'].append(manipulator)

            elif key_type == 'multi':
                # Handle sequence of key presses, potentially with modifiers
                to_sequence = []
                for item in key_data:
                    if isinstance(item, str):
                        # Split into modifiers and key_code
                        key_parts = item.split(' + ')
                        key_code = key_parts[-1]
                        modifiers = key_parts[:-1] if len(key_parts) > 1 else []
                        modifiers = [mod for mod in modifiers if mod in modification_keys]
                        to_sequence.append({"key_code": key_code, "modifiers": modifiers})
                    else:
                        # If item is not a string, ignore or handle as needed
                        continue

                manipulator = {
                    "type": "basic",
                    "from": from_dict,
                    "to": to_sequence,
                    "conditions": conditions
                }
                karabiner_rule['manipulators'].append(manipulator)

            elif key_type == 'osm':  # One-shot modifier
                # For one-shot modifiers, the last key is the key_code, others are modifiers
                key_code = key_data[-1]
                modifiers = [mod for mod in key_data[:-1] if mod in modification_keys]
                manipulator = {
                    "type": "basic",
                    "from": from_dict,
                    "to": [{
                        "key_code": key_code,
                        "modifiers": modifiers,
                        "one_shot": True
                    }],
                    "conditions": conditions
                }
                karabiner_rule['manipulators'].append(manipulator)

            elif key_type == 'shell':
                manipulator = {
                    "type": "basic",
                    "from": from_dict,
                    "to": [{"shell_command": key_data}],
                    "conditions": conditions
                }
                karabiner_rule['manipulators'].append(manipulator)

    return karabiner_rule

# Function to merge the generated rule into the Karabiner config file
def merge_into_karabiner_config():
    yaml_data = YAML_Config().data
    rule = yaml_to_karabiner(yaml_data)
    # Path to Karabiner configuration file
    karabiner_config_path = os.path.expanduser('~/.config/karabiner/karabiner.json')

    # Load existing configuration
    with open(karabiner_config_path, 'r') as f:
        config = json.load(f)

    # Find the selected profile
    selected_profile = None
    for profile in config['profiles']:
        if profile.get('selected', False):
            selected_profile = profile
            break

    if not selected_profile:
        print("No selected profile found in Karabiner configuration.")
        sys.exit(1)

    # Ensure complex_modifications and rules exist
    if 'complex_modifications' not in selected_profile:
        selected_profile['complex_modifications'] = {}
    if 'rules' not in selected_profile['complex_modifications']:
        selected_profile['complex_modifications']['rules'] = []

    # Find existing rule with the same description
    existing_rule_index = None
    for idx, rule_item in enumerate(selected_profile['complex_modifications']['rules']):
        if rule_item.get('description') == rule['description']:
            existing_rule_index = idx
            break

    # If the rule exists, overwrite it; else, add it
    if existing_rule_index is not None:
        selected_profile['complex_modifications']['rules'][existing_rule_index] = rule
        print(f"Rule '{rule['description']}' has been updated in the selected profile.")
    else:
        selected_profile['complex_modifications']['rules'].append(rule)
        print(f"Rule '{rule['description']}' has been added to the selected profile.")

    # Save the updated configuration back to the file
    with open(karabiner_config_path, 'w') as f:
        json.dump(config, f, indent=4)