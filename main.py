# Core
import sys
# GUI
from PyQt5 import QtWidgets
# Configurations
import hydra
from hydra.core.config_store import ConfigStore
# src
from src.config import Config
from src.gui.main_window import Main

cs = ConfigStore.instance()
# Registering the Config class.
cs.store(name="spectra_config", node=Config)

@hydra.main(version_base=None, config_path='src/conf', config_name="config")
def main(cfg: Config) -> None:
    # Load the program
    app = QtWidgets.QApplication(sys.argv)
    window = Main(settings=cfg)
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()