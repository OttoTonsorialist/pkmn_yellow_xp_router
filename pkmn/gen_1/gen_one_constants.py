import os

from utils.constants import const

class GenOneConstants:
    def __init__(self):
        self.GEN_ONE_DATA_PATH = os.path.join(const.POKEMON_RAW_DATA, "gen_one")
        self.ITEM_DB_PATH = os.path.join(self.GEN_ONE_DATA_PATH, const.ITEM_DB_FILE_NAME)
        self.MOVE_DB_PATH = os.path.join(self.GEN_ONE_DATA_PATH, const.MOVE_DB_FILE_NAME)
        self.TYPE_INFO_PATH = os.path.join(self.GEN_ONE_DATA_PATH, const.TYPE_INFO_FILE_NAME)
        self.FIGHTS_INFO_PATH = os.path.join(self.GEN_ONE_DATA_PATH, const.FIGHTS_INFO_FILE_NAME)

        self.YELLOW_ASSETS_PATH = os.path.join(self.GEN_ONE_DATA_PATH, "yellow")
        self.YELLOW_POKEMON_DB_PATH = os.path.join(self.YELLOW_ASSETS_PATH, const.POKEMON_DB_FILE_NAME)
        self.YELLOW_TRAINER_DB_PATH = os.path.join(self.YELLOW_ASSETS_PATH, const.TRAINERS_DB_FILE_NAME)
        self.YELLOW_MIN_BATTLES_DIR = os.path.join(self.YELLOW_ASSETS_PATH, "min_battles")

        self.RB_ASSETS_PATH = os.path.join(self.GEN_ONE_DATA_PATH, "red_blue")
        self.RB_POKEMON_DB_PATH = os.path.join(self.RB_ASSETS_PATH, const.POKEMON_DB_FILE_NAME)
        self.RB_TRAINER_DB_PATH = os.path.join(self.RB_ASSETS_PATH, const.TRAINERS_DB_FILE_NAME)
        self.RB_MIN_BATTLES_DIR = os.path.join(self.RB_ASSETS_PATH, "min_battles")

        # ok, actual consts
        self.BOULDER_BADGE = "boulder"
        self.CASCADE_BADGE = "cascade"
        self.THUNDER_BADGE = "thunder"
        self.RAINDBOW_BADGE = "rainbow"
        self.SOUL_BADGE = "soul"
        self.MARSH_BADGE = "marsh"
        self.VOLCANO_BADGE = "volcano"
        self.EARTH_BADGE = "earth"

        self.BAG_LIMIT = 20


gen_one_const = GenOneConstants()
