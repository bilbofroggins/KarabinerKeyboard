import json
import os
import sys

from src.config import config
from src.logic.key_mappings import modification_keys
from src.logic.yaml_config import YAML_Config


# Constants
KARABINER_CONFIG_PATH = config.kb_config_location
RULE_DESCRIPTION = "KBKeyboard"
OPTIONAL_MODIFIERS = [
    "left_shift", "left_control", "left_alt", "left_command",
    "right_shift", "right_control", "right_alt", "right_command"
]


def load_karabiner_config():
    """Load the Karabiner configuration file."""
    try:
        with open(KARABINER_CONFIG_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Karabiner configuration file not found at {KARABINER_CONFIG_PATH}.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {KARABINER_CONFIG_PATH}.")
        sys.exit(1)


def save_karabiner_config(config_data):
    """Save the Karabiner configuration file."""
    try:
        with open(KARABINER_CONFIG_PATH, 'w') as f:
            json.dump(config_data, f, indent=4)
    except Exception as e:
        print(f"Failed to save Karabiner configuration: {e}")
        sys.exit(1)


def get_selected_profile(config_data):
    """Retrieve the selected profile from the Karabiner configuration."""
    for profile in config_data.get('profiles', []):
        if profile.get('selected', False):
            return profile
    print("No selected profile found in Karabiner configuration.")
    sys.exit(1)


def find_rule_by_description(rules, description):
    """Find a rule within the rules list by its description."""
    for rule in rules:
        if rule.get('description') == description:
            return rule
    return None


def build_conditions(layer_num, max_layer, apps):
    """Construct the conditions for a manipulator based on the layer and applications."""
    conditions = []
    if layer_num == 0:
        # All higher layer variables must be 0 (no higher layers active)
        for higher_layer in range(1, max_layer + 1):
            conditions.append({
                "type": "variable_if",
                "name": f"layer{higher_layer}",
                "value": 0
            })
    else:
        # Current layer variable must be 1
        conditions.append({
            "type": "variable_if",
            "name": f"layer{layer_num}",
            "value": 1
        })
        # All higher layer variables must be 0
        for higher_layer in range(layer_num + 1, max_layer + 1):
            conditions.append({
                "type": "variable_if",
                "name": f"layer{higher_layer}",
                "value": 0
            })

    # Add app conditions if any
    if apps:
        conditions.append({
            "type": "frontmost_application_if",
            "bundle_identifiers": [f".*{app}.*" for app in apps]
        })
    return conditions


def build_from_dict(key):
    """Construct the 'from' dictionary for a manipulator."""
    if ',' in key:
        key_parts = [kc.strip() for kc in key.split(',')]

        # Separate modifiers from regular keys
        modifiers = [kc for kc in key_parts if kc in modification_keys]
        regular_keys = [kc for kc in key_parts if kc not in modification_keys]

        # Build the result dictionary
        result = {}

        # Handle regular keys - simultaneous if multiple, key_code if single
        if len(regular_keys) > 1:
            result["simultaneous"] = [{"key_code": kc} for kc in regular_keys]
        elif len(regular_keys) == 1:
            result["key_code"] = regular_keys[0]
        else:
            # All keys were modifiers, which shouldn't happen but handle gracefully
            # Use the first modifier as the key_code
            result["key_code"] = modifiers[0]
            modifiers = modifiers[1:]

        # Add modifiers section
        result["modifiers"] = {"optional": OPTIONAL_MODIFIERS}
        if modifiers:
            result["modifiers"]["mandatory"] = modifiers

        return result
    else:
        return {
            "key_code": key,
            "modifiers": {
                "optional": OPTIONAL_MODIFIERS
            }
        }


def yaml_to_karabiner(yaml_data):
    """Convert YAML data to Karabiner JSON with updated layer handling."""
    karabiner_rule = {
        "description": RULE_DESCRIPTION,
        "manipulators": []
    }

    if not config.enabled_flag:
        karabiner_rule["enabled"] = False

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

            from_dict = build_from_dict(key)
            conditions = build_conditions(layer_num, max_layer, apps)

            manipulator = {
                "type": "basic",
                "from": from_dict,
                "conditions": conditions
            }

            # Handle different key types
            if 'layer|MO' in key_type:  # Momentary layer
                target_layer = int(key_data)
                manipulator.update({
                    "to": [{"set_variable": {"name": f"layer{target_layer}", "value": 1}}],
                    "to_after_key_up": [{"set_variable": {"name": f"layer{target_layer}", "value": 0}}]
                })

            elif 'layer|LT' in key_type:  # Momentary layer with tap
                layernum = key_data
                tap_key_str = None
                # Handle both old format (int) and new format (dict with layer and tap_key)
                if isinstance(key_data, str):
                    layer_strings = key_data.split('|')
                    if len(layer_strings) > 1:
                        layernum = layer_strings[0]
                        tap_key_str = layer_strings[1]
                    else:
                        layernum = layer_strings[0]
                        tap_key_str = None

                target_layer = int(layernum)
                active_key = key if not tap_key_str else tap_key_str

                manipulator.update({
                    "to": [{"set_variable": {"name": f"layer{target_layer}", "value": 1}}],
                    "to_after_key_up": [{"set_variable": {"name": f"layer{target_layer}", "value": 0}}],
                    "to_if_alone": [{"key_code": active_key}]
                })

            elif 'layer|TO' in key_type:  # Toggle layer
                target_layer = int(key_data)
                manipulator.update({
                    "to": [
                        # First, set all other layers to 0
                        *[{"set_variable": {"name": f"layer{i}", "value": 0}} for i in
                          range(max_layer) if i != target_layer],
                        # Then, set the target layer to 1
                        {"set_variable": {"name": f"layer{target_layer}", "value": 1}}
                    ]
                })

            elif key_type == 'single':
                key_parts = key_data.split(' + ')
                key_code = key_parts[-1]
                modifiers = [mod for mod in key_parts[:-1] if mod in modification_keys]

                manipulator.update({
                    "to": [{
                        "key_code": key_code,
                        "repeat": False,
                        "modifiers": modifiers
                    }]
                })
                if key_code in modification_keys:
                    manipulator['to'][0]['repeat'] = True

            elif key_type == 'multi':
                to_sequence = []
                for item in key_data:
                    if isinstance(item, str):
                        key_parts = item.split(' + ')
                        key_code = key_parts[-1]
                        modifiers = [mod for mod in key_parts[:-1] if mod in modification_keys]
                        to_sequence.append({
                            "key_code": key_code,
                            "repeat": False,
                            "modifiers": modifiers
                        })
                manipulator.update({
                    "to": to_sequence
                })

            elif key_type == 'osm':  # One-shot modifier
                key_code = key_data[-1]
                modifiers = [mod for mod in key_data[:-1] if mod in modification_keys]
                manipulator.update({
                    "to": [{
                        "key_code": key_code,
                        "modifiers": modifiers,
                        "one_shot": True
                    }]
                })

            elif key_type == 'shell':
                manipulator.update({
                    "to": [{"shell_command": key_data}]
                })

            karabiner_rule['manipulators'].append(manipulator)

    return karabiner_rule


def set_enabled_flag():
    """Set the enabled flag based on the current Karabiner configuration."""
    config_data = load_karabiner_config()
    selected_profile = get_selected_profile(config_data)

    rules = selected_profile.get('complex_modifications', {}).get('rules', [])
    rule = find_rule_by_description(rules, RULE_DESCRIPTION)

    if rule:
        config.enabled_flag = rule.get('enabled', True)
    else:
        print(f"Rule '{RULE_DESCRIPTION}' not found in the selected profile.")
        config.enabled_flag = True


def write_enabled_flag():
    """Write the enabled flag back to the Karabiner configuration."""
    config_data = load_karabiner_config()
    selected_profile = get_selected_profile(config_data)

    complex_mods = selected_profile.setdefault('complex_modifications', {})
    rules = complex_mods.setdefault('rules', [])

    rule = find_rule_by_description(rules, RULE_DESCRIPTION)

    if rule:
        if config.enabled_flag:
            rule.pop('enabled', None)  # Enabled is default
        else:
            rule['enabled'] = False
        print(f"'enabled' flag for rule '{RULE_DESCRIPTION}' has been updated to {config.enabled_flag}.")
    else:
        print(f"Rule '{RULE_DESCRIPTION}' not found. No changes were made.")

    save_karabiner_config(config_data)


def merge_into_karabiner_config():
    """Merge the generated rule into the Karabiner configuration file."""
    yaml_data = YAML_Config().data
    new_rule = yaml_to_karabiner(yaml_data)

    config_data = load_karabiner_config()
    selected_profile = get_selected_profile(config_data)

    complex_mods = selected_profile.setdefault('complex_modifications', {})
    rules = complex_mods.setdefault('rules', [])

    existing_rule = find_rule_by_description(rules, new_rule['description'])

    if existing_rule:
        index = rules.index(existing_rule)
        rules[index] = new_rule
        print(f"Rule '{new_rule['description']}' has been updated in the selected profile.")
    else:
        rules.append(new_rule)
        print(f"Rule '{new_rule['description']}' has been added to the selected profile.")

    save_karabiner_config(config_data)
