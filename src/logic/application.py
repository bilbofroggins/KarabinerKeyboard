import subprocess

from src.logic.bundle import Bundle


class Application:
    def __init__(self, path):
        self.path = path
        self.name = path.split('/')[-1].replace('.app', '')
        self.bundle_obj: Bundle = None

    def bundle(self):
        if self.bundle_obj:
            return self.bundle_obj

        try:
            cmd = ['defaults', 'read', f'{self.path}/Contents/Info', 'CFBundleIdentifier']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.bundle_obj = Bundle(python_string=result.stdout.strip())
        except:
            self.bundle_obj = None

        return self.bundle_obj