import os
import subprocess
import sys
from pathlib import Path

import requests

from src.versions.version_compare import Version
from src.versions.version import __version__

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
        done_flag[0] = True
        return False

    zip_file_path = '/tmp/KarabinerKeyboard.zip'
    extract_to_path = '/tmp'

    download_update(f"https://github.com/{repo}/releases/download/{new_version}/KarabinerKeyboard.zip", zip_file_path)
    os.system("unzip -q -o %s -d %s" % (zip_file_path, extract_to_path))

    # Running in a PyInstaller bundle
    base_path = Path(sys.executable).parent.parent  # Reach the Contents directory
    script_path = str(base_path / 'Resources' / 'Scripts' / 'update.sh')
    app_directory = str(base_path.parent.parent)

    subprocess.run(["chmod", "+x", script_path])

    # Execute the script and exit the application
    subprocess.Popen(["/bin/bash", script_path, app_directory])
    done_flag[0] = True