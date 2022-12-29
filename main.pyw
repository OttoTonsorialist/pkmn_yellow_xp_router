import argparse
import os
import subprocess
import sys
import threading
import logging
import json

import tkinter as tk
from tkinter import filedialog
from tkinter import ttk, font, messagebox
from controllers.main_controller import MainController
from gui.auto_upgrade_window import AutoUpgradeGUI
from gui.main_window import MainWindow
from route_recording.recorder import RecorderController

from utils.constants import const
from utils.config_manager import config
from utils import auto_update, custom_logging


if not os.path.exists(const.GLOBAL_CONFIG_FILE) or not os.path.exists(const.GLOBAL_CONFIG_DIR):
    # First time setup. Just need to create a few folders
    # TODO: proper error handling...? Idk man
    os.makedirs(const.GLOBAL_CONFIG_DIR)
    if not os.path.exists(config.get_user_data_dir()):
        os.makedirs(config.get_user_data_dir())


custom_logging.config_logging(const.GLOBAL_CONFIG_DIR)
logger = logging.getLogger(__name__)
flag_to_auto_update = False


def startup_check_for_upgrade(main_app:MainWindow):
    new_app_version, new_asset_url = auto_update.get_new_version_info()
    logger.info(f"Latest version determined to be: {new_app_version}")

    # kinda dumb, but this should have enough delay that when restarting
    # the parent process should have died already, so we can properly clean it up
    auto_update.auto_cleanup_old_version()

    if not auto_update.is_upgrade_needed(new_app_version):
        logger.info(f"No upgrade needed")
        return
    
    if not messagebox.askyesno("Update?", f"Found new version {new_app_version}\nDo you want to update?"):
        logger.info(f"User rejected auto-update")
        return
    
    logger.info(f"User requested auto-update")
    global flag_to_auto_update
    flag_to_auto_update = True
    main_app.event_generate(const.FORCE_QUIT_EVENT)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    if args.debug:
        const.DEBUG_MODE = True
    
    app = MainWindow()
    background_thread = threading.Thread(target=startup_check_for_upgrade, args=(app,))

    background_thread.start()
    app.run()

    background_thread.join()

    if flag_to_auto_update:
        auto_update.auto_cleanup_old_version()
        app_upgrade = AutoUpgradeGUI()
        app_upgrade.mainloop()

        logger.info(f"About to restart: {sys.argv}")
        if os.path.splitext(sys.argv[0])[1] == ".pyw":
            subprocess.Popen([sys.executable] + sys.argv, start_new_session=True)
        else:
            subprocess.Popen(sys.argv, start_new_session=True)

    
