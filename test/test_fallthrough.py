import yaml


def is_key_overridden(yaml_file_path, key_to_check):
    """
    Check if a specific key is overridden in the YAML config file.
    If the key has a 'single' type, return the overridden key.

    :param yaml_file_path: The path to the YAML file
    :param key_to_check: The key to check for overrides (e.g., 'j')
    :return: The overridden key if type is 'single', otherwise None
    """
    # Load the YAML data from the file
    with open(yaml_file_path, 'r') as file:
        yaml_data = yaml.safe_load(file)

    layers = yaml_data.get('layers', {})

    # Loop through all layers and keys
    for layer_num, layer_data in layers.items():
        for key, value in layer_data.items():
            # Handle cases where multiple keys are specified (e.g., 'j,k')
            key_list = key.split(',')

            # Check if the specific key is present in the current key
            if key_to_check in key_list:
                if value['type'] == 'single':
                    return value['data']  # Return the overridden key for 'single' type
                else:
                    return "Something else"

    return None


# Example usage:
yaml_file = 'test_config.yaml'  # Path to your YAML input file
key_to_check = 'comma'  # Key to check for override

overridden_key = is_key_overridden(yaml_file, key_to_check)

if overridden_key:
    print(f"The key '{key_to_check}' is overridden with '{overridden_key}'")
else:
    print(f"The key '{key_to_check}' is not overridden.")