import argparse
import os
import subprocess
import sys
import threading
import logging

from utils.constants import const

from tkinter import Tk, messagebox

from pkmn.gen_1 import gen_one_object
from pkmn.gen_2 import gen_two_object
from pkmn.gen_3 import gen_three_object
from pkmn import gen_factory

from utils.config_manager import config
from utils import auto_update

logger = logging.getLogger(__name__)



def route_startup_check_for_upgrade(main_app:Tk):
    new_app_version, new_asset_url = auto_update.get_new_version_info()
    logger.info(f"Latest version determined to be: {new_app_version}")

    if not auto_update.is_upgrade_needed(new_app_version, const.APP_VERSION):
        logger.info(f"No upgrade needed")
        return False
    
    if not auto_update.is_upgrade_possible():
        logger.info(f"Cannot upgrade this deployment")
        return False
    
    if not messagebox.askyesno("Update?", f"Found new version {new_app_version}\nDo you want to update?"):
        logger.info(f"User rejected auto-update")
        return False
    
    logger.info(f"User requested auto-update")
    main_app.event_generate(const.FORCE_QUIT_EVENT)
    return True


def init_base_generations():
    gen_factory._gen_factory.register_gen(gen_one_object.gen_one_red, const.RED_VERSION)
    gen_factory._gen_factory.register_gen(gen_one_object.gen_one_blue, const.BLUE_VERSION)
    gen_factory._gen_factory.register_gen(gen_one_object.gen_one_yellow, const.YELLOW_VERSION)

    gen_factory._gen_factory.register_gen(gen_two_object.gen_two_gold, const.GOLD_VERSION)
    gen_factory._gen_factory.register_gen(gen_two_object.gen_two_silver, const.SILVER_VERSION)
    gen_factory._gen_factory.register_gen(gen_two_object.gen_two_crystal, const.CRYSTAL_VERSION)

    gen_factory._gen_factory.register_gen(gen_three_object.gen_three_ruby, const.RUBY_VERSION)
    gen_factory._gen_factory.register_gen(gen_three_object.gen_three_sapphire, const.SAPPHIRE_VERSION)
    gen_factory._gen_factory.register_gen(gen_three_object.gen_three_emerald, const.EMERALD_VERSION)
    gen_factory._gen_factory.register_gen(gen_three_object.gen_three_fire_red, const.FIRE_RED_VERSION)
    gen_factory._gen_factory.register_gen(gen_three_object.gen_three_leaf_green, const.LEAF_GREEN_VERSION)

    gen_factory.change_version(const.YELLOW_VERSION)