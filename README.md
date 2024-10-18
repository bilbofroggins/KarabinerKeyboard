<h1 align="center">An alternate UI for Karabiner-Elements</h1>

<p align="center">
<img width="1295" alt="app-screenshot" src="https://github.com/user-attachments/assets/7838564a-f1f9-4229-be51-3ceda3b2dff8">
</p>

## Overview
Karabiner Keyboard is a user interface designed to simplify the customization of keyboard configurations using [Karabiner-Elements](https://github.com/pqrs-org/Karabiner-Elements). It eliminates the need to manually edit JSON files by providing a friendly UI for writing configurations directly to the Karabiner-Elements JSON file. This tool took inspiration from qmk, where users can adjust their keyboard settings through layers without diving into complex key overrides.

## Instructions
For the latest release, please check the [Releases](https://github.com/bilbofroggins/KarabinerKeyboard/releases) section of this repository. Download & extract the zip file. The app stores a yaml file behind the scenes within ~/.config/karabiner_keyboard that gets translated into a karabiner config rule called "KBKeyboard" underneath complex modifications.

From the Keyboard panel, press the keys you want to change, or click on the key. You can currently either set to Keybinding, which will allow you to override the key with a single sequence or an array of "to" sequences. You can also pick the layer type, which has a few types to it:

Layer|MO = Momentary (layer will activate upon holding down the key and reset once released)
Layer|LT = Layer with Tap (similar to momentary except will trigger the key press if no keys within the layer were hit)
Layer|TO = Toggle (one tap toggles the layer on and you need a seperate key in the next layer to reset back)

### Limitations
English only hardcoded default keyboard at the moment
Shell commands not added yet
Some assumptions are made
* Most key overrides are set to "repeat": false
* Most key overrides have all mod keys as optional
* You will not jump back up layers when using MO type. For example, having a "MO to layer 1" key set on layer 4

## Prerequisites
Before using Better Keyboard UI, ensure that [Karabiner-Elements](https://github.com/pqrs-org/Karabiner-Elements) is installed on your machine.

## Contributing

### Development - Running the app
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
