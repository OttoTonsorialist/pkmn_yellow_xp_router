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

        self.CLAMPERL_NAME = "Clamperl"
        self.DEEP_SEA_TOOTH_NAME = "DeepSeaTooth"
        self.DEEP_SEA_SCALE_NAME = "DeepSeaScale"
        self.CHOICE_BAND_NAME = "Choice Band"

        self.LATIOS_NAME = "Latios"
        self.LATIAS_NAME = "Latias"
        self.SOULD_DEW_NAME = "Soul Dew"

        self.BATTLE_ARMOR_ABILITY = "Battle Armor"
        self.SHELL_ARMOR_ABILITY = "Shell Armor"
        self.CLOUD_NINE_ABILITY = "Cloud Nine"
        self.AIR_LOCK_ABILITY = "Air Lock"
        self.HUSTLE_ABILITY = "Hustle"
        self.THICK_FAT_ABILITY = "Thick Fat"
        self.MARVEL_SCALE_ABILITY = "Marvel Scale"
        self.GUTS_ABILITY = "Guts"
        self.OVERGROW_ABILITY = "Overgrow"
        self.BLAZE_ABILITY = "Blaze"
        self.TORRENT_ABILITY = "Torrent"
        self.SWARM_ABILITY = "Swarm"

        self.NO_BONUS = "No Bonus"
        self.DIG_BONUS = "Dig Bonus"
        self.DIVE_BONUS = "Dive Bonus"
        self.FLY_BONUS = "Fly/Bounce Bonus"
        self.SWITCH_BONUS = "Switch Bonus"
        self.MINIMIZE_BONUS = "Minimize Bonus"
        self.STATUS_BONUS = "Status Bonus"
        self.PARALYSIS_BONUS = "Paralysis Bonus"
        self.DAMAGED_BONUS = "Damaged Bonus"

        self.PLAIN_TERRAIN = "Plain"
        self.SAND_TERRAIN = "Sand"
        self.CAVE_TERRAIN = "Cave"
        self.ROCK_TERRAIN = "Rock"
        self.TALL_GRASS_TERRAIN = "Tall Grass"
        self.LONG_GRASS_TERRAIN = "Long Grass"
        self.POND_WATER_TERRAIN = "Pond Water"
        self.SEA_WATER_TERRAIN = "Sea Water"
        self.UNDERWATER_TERRAIN = "Underwater"

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
        self.ICE_BALL_MOVE_NAME = "Ice Ball"
        self.TRIPLE_KICK_MOVE_NAME = "Triple Kick"
        self.RAGE_MOVE_NAME = "Rage"
        self.SPIT_UP_MOVE_NAME = "Spit Up"
        self.WEATHER_BALL_MOVE_NAME = "Weather Ball"
        self.PURSUIT_MOVE_NAME = "Pursuit"
        self.STOMP_MOVE_NAME = "Stomp"
        self.GUST_MOVE_NAME = "Gust"
        self.TWISTER_MOVE_NAME = "Twister"
        self.SURF_MOVE_NAME = "Surf"
        self.WHIRLPOOL_MOVE_NAME = "Whirlpool"
        self.EARTHQUAKE_MOVE_NAME = "Earthquake"
        self.RETURN_MOVE_NAME = "Return"
        self.FACADE_MOVE_NAME = "Facade"
        self.NEEDLE_ARM_MOVE_NAME = "Needle Arm"
        self.ASTONISH_MOVE_NAME = "Astonish"
        self.EXTRASENSORY_MOVE_NAME = "Extrasensory"
        self.SMELLING_SALT_MOVE_NAME = "SmellingSalt"
        self.REVENGE_MOVE_NAME = "Revenge"
        self.NATURE_POWER_MOVE_NAME = "Nature Power"
        self.BRICK_BREAK_MOVE_NAME = "Brick Break"
        self.ERUPTION_MOVE_NAME = "Eruption"
        self.WATER_SPOUT_MOVE_NAME = "Water Spout"

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
            self.NATURE_POWER_MOVE_NAME: [
                self.PLAIN_TERRAIN,
                self.SAND_TERRAIN,
                self.CAVE_TERRAIN,
                self.ROCK_TERRAIN,
                self.TALL_GRASS_TERRAIN,
                self.LONG_GRASS_TERRAIN,
                self.POND_WATER_TERRAIN,
                self.SEA_WATER_TERRAIN,
                self.UNDERWATER_TERRAIN,
            ],
            self.FURY_CUTTER_MOVE_NAME: ["1", "2", "3", "4", "5", "6"],
            self.ROLLOUT_MOVE_NAME: ["1", "2", "3", "4", "5", "5 + DefenseCurl"],
            self.ICE_BALL_MOVE_NAME: ["1", "2", "3", "4", "5", "5 + DefenseCurl"],
            self.TRIPLE_KICK_MOVE_NAME: ["1", "2", "3"],
            self.RAGE_MOVE_NAME: ["1", "2", "3", "4", "5", "6"],

            self.PURSUIT_MOVE_NAME: [self.NO_BONUS, self.SWITCH_BONUS],
            self.STOMP_MOVE_NAME: [self.NO_BONUS, self.MINIMIZE_BONUS],
            self.ASTONISH_MOVE_NAME: [self.NO_BONUS, self.MINIMIZE_BONUS],
            self.NEEDLE_ARM_MOVE_NAME: [self.NO_BONUS, self.MINIMIZE_BONUS],
            self.EXTRASENSORY_MOVE_NAME: [self.NO_BONUS, self.MINIMIZE_BONUS],
            self.GUST_MOVE_NAME: [self.NO_BONUS, self.FLY_BONUS],
            self.TWISTER_MOVE_NAME: [self.NO_BONUS, self.FLY_BONUS],
            self.EARTHQUAKE_MOVE_NAME: [self.NO_BONUS, self.DIG_BONUS],
            self.SURF_MOVE_NAME: [self.NO_BONUS, self.DIVE_BONUS],
            self.WHIRLPOOL_MOVE_NAME: [self.NO_BONUS, self.DIVE_BONUS],
            self.FACADE_MOVE_NAME: [self.NO_BONUS, self.STATUS_BONUS],
            self.SMELLING_SALT_MOVE_NAME: [self.NO_BONUS, self.PARALYSIS_BONUS],
            self.REVENGE_MOVE_NAME: [self.NO_BONUS, self.DAMAGED_BONUS],
            self.RETURN_MOVE_NAME: [str(x) for x in range(102, 0, -1)],
            self.ERUPTION_MOVE_NAME: [str(x) for x in range(100, 0, -1)],
            self.WATER_SPOUT_MOVE_NAME: [str(x) for x in range(100, 0, -1)],
            self.SPIT_UP_MOVE_NAME: [str(x) for x in range(1, 4)],
        }


gen_three_const = GenThreeConstants()
