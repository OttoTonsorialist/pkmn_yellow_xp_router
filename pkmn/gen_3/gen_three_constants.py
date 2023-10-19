import os

from utils.constants import const

class GenThreeConstants:
    def __init__(self):
        self.GEN_THREE_DATA_PATH = os.path.join(const.POKEMON_RAW_DATA, "gen_three")
        self.ITEM_DB_PATH = os.path.join(self.GEN_THREE_DATA_PATH, const.ITEM_DB_FILE_NAME)
        self.MOVE_DB_PATH = os.path.join(self.GEN_THREE_DATA_PATH, const.MOVE_DB_FILE_NAME)
        self.TYPE_INFO_PATH = os.path.join(self.GEN_THREE_DATA_PATH, const.TYPE_INFO_FILE_NAME)
        self.FIGHTS_INFO_PATH = os.path.join(self.GEN_THREE_DATA_PATH, const.FIGHTS_INFO_FILE_NAME)

        self.RUBY_SAPPHIRE_POKEMON_PATH = os.path.join(self.GEN_THREE_DATA_PATH, "ruby_sapphire", const.POKEMON_DB_FILE_NAME)
        self.RUBY_TRAINER_DB_PATH = os.path.join(self.GEN_THREE_DATA_PATH, "ruby_sapphire", f"ruby_{const.TRAINERS_DB_FILE_NAME}")
        self.SAPPHIRE_TRAINER_DB_PATH = os.path.join(self.GEN_THREE_DATA_PATH, "ruby_sapphire", f"sapphire_{const.TRAINERS_DB_FILE_NAME}")
        self.EMERALD_POKEMON_PATH = os.path.join(self.GEN_THREE_DATA_PATH, "emerald", const.POKEMON_DB_FILE_NAME)
        self.EMERALD_TRAINER_DB_PATH = os.path.join(self.GEN_THREE_DATA_PATH, "emerald", const.TRAINERS_DB_FILE_NAME)
        self.FIRE_RED_LEAF_GREEN_POKEMON_PATH = os.path.join(self.GEN_THREE_DATA_PATH, "firered_leafgreen", const.POKEMON_DB_FILE_NAME)
        self.FIRE_RED_LEAF_GREEN_TRAINER_DB_PATH = os.path.join(self.GEN_THREE_DATA_PATH, "firered_leafgreen", const.TRAINERS_DB_FILE_NAME)

        self.STONE_BADGE = "stone"
        self.KNUCKLE_BADGE = "knuckle"
        self.DYNAMO_BADGE = "dynamo"
        self.HEAT_BADGE = "heat"
        self.BALANCE_BADGE = "balance"
        self.FEATHER_BADGE = "feather"
        self.MIND_BADGE = "mind"
        self.RAIN_BADGE = "rain"

        self.BOULDER_BADGE = "boulder"
        self.CASCADE_BADGE = "cascade"
        self.THUNDER_BADGE = "thunder"
        self.RAINDBOW_BADGE = "rainbow"
        self.SOUL_BADGE = "soul"
        self.MARSH_BADGE = "marsh"
        self.VOLCANO_BADGE = "volcano"
        self.EARTH_BADGE = "earth"

        self.MAROWAK_NAME = "Marowak"
        self.THICK_CLUB_NAME = "Thick Club"

        self.PIKACHU_NAME = "Pikachu"
        self.LIGHT_BALL_NAME = "Light Ball"

        self.DITTO_NAME = "Ditto"
        self.METAL_POWDER_NAME = "Metal Powder"

        self.NO_BONUS = "No Bonus"
        self.DIG_BONUS = "Dig Bonus"
        self.FLY_BONUS = "Fly Bonus"
        self.SWITCH_BONUS = "Switch Bonus"
        self.MINIMIZE_BONUS = "Minimize Bonus"

        self.MAGNITUDE_MOVE_NAME = "Magnitude"
        self.MAGNITUDE_4 = "Mag 4"
        self.MAGNITUDE_5 = "Mag 5"
        self.MAGNITUDE_6 = "Mag 6"
        self.MAGNITUDE_7 = "Mag 7"
        self.MAGNITUDE_8 = "Mag 8"
        self.MAGNITUDE_9 = "Mag 9"
        self.MAGNITUDE_10 = "Mag 10"

        self.FLAIL_FULL_HP = "100-69 % HP"
        self.FLAIL_HALF_HP = "69-35 % HP"
        self.FLAIL_QUARTER_HP = "35-20 % HP"
        self.FLAIL_TEN_PERCENT_HP = "20-10 % HP"
        self.FLAIL_FIVE_PERCENT_HP = "10-4 % HP"
        self.FLAIL_MIN_HP = "4-0 % HP"

        self.FURY_CUTTER_MOVE_NAME = "Fury Cutter"
        self.ROLLOUT_MOVE_NAME = "Rollout"
        self.TRIPLE_KICK_MOVE_NAME = "Triple Kick"
        self.RAGE_MOVE_NAME = "Rage"

        self.PURSUIT_MOVE_NAME = "Pursuit"
        self.STOMP_MOVE_NAME = "Stomp"
        self.GUST_MOVE_NAME = "Gust"
        self.TWISTER_MOVE_NAME = "Twister"
        self.EARTHQUAKE_MOVE_NAME = "Earthquake"
        self.RETURN_MOVE_NAME = "Return"

        self.CUSTOM_MOVE_DATA = {
            self.MAGNITUDE_MOVE_NAME: [
                self.MAGNITUDE_7, self.MAGNITUDE_7 + " " + self.DIG_BONUS,
                self.MAGNITUDE_4, self.MAGNITUDE_4 + " " + self.DIG_BONUS,
                self.MAGNITUDE_5, self.MAGNITUDE_5 + " " + self.DIG_BONUS,
                self.MAGNITUDE_6, self.MAGNITUDE_6 + " " + self.DIG_BONUS,
                self.MAGNITUDE_8, self.MAGNITUDE_8 + " " + self.DIG_BONUS,
                self.MAGNITUDE_9, self.MAGNITUDE_9 + " " + self.DIG_BONUS,
                self.MAGNITUDE_10, self.MAGNITUDE_10 + " " + self.DIG_BONUS,
            ],
            const.FLAIL_MOVE_NAME: [
                self.FLAIL_FULL_HP,
                self.FLAIL_HALF_HP,
                self.FLAIL_QUARTER_HP,
                self.FLAIL_TEN_PERCENT_HP,
                self.FLAIL_FIVE_PERCENT_HP,
                self.FLAIL_MIN_HP,
            ],
            const.REVERSAL_MOVE_NAME: [
                self.FLAIL_FULL_HP,
                self.FLAIL_HALF_HP,
                self.FLAIL_QUARTER_HP,
                self.FLAIL_TEN_PERCENT_HP,
                self.FLAIL_FIVE_PERCENT_HP,
                self.FLAIL_MIN_HP,
            ],
            self.FURY_CUTTER_MOVE_NAME: ["1", "2", "3", "4", "5", "6"],
            self.ROLLOUT_MOVE_NAME: ["1", "2", "3", "4", "5", "5 + DefenseCurl"],
            self.TRIPLE_KICK_MOVE_NAME: ["1", "2", "3"],
            self.RAGE_MOVE_NAME: ["1", "2", "3", "4", "5", "6"],

            self.PURSUIT_MOVE_NAME: [self.NO_BONUS, self.SWITCH_BONUS],
            self.STOMP_MOVE_NAME: [self.NO_BONUS, self.MINIMIZE_BONUS],
            self.GUST_MOVE_NAME: [self.NO_BONUS, self.FLY_BONUS],
            self.TWISTER_MOVE_NAME: [self.NO_BONUS, self.FLY_BONUS],
            self.EARTHQUAKE_MOVE_NAME: [self.NO_BONUS, self.DIG_BONUS],
            self.RETURN_MOVE_NAME: [str(x) for x in range(102, 0, -1)],
        }


gen_three_const = GenThreeConstants()
