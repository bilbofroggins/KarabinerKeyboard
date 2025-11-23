<h1 align="center">An alternate UI for Karabiner-Elements</h1>

<p align="center">
<img width="1295" alt="app-screenshot" src="https://github.com/user-attachments/assets/7838564a-f1f9-4229-be51-3ceda3b2dff8">
</p>

## Overview
Karabiner Keyboard is a user interface designed to simplify the customization of keyboard configurations using [Karabiner-Elements](https://github.com/pqrs-org/Karabiner-Elements). It eliminates the need to manually edit JSON files by providing a friendly UI for writing configurations directly to the Karabiner-Elements JSON file. This tool took inspiration from qmk, where users can adjust their keyboard settings through layers without diving into complex key overrides.

## Instructions
For the latest release, please check the [Releases](https://github.com/bilbofroggins/KarabinerKeyboard/releases) section of this repository. Download & extract the zip file. The app stores a yaml file behind the scenes within ~/.config/karabiner_keyboard that gets translated into a karabiner config rule called "KBKeyboard" underneath complex modifications.

From the Keyboard panel, press the keys you want to change, or click on the key. You can configure keys using several types:

**Keybinding**: Override the key with a single sequence or an array of "to" sequences.

**Layer**: Create keyboard layers with different activation modes:
* Layer|MO = Momentary (layer activates while holding the key, resets when released)
* Layer|LT = Layer with Tap (momentary layer, but taps the key if no layer keys were pressed)
* Layer|TO = Toggle (one tap toggles the layer on; use another key to toggle back)

**Shell**: Execute shell commands when a key is pressed.

**Conditional**: Use variables to create dynamic behavior:
* **Get mode**: Make a key only activate when a variable is true (adds an `if` condition)
* **Toggle mode**: Make a key toggle a variable between true/false

Variables allow you to create modes (like vim mode, gaming mode, etc.) where certain keys only work when that mode is active, and other keys toggle the modes on/off.

Then click "Merge to config" in the top right to merge it to the Karabiner-Elements config file, and you should be good to go!

**Note**: Configuration and logs are stored in `~/.config/karabiner_keyboard/` (including `errors.log` and `update.log`).

### Limitations
English only hardcoded default keyboard at the moment
Some assumptions are made
* Most key overrides are set to "repeat": false
* Most key overrides have all mod keys as optional
* You will not jump back up layers when using MO type. For example, having a "MO to layer 1" key set on layer 4

## Prerequisites
Before using Better Keyboard UI, ensure that [Karabiner-Elements](https://github.com/pqrs-org/Karabiner-Elements) is installed on your machine.

## Contributing

### Prerequisites for Development
First, install [uv](https://github.com/astral-sh/uv) if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Development - Running the app
```bash
export PYTHONPATH=.
uv sync
uv run python src/main.py
```

### Building for distribution
```bash
uv sync --all-extras  # Installs dev dependencies including pyinstaller
uv run bundle-app
```

The app will be built to `dist/KarabinerKeyboard.app` and can be run locally.

**For public distribution (optional):** To notarize the app for macOS Gatekeeper, create a `.env` file in the project root with your Apple Developer credentials:
```
APPLE_ID=your-apple-id@example.com
APPLE_TEAM_ID=your-team-id
KK_APP_SPECIFIC_PASSWORD=your-app-specific-password
```

