from common.app import App
from config import devel as config


if __name__ == "__main__":
    app = App(config)
    app.run()
