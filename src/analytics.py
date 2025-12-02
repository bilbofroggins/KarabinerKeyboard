"""
Anonymous telemetry for KarabinerKeyboard.

Collects basic usage statistics to help improve the application.
- Anonymous ID is randomly generated, not tied to hardware
- No personal information is collected
- Telemetry fails silently and never impacts app functionality
"""

import hashlib
import json
import os
import platform
import threading
import uuid

import requests

from src.versions.version import __version__
from src.config import config


ANALYTICS_ID_FILE = os.path.expanduser('~/.config/karabiner_keyboard/.analytics_id')


def get_anonymous_id():
    """Get or create a persistent anonymous ID."""
    try:
        if os.path.exists(ANALYTICS_ID_FILE):
            with open(ANALYTICS_ID_FILE, 'r') as f:
                return f.read().strip()
        
        # Generate new ID (hash of random UUID - not tied to hardware)
        anon_id = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:16]
        os.makedirs(os.path.dirname(ANALYTICS_ID_FILE), exist_ok=True)
        with open(ANALYTICS_ID_FILE, 'w') as f:
            f.write(anon_id)
        return anon_id
    except Exception:
        return "unknown"


def get_system_info():
    """Get system information for telemetry."""
    return {
        "architecture": platform.machine(),
        "macos_version": platform.mac_ver()[0],
        "app_version": __version__
    }


def _send_telemetry(event_name):
    """Internal function to send telemetry (runs in background thread)."""
    try:
        if not config.telemetry_url:
            return
            
        data = {
            "anonymous_id": get_anonymous_id(),
            "event": event_name,
            **get_system_info()
        }
        # Use data= instead of json= to avoid Content-Type: application/json
        # which Google Apps Script doesn't handle well
        requests.post(config.telemetry_url, data=json.dumps(data), timeout=5)
    except Exception:
        pass  # Fail silently - telemetry should never break the app


def track_event(event_name):
    """
    Send telemetry event (non-blocking, fails silently).
    
    Events:
    - app_launch: App was started
    - update_check: User checked for updates
    - update_started: Update download began
    - update_completed: Update was successfully applied
    """
    # Run in background thread to avoid blocking the app
    thread = threading.Thread(target=_send_telemetry, args=(event_name,), daemon=True)
    thread.start()

