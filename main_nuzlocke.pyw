import os
import subprocess
import sys
import threading
import logging

from gui.auto_upgrade_window import AutoUpgradeGUI
from nuzlocke_gui.nuzlocke_controller import NuzlockeController
from nuzlocke_gui.nuzlocke_main_window import NuzlockeWindow

from utils.constants import const
from utils.config_manager import config
from utils import auto_update, custom_logging, setup

custom_logging.config_logging(const.GLOBAL_CONFIG_DIR)
logger = logging.getLogger(__name__)


if __name__ == '__main__':
    flag_to_auto_update = False
    if not os.path.exists(config.get_user_data_dir()):
        os.makedirs(config.get_user_data_dir())

    setup.init_base_generations()
    controller = NuzlockeController()
    app = NuzlockeWindow(controller)
    background_thread = threading.Thread(target=setup.nuzlocke_startup_check_for_upgrade, args=(app,))

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
