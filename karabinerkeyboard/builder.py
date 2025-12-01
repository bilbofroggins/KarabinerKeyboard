import argparse
import os
import platform
import re
import shutil
import subprocess
import sys

from karabinerkeyboard.notarization import notarize_app


def modify_bundle_spec(spec_file, icon_path, bundle_id):
    with open(spec_file, 'r') as file:
        content = file.read()

    # Regular expression pattern to match the BUNDLE section
    pattern = r"(app\s*=\s*BUNDLE\([^)]*name\s*=\s*['\"]KarabinerKeyboard.app['\"][^)]*\))"

    # Replacement string with the new icon and bundle_identifier
    replacement = f"app = BUNDLE(\n    coll,\n    name='KarabinerKeyboard.app',\n    icon='{icon_path}',\n    bundle_identifier='{bundle_id}'\n)"

    # Replace the matched text with the new BUNDLE section
    modified_content1 = re.sub(pattern, replacement, content, flags=re.DOTALL)


    # Check if 'datas' exists in Analysis
    additional_data = "('resources/*', 'resources')"
    datas_pattern = re.compile(r'(datas=\[.*?\])', re.DOTALL)
    datas_match = datas_pattern.search(modified_content1)

    modified_content = modified_content1  # Default to no changes
    
    if datas_match:
        # If 'datas' exists, append the additional_data if not already present
        datas_content = datas_match.group(1)
        if additional_data not in datas_content:
            new_datas_content = datas_content[:-1] + ", " + additional_data + "]"
            modified_content = modified_content1.replace(datas_content, new_datas_content)
    else:
        # If 'datas' does not exist, insert it after the first parenthesis of 'Analysis'
        analysis_pattern = re.compile(r'(Analysis\([^\)]*)', re.DOTALL)
        modified_content = analysis_pattern.sub(r'\1, datas=[' + additional_data + ']',
                                                modified_content1)

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


def get_current_arch():
    """Get the current machine architecture."""
    machine = platform.machine()
    if machine == 'x86_64':
        return 'x86_64'
    elif machine in ('arm64', 'aarch64'):
        return 'arm64'
    return machine


def setup_arch_venv(target_arch):
    """
    Set up a virtual environment for the target architecture.
    Returns the path to the Python executable in that venv.
    """
    current_arch = get_current_arch()
    
    # If building for current arch, use the current venv
    if target_arch == current_arch:
        return sys.executable
    
    # For cross-arch builds, we need a separate venv
    venv_name = f".venv-{target_arch}"
    venv_path = os.path.join(os.getcwd(), venv_name)
    python_path = os.path.join(venv_path, "bin", "python3")
    
    if not os.path.exists(venv_path):
        print(f"\n=== Creating {target_arch} virtual environment ===\n")
        
        if target_arch == 'x86_64' and current_arch == 'arm64':
            # Need to use Rosetta to create x86_64 venv
            # First check if x86_64 Python is available
            result = subprocess.run(
                ["arch", "-x86_64", "python3", "--version"],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                print("ERROR: Cannot find x86_64 Python.")
                print("To build for Intel Macs from Apple Silicon, you need to install Python for Intel:")
                print("")
                print("  Option 1 - Using pyenv:")
                print("    arch -x86_64 /bin/bash -c 'pyenv install 3.11'")
                print("")
                print("  Option 2 - Using Homebrew under Rosetta:")
                print("    arch -x86_64 /bin/bash -c 'eval \"$(/usr/local/bin/brew shellenv)\" && brew install python@3.11'")
                print("")
                print("  Option 3 - Download Intel Python installer from python.org")
                print("")
                sys.exit(1)
            
            # Create venv using x86_64 Python
            subprocess.run(
                ["arch", "-x86_64", "python3", "-m", "venv", venv_path],
                check=True
            )
        else:
            # For other cases, just create a regular venv
            subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)
        
        # Install dependencies in the new venv
        print(f"\n=== Installing dependencies in {target_arch} venv ===\n")
        pip_cmd = [python_path, "-m", "pip", "install", "-e", ".[dev]"]
        
        if target_arch == 'x86_64' and current_arch == 'arm64':
            subprocess.run(["arch", "-x86_64"] + pip_cmd, check=True)
        else:
            subprocess.run(pip_cmd, check=True)
    
    return python_path


