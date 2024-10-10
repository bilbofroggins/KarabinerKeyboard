import warnings

from src.logic.yaml_config import YAML_Config
from window import MyApp

def main():
    warnings.simplefilter('always', DeprecationWarning)
    YAML_Config()
    app = MyApp()
    app.run()

if __name__ == '__main__':
    main()
