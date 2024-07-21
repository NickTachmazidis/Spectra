"""Main file of the Spectra app."""

import sys

import hydra
from hydra.core.config_store import ConfigStore

from PyQt5 import QtWidgets

from src.classes.config import Config
from src.gui.main_window import QtMain

cs = ConfigStore.instance()
# Registering the Config class.
cs.store(name="spectra_config", node=Config)


@hydra.main(version_base=None, config_path="src/conf", config_name="config")
def main(cfg: Config) -> None:
    """Main function of the Spectra app that executes the program."""
    # Load the program
    app = QtWidgets.QApplication(sys.argv)
    window = QtMain(settings=cfg)
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
