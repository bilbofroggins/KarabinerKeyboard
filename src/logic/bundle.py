class Bundle:
    def __init__(self, *, json_string='', python_string=''):
        self.pystring = ''
        if len(json_string):
            self.pystring = self.json_to_py(json_string)
        else:
            self.pystring = python_string

    def to_json(self):
        return self.py_to_json(self.pystring)

    def json_to_py(self, input_string):
        return input_string.strip("^$").replace("\\.", ".")

    def py_to_json(self, input_string):
        return ("^" + input_string + "$").replace(".", "\\.")
