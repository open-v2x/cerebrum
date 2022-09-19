from config import devel as cfg
from common.app import App


if __name__ == "__main__":
    app = App(cfg)
    app.run()
