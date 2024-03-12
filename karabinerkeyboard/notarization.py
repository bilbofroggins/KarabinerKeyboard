import os
import subprocess
import time
import json

def run_command(command):
    process = subprocess.run(command, shell=True, text=True, capture_output=True)
    if process.returncode != 0:
        print(f"Error running command: {command}\n{process.stderr}")
        exit(process.returncode)
    return process.stdout

def notarize_app(apple_id, team_id, app_path, zip_name):
    app_specific_password = os.environ.get("KK_APP_SPECIFIC_PASSWORD")
    if not app_specific_password:
        print("App-specific password not found in environment variables. Cannot notarize, but app has been created in ./dist")
        return

    # Sign the app
    sign_command = f'codesign --deep --force --verbose --sign "Developer ID Application: Patrick Cunniff (GD76CFHAZT)" {app_path} --options=runtime'
    print(run_command(sign_command))

    # Zip the app
    zip_command = f'ditto -c -k --keepParent {app_path} {zip_name}'
    print(run_command(zip_command))

    # Submit for notarization
    submit_command = f'xcrun notarytool submit --apple-id "{apple_id}" --team-id "{team_id}" --password "{app_specific_password}" {zip_name} --wait'
    submit_output = run_command(submit_command)
    try:
        submission_info = json.loads(submit_output)
        request_id = submission_info.get("id")
    except (json.JSONDecodeError, KeyError):
        print("Failed to parse notarization submission response.")
        return

    # Check notarization status in a loop
    while True:
        info_command = f'xcrun notarytool info {request_id} --apple-id "{apple_id}" --team-id "{team_id}" --password "{app_specific_password}"'
        info_output = run_command(info_command)
        try:
            info_status = json.loads(info_output)
            if info_status.get("status") == "Accepted":
                print("Notarization succeeded.")
                break
            elif info_status.get("status") == "Invalid":
                print("Notarization failed.")
                print(info_output)
                return
        except (json.JSONDecodeError, KeyError):
            print("Failed to parse notarization info response.")

        print("Waiting for notarization to complete...")
        time.sleep(60)  # Wait for a minute before checking again

    # Staple the app
    staple_command = f'xcrun stapler staple {app_path}'
    print(run_command(staple_command))