def bundle_app():
    """Bundle app for current architecture (default behavior)."""
    parser = argparse.ArgumentParser(description='Build KarabinerKeyboard app')
    parser.add_argument('--arch', choices=['x86_64', 'arm64', 'current'], 
                        default='current',
                        help='Target architecture (x86_64 for Intel, arm64 for Apple Silicon, current for native)')
    parser.add_argument('--skip-version-bump', action='store_true',
                        help='Skip incrementing the version number')
    args = parser.parse_args()
    
    target_arch = args.arch
    if target_arch == 'current':
        target_arch = get_current_arch()
    
    print(f"\n=== Building for architecture: {target_arch} ===\n")
    
    # Get the correct Python for this architecture
    python_exe = setup_arch_venv(target_arch)
    current_arch = get_current_arch()
    use_rosetta = (target_arch == 'x86_64' and current_arch == 'arm64')
    
    # Remove old build files
    try:
        shutil.rmtree('build')
        shutil.rmtree('dist')
    except OSError:
        pass

    if not args.skip_version_bump:
        update_version_number()

    # Build with target architecture
    pyinstaller_cmd = [
        python_exe, "-m", "PyInstaller",
        "src/main.py",
        "--collect-submodules", "application",
        "--windowed",
        "--onedir",
        "--name", "KarabinerKeyboard",
        "--add-data", "src/versions/update.sh:Scripts",
        "--target-arch", target_arch,
        "-y",  # Overwrite output without confirmation
    ]
    
    if use_rosetta:
        pyinstaller_cmd = ["arch", "-x86_64"] + pyinstaller_cmd
    
    subprocess.run(pyinstaller_cmd)

    spec_file = 'KarabinerKeyboard.spec'
    icon_path = 'resources/icon.icns'
    bundle_identifier = 'com.patcunniff.karabinerkeyboard'
    modify_bundle_spec(spec_file, icon_path, bundle_identifier)
    
    # Also update target_arch in the spec file
    modify_spec_target_arch(spec_file, target_arch)

    # Run PyInstaller with spec file
    spec_cmd = [python_exe, "-m", "PyInstaller", "-y", spec_file]
    if use_rosetta:
        spec_cmd = ["arch", "-x86_64"] + spec_cmd
    result = subprocess.run(spec_cmd)
    
    # App path stays as KarabinerKeyboard.app, only the zip has arch suffix
    app_path = "dist/KarabinerKeyboard.app"
    arch_suffix = "intel" if target_arch == "x86_64" else "arm"
    temp_zip_name = "KarabinerKeyboard-notarize-temp.zip"
    # Final zip goes in project root for easy access
    final_zip_name = f"KarabinerKeyboard-{arch_suffix}.zip"
    
    # Only proceed with notarization if build was successful and .env exists
    if result.returncode == 0 and os.path.exists(app_path):
        print(f"\nBuild completed: {app_path}")
        
        if os.path.exists('.env'):
            print("\n=== Starting notarization process ===")
            load_env_variables_from_file('.env')

            # Read credentials from environment variables
            apple_id = os.getenv('APPLE_ID')
            team_id = os.getenv('APPLE_TEAM_ID')

            if not apple_id or not team_id:
                print("Warning: APPLE_ID or APPLE_TEAM_ID not found in .env file")
                print(f"Build completed successfully at: {app_path}")
            else:
                # Notarize (uses temp zip, deletes it after)
                notarize_app(apple_id, team_id, app_path, temp_zip_name)
                
                # Create final distribution zip with arch suffix in project root
                print(f"\n=== Creating distribution zip: {final_zip_name} ===")
                if os.path.exists(final_zip_name):
                    os.remove(final_zip_name)
                subprocess.run(["ditto", "-c", "-k", "--keepParent", app_path, final_zip_name], check=True)
                print(f"Distribution zip created: {final_zip_name}")
        else:
            print("\n=== Skipping notarization (no .env file found) ===")
            print(f"Build completed successfully at: {app_path}")
            # Still create the distribution zip in project root
            print(f"\n=== Creating distribution zip: {final_zip_name} ===")
            if os.path.exists(final_zip_name):
                os.remove(final_zip_name)
            subprocess.run(["ditto", "-c", "-k", "--keepParent", app_path, final_zip_name], check=True)
            print(f"Distribution zip created: {final_zip_name}")
            print("Note: App is not notarized. For distribution, create a .env file with Apple credentials and run again.")
    else:
        print("Build failed or app not found. Skipping notarization.")


def modify_spec_target_arch(spec_file, target_arch):
    """Update the target_arch in the spec file."""
    with open(spec_file, 'r') as file:
        content = file.read()
    
    # Update target_arch in EXE section
    content = re.sub(
        r'target_arch=None',
        f"target_arch='{target_arch}'",
        content
    )
    
    with open(spec_file, 'w') as file:
        file.write(content)
