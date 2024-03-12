import subprocess
import os

def run_command(command):
    """
    Executes a command and prints output in real-time.
    Returns the command output as a string.
    """
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True)
    output_lines = []
    while True:
        output_line = process.stdout.readline()
        if not output_line and process.poll() is not None:
            break
        if output_line:
            print(output_line.strip())
            output_lines.append(output_line.strip())
    return '\n'.join(output_lines)

def notarize_app(apple_id, team_id, app_path, zip_name):
    app_specific_password = os.getenv("KK_APP_SPECIFIC_PASSWORD")
    if not app_specific_password:
        print("App-specific password not found in environment variables but app built successfully")
        return

    # Sign the app
    sign_command = f'codesign --deep --force --verbose --sign "Developer ID Application: Patrick Cunniff (GD76CFHAZT)" "{app_path}" --options=runtime'
    run_command(sign_command)

    # Zip the app
    zip_command = f'ditto -c -k --keepParent "{app_path}" "{zip_name}"'
    run_command(zip_command)

    # Submit for notarization
    submit_command = f'xcrun notarytool submit "{zip_name}" --apple-id "{apple_id}" --team-id "{team_id}" --password "{app_specific_password}" --wait'
    submit_output = run_command(submit_command)

    # Check if "Accepted" is in the output of the submit_command
    if "Accepted" in submit_output:
        print("Notarization Accepted.")
        # Staple the app
        staple_command = f'xcrun stapler staple "{app_path}"'
        run_command(staple_command)
    else:
        print("Notarization may not be accepted, please check the output above for details.")

    # Remove the zipped file
    try:
        os.remove(zip_name)
        print(f"Removed zipped file: {zip_name}")
    except OSError as e:
        print(f"Error removing zipped file {zip_name}: {e}")