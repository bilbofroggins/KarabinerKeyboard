import json

json_str = '''
{
    "type": "basic",
    "from": "from event definition",
    "to": ["to event definition", "to event definition"],
    "to_if_alone": ["to event definition", "to event definition"],
                        "to_delayed_action": {
                        "to_if_invoked": [
                            "test", "test2"
                        ],
                        "to_if_canceled": [
                            "cats"
                        ]
                    }
}
'''

# Load the string into a Python dictionary
data = json.loads(json_str)

# Define the keys you want to exclude
keys_to_exclude = {'type', 'from', 'to'}

# Use a dictionary comprehension to create a new dictionary without the excluded keys
rest = {key: value for key, value in data.items() if key not in keys_to_exclude}

print(rest)