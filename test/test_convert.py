import yaml
import json

# Function to convert YAML to Karabiner JSON with updated layer handling
def yaml_to_karabiner(yaml_data):
    karabiner_json = {
        "description": "KBKeyboard",
        "manipulators": []
    }

    # Extract layer numbers and determine the maximum layer
    layers = yaml_data['layers']
    layer_numbers = [int(layer) for layer in layers.keys()]
    max_layer = max(layer_numbers)

    # No need to initialize variables; they default to 0

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
                karabiner_json['manipulators'].append(manipulator)

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
                karabiner_json['manipulators'].append(manipulator)

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
                karabiner_json['manipulators'].append(manipulator)

            elif key_type == 'single':
                key_code = key_data.split(' + ')[-1]
                modifiers = key_data.split(' + ')[:-1] if ' + ' in key_data else []
                manipulator = {
                    "type": "basic",
                    "from": from_dict,
                    "to": [{"key_code": key_code, "modifiers": modifiers}],
                    "conditions": conditions
                }
                karabiner_json['manipulators'].append(manipulator)

            elif key_type == 'multi':
                to_sequence = [{"key_code": k} for k in key_data]
                manipulator = {
                    "type": "basic",
                    "from": from_dict,
                    "to": to_sequence,
                    "conditions": conditions
                }
                karabiner_json['manipulators'].append(manipulator)

            elif key_type == 'shell':
                manipulator = {
                    "type": "basic",
                    "from": from_dict,
                    "to": [{"shell_command": key_data}],
                    "conditions": conditions
                }
                karabiner_json['manipulators'].append(manipulator)

    return karabiner_json

# Example YAML input
yaml_input = """
layers:
  0:
    left_command:
      data: '1'
      type: layer|MO
    tab:
      data: '2'
      type: layer|LT
  1:
    left_option:
      data: '2'
      type: layer|MO
    j,k:
      data: left_alt + delete_or_backspace
      type: single
  2:
    f:
      data: k
      type: single
"""

# Load YAML input
yaml_data = yaml.safe_load(yaml_input)

# Convert YAML to Karabiner JSON
karabiner_output = yaml_to_karabiner(yaml_data)

# Print JSON output
print(json.dumps(karabiner_output, indent=4))