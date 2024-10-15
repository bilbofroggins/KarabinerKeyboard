import warnings

from src.logic.merge_kb_config import set_enabled_flag
from src.logic.yaml_config import YAML_Config
from window import MyApp

def main():
    warnings.simplefilter('always', DeprecationWarning)
    YAML_Config()
    set_enabled_flag()
    app = MyApp()
    app.run()

if __name__ == '__main__':
    main()
