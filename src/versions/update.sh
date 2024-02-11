#!/bin/bash

app_directory="$1"

# Wait for the application to exit, ignoring grep & update script
while ps aux | grep '[K]arabinerKeyboard' | grep -v 'update.sh' | grep -v grep > /dev/null; do sleep 1; done

# Remove the old version
rm -rf "$app_directory/KarabinerKeyboard.app"

# Move the new version into place
mv /tmp/KarabinerKeyboard.app "$app_directory"

# Restart the application
open "$app_directory/KarabinerKeyboard.app"
