import argparse
import os
import concurrent.futures
from threading import Thread
import logging
from typing import Tuple

from controllers.main_controller import MainController
from controllers.battle_summary_controller import BattleSummaryController
from route_recording.recorder import RecorderController
from gui.main_window import MainWindow
from webserver import router_server

from utils.constants import const
from utils.config_manager import config
from utils import setup, custom_logging

logger = logging.getLogger(__name__)


def make_controllers(headless) -> Tuple[MainController, BattleSummaryController, RecorderController]:
    custom_logging.config_logging(const.GLOBAL_CONFIG_DIR)

    if not os.path.exists(config.get_user_data_dir()):
        os.makedirs(config.get_user_data_dir())

    setup.init_base_generations()
    controller = MainController(headless=headless)
    battle_controller = BattleSummaryController(controller)
    recorder_controller = RecorderController(controller)
    controller.sync_register_record_mode_change(recorder_controller.on_recording_mode_changed)

    return controller, battle_controller, recorder_controller


def run(
    controller:MainController,
    battle_controller:BattleSummaryController,
    recorder_controller:RecorderController,
    port:int,
    headless:bool
):

    if headless:
        router_server.spawn_server(
            controller,
            battle_controller,
            recorder_controller,
            port,
        )
    else:
        MainWindow(
            controller,
            battle_controller,
            recorder_controller,
            #f"http://127.0.0.1:{port}/shutdown"
        ).run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--gui", action="store_true")
    parser.add_argument("--port", "-p", type=int, default=5000)
    args = parser.parse_args()
    const.DEBUG_MODE = args.debug

    controllers = make_controllers(headless=(not args.gui))
    run(
        *controllers,
        args.port,
        not args.gui,
    )
