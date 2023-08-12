import argparse
import os
import subprocess
import sys
import threading
import concurrent.futures
import logging

from controllers.main_controller import MainController
from gui.auto_upgrade_window import AutoUpgradeGUI
from gui.main_window import MainWindow

from utils.constants import const
from utils.config_manager import config
from utils import auto_update, setup, custom_logging

logger = logging.getLogger(__name__)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--debug_recorder", action="store_true")
    args = parser.parse_args()
    const.DEBUG_MODE = args.debug
    const.DEBUG_RECORDING_MODE = args.debug_recorder or args.debug

    custom_logging.config_logging(const.GLOBAL_CONFIG_DIR)

    if not os.path.exists(config.get_user_data_dir()):
        os.makedirs(config.get_user_data_dir())
    
    setup.init_base_generations()
    controller = MainController()
    app = MainWindow(controller)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        background_thread = executor.submit(setup.route_startup_check_for_upgrade, app)

        app.run()
        flag_to_auto_update = background_thread.result()
        logger.info(f"App closed, autoupdate requested? {flag_to_auto_update}")

    if flag_to_auto_update:
        logger.info(f"Beginning cleanup of old version")
        auto_update.auto_cleanup_old_version()
        logger.info(f"Launching temp gui for AutoUpgrade")
        app_upgrade = AutoUpgradeGUI()
        app_upgrade.mainloop()

        logger.info(f"About to restart: {sys.argv}")
        if os.path.splitext(sys.argv[0])[1] == ".pyw":
            subprocess.Popen([sys.executable] + sys.argv, start_new_session=True)
        else:
            subprocess.Popen(sys.argv, start_new_session=True)
