<h1 align="center">An alternate UI for Karabiner-Elements</h1>

<p align="center">
  <img style="display:block;margin: auto;" src="https://github.com/bilbofroggins/KarabinerKeyboard/assets/82745308/cc8b1bbd-add8-4240-abd5-4905a68f3550" width="700"/>
</p>

## Overview
Karabiner Keyboard is a user interface designed to simplify the customization of keyboard configurations using [Karabiner-Elements](https://github.com/pqrs-org/Karabiner-Elements). It eliminates the need to manually edit JSON files by providing a friendly UI for reading and writing configurations directly to the Karabiner-Elements JSON file. This tool is essential for users seeking an easier way to adjust their keyboard settings without diving into complex file structures.

## Instructions
From the Keyboard panel, press the keys you want to change. This will trigger a search to check anything containing the keys you've pressed. Once the keys turn gold, you can take your fingers off the keys as it has locked them in. You can then click the one of the sides of the binding to rebind, or the "x" to delete the modification.

The Overrides panel is very similar, but just shows a larger view of all the overrides you have set.

### WARNING! Early Development -- Current Limitations
- **Backup and Recovery**: Automatically backs up the `karabiner.json` file on the first modification, allowing easy reversion if needed.
- **Features not supported yet**: Does not support profiles, devices, app-specific settings, shell commands, sticky keys, or mouse support.
- **Complex Modifications**: Converts all simple modifications in Karabiner-Elements to complex modifications; original names are overwritten.
- **Number of modifications**: There is no scroll bar at the moment so it's hard to see every modification - searching is necessary.
- **Language**: Limited to English language configurations.
- **Macros**: Only supports a single "to" field for key mappings, affecting the ability to create macros (e.g., mapping `alt-d` to the string "diapers").

## Prerequisites
Before using Better Keyboard UI, ensure that [Karabiner-Elements](https://github.com/pqrs-org/Karabiner-Elements) is installed on your machine.

### Backup and Recovery
The application automatically creates a backup of the `karabiner.json` file upon making the first change. In case of any issues, users can revert to the original configuration through the help panel.

For the latest release and installation instructions, please check the [Releases](https://github.com/bilbofroggins/KarabinerKeyboard/releases) section of this repository.

## Contributing

### Running the app
```
pip3 install poetry
poetry shell
python3 src/main.py
```

### Building for distribution
```
pip3 install poetry
poetry shell
poetry install
poetry run bundle-app
```
