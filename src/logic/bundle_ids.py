import subprocess
from collections import defaultdict

from src.logic.application import Application


class BundleIds:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls.get_applications(cls._instance)
        return cls._instance

    def fuzzy_search(self, search_term):
        if not search_term:
            return []
        # Limit the search to entries that start with the same letter as the search term
        first_letter = search_term[0].lower()
        candidates = self.apps_index.get(first_letter, [])
        # Perform a case-insensitive match on the reduced candidate list
        return [app for app in candidates if search_term.lower() in app.name.lower()]

    def get_applications(self):
        cmd = ['mdfind', "kMDItemContentType == 'com.apple.application-bundle'"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # Splitting the result by lines and extracting the last part of the path
        app_names = {path.split('/')[-1].replace('.app', ''): Application(path) for path in
                     result.stdout.strip().split('\n')}
        # Build an index by the first letter of each app name
        self.apps_index = defaultdict(list)
        for name, app in app_names.items():
            if name:
                self.apps_index[name[0].lower()].append(app)

        return