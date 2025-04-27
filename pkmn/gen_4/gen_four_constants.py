import os

from utils.constants import const

class GenFourConstants:
    def __init__(self):
        self.GEN_FOUR_DATA_PATH = os.path.join(const.POKEMON_RAW_DATA, "gen_four")
        self.ITEM_DB_PATH = os.path.join(self.GEN_FOUR_DATA_PATH, const.ITEM_DB_FILE_NAME)
        self.MOVE_DB_PATH = os.path.join(self.GEN_FOUR_DATA_PATH, const.MOVE_DB_FILE_NAME)
        self.TYPE_INFO_PATH = os.path.join(self.GEN_FOUR_DATA_PATH, const.TYPE_INFO_FILE_NAME)
        self.FIGHTS_INFO_PATH = os.path.join(self.GEN_FOUR_DATA_PATH, const.FIGHTS_INFO_FILE_NAME)

        self.PLATINUM_POKEMON_PATH = os.path.join(self.GEN_FOUR_DATA_PATH, "platinum", const.POKEMON_DB_FILE_NAME)
        self.PLATINUM_TRAINER_DB_PATH = os.path.join(self.GEN_FOUR_DATA_PATH, "platinum", const.TRAINERS_DB_FILE_NAME)
        self.DP_POKEMON_PATH = os.path.join(self.GEN_FOUR_DATA_PATH, "diamond_pearl", const.POKEMON_DB_FILE_NAME)
        self.DP_TRAINER_DB_PATH = os.path.join(self.GEN_FOUR_DATA_PATH, "diamond_pearl", const.TRAINERS_DB_FILE_NAME)
        self.HGSS_POKEMON_PATH = os.path.join(self.GEN_FOUR_DATA_PATH, "heartgold_soulsilver", const.POKEMON_DB_FILE_NAME)
        self.HGSS_TRAINER_DB_PATH = os.path.join(self.GEN_FOUR_DATA_PATH, "heartgold_soulsilver", const.TRAINERS_DB_FILE_NAME)

        self.COAL_BADGE = "coal"
        self.FOREST_BADGE = "forest"
        self.COBBLE_BADGE = "cobble"
        self.FEN_BADGE = "fen"
        self.RELIC_BADGE = "relic"
        self.MINE_BADGE = "mine"
        self.ICICLE_BADGE = "icicle"
        self.BEACON_BADGE = "beacon"

        self.ZEPHYR_BADGE = "zephyr"
        self.HIVE_BADGE = "hive"
        self.PLAIN_BADGE = "plain"
        self.FOG_BADGE = "fog"
        self.STORM_BADGE = "storm"
        self.MINERAL_BADGE = "mineral"
        self.GLACIER_BADGE = "glacier"
        self.RISING_BADGE = "rising"

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
        self.CHOICE_SPECS_NAME = "Choice Specs"
        self.CHOICE_SCARF_NAME = "Choice Scarf"

        self.LATIOS_NAME = "Latios"
        self.LATIAS_NAME = "Latias"
        self.SOULD_DEW_NAME = "Soul Dew"

        self.COMPOUND_EYES_ABILITY = "Compound Eyes"
        self.LEVITATE_ABILITY = "Levitate"
        self.DAMP_ABILITY = "Damp"
        self.VOLT_ABOSRB_ABILITY = "Volt Absorb"
        self.LIGHTNING_ROD_ABILITY = "Lightning Rod"
        self.WATER_ABSORB_ABILITY = "Water Absorb"
        self.FLASH_FIRE_ABILITY = "Water Absorb"
        self.WONDER_GUARD_ABILITY = "Wonder Guard"
        self.BATTLE_ARMOR_ABILITY = "Battle Armor"
        self.SHELL_ARMOR_ABILITY = "Shell Armor"
        self.CLOUD_NINE_ABILITY = "Cloud Nine"
        self.AIR_LOCK_ABILITY = "Air Lock"
        self.HUSTLE_ABILITY = "Hustle"
        self.SAND_VEIL_ABILITY = "Sand Veil"
        self.HUGE_POWER_ABILITY = "Huge Power"
        self.PURE_POWER_ABILITY = "Pure Power"
        self.THICK_FAT_ABILITY = "Thick Fat"
        self.MARVEL_SCALE_ABILITY = "Marvel Scale"
        self.GUTS_ABILITY = "Guts"
        self.OVERGROW_ABILITY = "Overgrow"
        self.BLAZE_ABILITY = "Blaze"
        self.TORRENT_ABILITY = "Torrent"
        self.SWARM_ABILITY = "Swarm"
        self.NO_GUARD_ABILITY = "No Guard"
        self.SCRAPPY_ABILITY = "Scrappy"
        self.SNIPER_ABILITY = "Sniper"
        self.SNOW_CLOAK_ABILITY = "Snow Cloak"
        self.SUPER_LUCK_ABILITY = "Super Luck"
        self.ADAPTABILITY_ABILITY = "Adaptability"
        self.DRY_SKIN_ABILITY = "Dry Skin"
        self.FILTER_ABILITY = "Filter"
        self.SOLID_ROCK_ABILITY = "Solid Rock"
        self.FLOWER_GIFT_ABILITY = "Flower Gift"
        self.HEATPROOF_ABILITY = "Heatproof"
        self.KLUTZ_ABILITY = "Klutz"
        self.MOTOR_DRIVE_ABILITY = "Motor Drive"
        self.NORMALIZE_ABILITY = "Normalize"
        self.SOLAR_POWER_ABILITY = "Solar Power"
        self.TECHNICIAN_ABILITY = "Technician"
        self.TINTED_LENS_ABILITY = "Tinted Lens"

        self.NO_BONUS = "No Bonus"
        self.DIG_BONUS = "Dig Bonus"
        self.DIVE_BONUS = "Dive Bonus"
        self.FLY_BONUS = "Fly/Bounce Bonus"
        self.SWITCH_BONUS = "Switch Bonus"
        self.MINIMIZE_BONUS = "Minimize Bonus"
        self.STATUS_BONUS = "Status Bonus"
        self.PARALYSIS_BONUS = "Paralysis Bonus"
        self.DAMAGED_BONUS = "Damaged Bonus"
        self.LOW_HEALTH_BONUS = "Low Health Bonus"
        self.SECOND_BONUS = "Move Second Bonus"
        self.SLEEPING_BONUS = "Sleeping Bonus"

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
        self.ASSURANCE_MOVE_NAME = "Assurance"
        self.AVALANCHE_MOVE_NAME = "Avalanche"
        self.BRINE_MOVE_NAME = "Brine"
        self.PAYBACK_MOVE_NAME = "Payback"
        self.PUNISHMENT_MOVE_NAME = "Punishment"
        self.TRUMP_CARD_MOVE_NAME = "Trump Card"
        self.WAKE_UP_SLAP_MOVE_NAME = "Wake-Up Slap"
        self.CRUSH_GRIP_MOVE_NAME = "Crush Grip"
        self.WRING_OUT_MOVE_NAME = "Wring OUt"

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

            self.ASSURANCE_MOVE_NAME: [self.NO_BONUS, self.DAMAGED_BONUS],
            self.AVALANCHE_MOVE_NAME: [self.NO_BONUS, self.DAMAGED_BONUS],
            self.BRINE_MOVE_NAME: [self.NO_BONUS, self.LOW_HEALTH_BONUS],
            self.PAYBACK_MOVE_NAME: [self.NO_BONUS, self.SECOND_BONUS],
            self.TRUMP_CARD_MOVE_NAME: [str(x) if x < 4 else f"{x}+" for x in range(4, 0, -1)],
            self.WAKE_UP_SLAP_MOVE_NAME: [self.NO_BONUS, self.SLEEPING_BONUS],
            self.CRUSH_GRIP_MOVE_NAME: [str(x) for x in range(100, 0, -1)],
            self.WRING_OUT_MOVE_NAME_MOVE_NAME: [str(x) for x in range(100, 0, -1)],
        }


gen_four_const = GenFourConstants()
