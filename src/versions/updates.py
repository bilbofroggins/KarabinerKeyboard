import os
import platform
import subprocess
import sys
from pathlib import Path
from datetime import datetime

import requests

from src.versions.version_compare import Version
from src.versions.version import __version__

# Update log file location
UPDATE_LOG_FILE = os.path.expanduser('~/.config/karabiner_keyboard/update.log')


def get_arch_suffix():
    """Get the architecture suffix for downloads (intel or arm)."""
    machine = platform.machine()
    if machine == 'x86_64':
        return 'intel'
    elif machine in ('arm64', 'aarch64'):
        return 'arm'
    return 'arm'  # Default to arm for unknown architectures on Mac

def log_update(message):
    """Write update messages to log file."""
    try:
        os.makedirs(os.path.dirname(UPDATE_LOG_FILE), exist_ok=True)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(UPDATE_LOG_FILE, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        # Fallback to console if logging fails
        print(f"[LOG ERROR] {e}: {message}")

repo = 'bilbofroggins/KarabinerKeyboard'

def get_latest_release_info(repo):
    """Fetches the latest release information from the specified GitHub repository."""
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        response = requests.get(url)
        # Check if the response was successful
        response.raise_for_status()
        return response.json()
    except Exception as err:
        print(f"An error occurred: {err}")
    return None

def get_releases_since_version(repo, since_version):
    """Fetches all releases since a specific version from the specified GitHub repository."""
    url = f"https://api.github.com/repos/{repo}/releases"
    response = requests.get(url)
    response.raise_for_status()
    releases = response.json()

    newer_releases = []
    for release in releases:
        if Version(release['tag_name']) > since_version:
            newer_releases.append(release)
        else:
            break  # Assuming releases are sorted from latest to oldest
    return newer_releases

def download_update(download_url, save_path):
    with requests.get(download_url, stream=True) as r:
        with open(save_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

latest_version = None
current_version = None
def check_up_to_date():
    global latest_version
    global current_version
    if latest_version is None:
        latest_release = get_latest_release_info(repo)
        latest_version = Version(latest_release['tag_name'])
        current_version = Version(__version__)

    if latest_version > current_version:
        return (False, str(latest_version))
    else:
        return (True, None)

def background_updates(new_version, done_flag):
    # Just give up in dev environment
    if not getattr(sys, 'frozen', False):
        log_update("Skipping update - running in development mode")
        done_flag[0] = True
        return False

    arch_suffix = get_arch_suffix()
    log_update(f"Starting update to version {new_version} for architecture: {arch_suffix}")

    zip_file_path = '/tmp/KarabinerKeyboard.zip'
    extract_to_path = '/tmp'
    
    # Architecture-specific zip file name
    arch_zip_name = f"KarabinerKeyboard-{arch_suffix}.zip"
    # Fallback to generic name for older releases
    generic_zip_name = "KarabinerKeyboard.zip"

    try:
        # Try architecture-specific download first, fall back to generic
        arch_url = f"https://github.com/{repo}/releases/download/{new_version}/{arch_zip_name}"
        generic_url = f"https://github.com/{repo}/releases/download/{new_version}/{generic_zip_name}"
        
        log_update(f"Attempting to download architecture-specific update: {arch_zip_name}")
        try:
            # Check if arch-specific file exists
            response = requests.head(arch_url, allow_redirects=True)
            if response.status_code == 200:
                download_url = arch_url
                log_update(f"Found architecture-specific release")
            else:
                log_update(f"Architecture-specific release not found, falling back to generic")
                download_url = generic_url
        except Exception:
            log_update(f"Error checking for arch-specific release, falling back to generic")
            download_url = generic_url
        
        log_update(f"Downloading update from: {download_url}")
        download_update(download_url, zip_file_path)
        log_update(f"Download completed: {zip_file_path}")

        # Unzip using subprocess for better error handling
        log_update("Extracting update...")
        result = subprocess.run(["unzip", "-q", "-o", zip_file_path, "-d", extract_to_path],
                               capture_output=True, text=True)
        if result.returncode != 0:
            log_update(f"ERROR: Unzip failed with code {result.returncode}: {result.stderr}")
            done_flag[0] = True
            return False
        log_update("Extraction completed")

        # The app inside the zip is always named KarabinerKeyboard.app
        final_app_path = '/tmp/KarabinerKeyboard.app'
        
        if not os.path.exists(final_app_path):
            log_update(f"ERROR: Downloaded app not found after extraction at {final_app_path}")
            done_flag[0] = True
            return False
        log_update(f"Verified extracted app exists at: {final_app_path}")

        # Running in a PyInstaller bundle
        base_path = Path(sys.executable).parent.parent  # Reach the Contents directory
        script_path = str(base_path / 'Resources' / 'Scripts' / 'update.sh')
        app_directory = str(base_path.parent.parent)

        # Verify script exists
        if not os.path.exists(script_path):
            log_update(f"ERROR: Update script not found at: {script_path}")
            done_flag[0] = True
            return False
        log_update(f"Found update script at: {script_path}")

        # Make script executable
        subprocess.run(["chmod", "+x", script_path], check=True)
        log_update("Made update script executable")

        # Execute the script and exit the application
        log_update(f"Launching update script for app at: {app_directory}")
        subprocess.Popen(["/bin/bash", script_path, app_directory])
        log_update("Update script launched successfully - application will restart")
        done_flag[0] = True
        return True

    except Exception as e:
        log_update(f"ERROR: Update failed with exception: {type(e).__name__}: {e}")
        done_flag[0] = True
        return False
