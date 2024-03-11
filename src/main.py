from src.logic.karabiner_config import KarabinerConfig
from window import MyApp

def main():
    KarabinerConfig()
    app = MyApp()
    app.run()

if __name__ == '__main__':
    main()
