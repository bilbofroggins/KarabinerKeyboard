import subprocess

def add_bundle_to_spec(spec_file_path, bundle_section):
    # Read the existing content of the .spec file
    with open(spec_file_path, 'r') as file:
        lines = file.readlines()

    # Check if the BUNDLE section already exists
    if any('BUNDLE(' in line for line in lines):
        print("BUNDLE section already exists in the .spec file.")
        return

    # Append the BUNDLE section to the file
    with open(spec_file_path, 'a') as file:
        file.write("\n" + bundle_section)
        print("BUNDLE section added to the .spec file.")

def bundle_app():
    subprocess.run([
        "pyinstaller",
        "src/main.py",
        "--collect-submodules", "application",
        "--onefile",
        "--name", "KarabinerKeyboard"
    ])

    spec_file = 'KarabinerKeyboard.spec'
    # BUNDLE section to add
    bundle_section = """
app = BUNDLE(exe,
    name='KarabinerKeyboard.app',
    icon='images/icon.icns',
    bundle_identifier='com.patcunniff.karabinerkeyboard')
    """

    # Run the function
    add_bundle_to_spec(spec_file, bundle_section)

    # Run PyInstaller
    subprocess.run(["pyinstaller", spec_file])