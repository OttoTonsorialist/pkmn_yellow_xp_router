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
    args = parser.parse_args()
    if args.debug:
        const.DEBUG_MODE = True

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
        logger.info(f"gottem: {flag_to_auto_update}")

    if flag_to_auto_update:
        logger.info(f"cleaning up")
        auto_update.auto_cleanup_old_version()
        logger.info(f"creating temp gui")
        app_upgrade = AutoUpgradeGUI()
        app_upgrade.mainloop()

        logger.info(f"About to restart: {sys.argv}")
        if os.path.splitext(sys.argv[0])[1] == ".pyw":
            subprocess.Popen([sys.executable] + sys.argv, start_new_session=True)
        else:
            subprocess.Popen(sys.argv, start_new_session=True)
