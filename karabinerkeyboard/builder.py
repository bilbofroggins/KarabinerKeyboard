import re
import subprocess

def modify_bundle_spec(spec_file, icon_path, bundle_id):
    with open(spec_file, 'r') as file:
        content = file.read()

    # Regular expression pattern to match the BUNDLE section
    pattern = r"(app\s*=\s*BUNDLE\([^)]*name\s*=\s*['\"]KarabinerKeyboard.app['\"][^)]*\))"

    # Replacement string with the new icon and bundle_identifier
    replacement = f"app = BUNDLE(\n    coll,\n    name='KarabinerKeyboard.app',\n    icon='{icon_path}',\n    bundle_identifier='{bundle_id}'\n)"

    # Replace the matched text with the new BUNDLE section
    modified_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open(spec_file, 'w') as file:
        file.write(modified_content)

def bundle_app():
    subprocess.run([
        "pyinstaller",
        "src/main.py",
        "--collect-submodules", "application",
        "--windowed",
        "--onedir",
        "--name", "KarabinerKeyboard",
        "--add-data", "src/versions/update.sh:Scripts"
    ])

    spec_file = 'KarabinerKeyboard.spec'
    icon_path = 'images/icon.icns'
    bundle_identifier = 'com.patcunniff.karabinerkeyboard'
    modify_bundle_spec(spec_file, icon_path, bundle_identifier)

    # Run PyInstaller
    subprocess.run(["pyinstaller", spec_file])