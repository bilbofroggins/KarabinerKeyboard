import os
import re
import shutil
import subprocess

from karabinerkeyboard.notarization import notarize_app


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

def update_version_number():
    filename = 'src/versions/version.py'

    with open(filename, 'r') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            if line.startswith('__version__'):
                version_line_index = i
                version_string = line.split('=')[1].strip().strip("'").strip('"')
                break

    version_parts = version_string.split('.')
    version_parts[-1] = str(
        int(version_parts[-1]) + 1)
    updated_version_string = '.'.join(version_parts)

    updated_version_line = f"__version__ = '{updated_version_string}'\n"

    lines[version_line_index] = updated_version_line
    with open(filename, 'w') as file:
        file.writelines(lines)

    print(f"Version updated to: {updated_version_string}")

def load_env_variables_from_file(env_file_path):
    try:
        with open(env_file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    except FileNotFoundError:
        print(f"Error: The file {env_file_path} was not found.")
    except Exception as e:
        print(f"An error occurred while reading {env_file_path}: {e}")


def bundle_app():
    # Remove old build files
    try:
        shutil.rmtree('build')
        shutil.rmtree('dist')
    except OSError as e:
        print(f"Error removing build dirs")

    load_env_variables_from_file('.env')
    update_version_number()

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

    notarize_app("pjcfifa@gmail.com", "GD76CFHAZT", "dist/KarabinerKeyboard.app", "KarabinerKeyboard.zip")
