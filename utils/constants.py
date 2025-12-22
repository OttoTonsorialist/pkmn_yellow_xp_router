import os
import appdirs
import sys


class Constants:
    def __init__(self):
        self.APP_VERSION = "v3.1k"
        self.APP_RELEASE_DATE = "2025-Dec-20"

        self.DEBUG_MODE = False
        self.DEBUG_RECORDING_MODE = False
        self.APP_NAME = "pkmn_xp_router"
        self.APP_DATA_FOLDER_DEFAULT_NAME = "pkmn_xp_router_data"
        self.USER_LOCATION_DATA_KEY = "user_data_location"
        self.IMAGE_LOCATION_KEY = "image_export_location"

        self.SOURCE_ROOT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.GLOBAL_CONFIG_DIR = os.path.realpath(appdirs.user_data_dir(appname=self.APP_NAME, appauthor=self.APP_NAME))
        self.GLOBAL_CONFIG_FILE = os.path.join(self.GLOBAL_CONFIG_DIR, "config.json")
        self.POKEMON_RAW_DATA = os.path.join(self.SOURCE_ROOT_PATH, "raw_pkmn_data")
        self.ASSETS_PATH = os.path.join(self.SOURCE_ROOT_PATH, "assets")

        # internal constants for configurable locations
        self._SAVED_ROUTES_FOLDER_NAME = "saved_routes"
        self.SAVED_IMAGES_FOLDER_NAME = "images"
        self._OUTDATED_ROUTES_FOLDER_NAME = "outdated_routes"
        self._CUSTOM_GENS_FOLDER_NAME = "custom_gens"
        # locations that change based on user data dir
        self.SAVED_ROUTES_DIR = None
        self.OUTDATED_ROUTES_DIR = None
        self.CUSTOM_GENS_DIR = None
        self.ALL_USER_DATA_PATHS = []

        self.CUSTOM_GEN_META_FILE_NAME = "custom_gen.json"
        self.CUSTOM_GEN_NAME_KEY = "custom_gen_name"
        self.BASE_GEN_NAME_KEY = "base_gen_name"

        # bunch of keys just for file management crap
        self.MAJOR_FIGHTS_KEY = "major_fights"
        self.BADGE_REWARDS_KEY = "badge_rewards"
        self.FIGHT_REWARDS_KEY = "fight_rewards"
        self.TYPE_CHART_KEY = "type_chart"
        self.SPECIAL_TYPES_KEY = "special_types"
        self.HELD_ITEM_BOOSTS_KEY = "held_item_boosts"
        self.TRAINER_TIMING_INFO_KEY = "trainer_timing_info"
        self.INTRO_TIME_KEY = "intro_time"
        self.OUTRO_TIME_KEY = "outro_time"
        self.KO_TIME_KEY = "ko_time"
        self.SEND_OUT_TIME_KEY = "send_out_time"

        # file names (without full paths)
        self.ITEM_DB_FILE_NAME = "items.json"
        self.MOVE_DB_FILE_NAME = "moves.json"
        self.POKEMON_DB_FILE_NAME = "pokemon.json"
        self.TRAINERS_DB_FILE_NAME = "trainers.json"
        self.TYPE_INFO_FILE_NAME = "type_info.json"
        self.FIGHTS_INFO_FILE_NAME = "fights_info.json"

        self.SPECIES_KEY = "species"
        self.NAME_KEY = "name"
        self.STATS_KEY = "stats"
        self.BASE_STATS_KEY = "base_stats"
        self.BASE_HP_KEY = "base_hp"
        self.BASE_ATK_KEY = "base_atk"
        self.BASE_DEF_KEY = "base_def"
        self.BASE_SPA_KEY = "base_spc_atk"
        self.BASE_SPD_KEY = "base_spc_def"
        self.OLD_BASE_SPD_KEY = "base_spd"
        self.BASE_SPE_KEY = "base_spe"
        self.BASE_SPC_KEY = "base_spc"
        self.EV_YIELD_KEY = "ev_yield"
        self.EV_YIELD_HP_KEY = "ev_yield_hp"
        self.EV_YIELD_ATK_KEY = "ev_yield_atk"
        self.EV_YIELD_DEF_KEY = "ev_yield_def"
        self.EV_YIELD_SPC_ATK_KEY = "ev_yield_spc_atk"
        self.EV_YIELD_SPC_DEF_KEY = "ev_yield_spc_def"
        self.EV_YIELD_SPD_KEY = "ev_yield_spd"
        self.FIRST_TYPE_KEY = "type_1"
        self.SECOND_TYPE_KEY = "type_2"
        self.CATCH_RATE_KEY = "catch_rate"
        self.BASE_XP_KEY = "base_xp"
        self.BASE_EXPERIENCE_KEY = "base_experience"
        self.INITIAL_MOVESET_KEY = "initial_moveset"
        self.LEARNED_MOVESET_KEY = "levelup_moveset"
        self.LEVEL_UP_MOVESET_KEY = "level_up_learnset"
        self.GROWTH_RATE_KEY = "growth_rate"
        self.TM_HM_LEARNSET_KEY = "tm_hm_learnset"
        self.DVS_KEY = "dv"
        self.IVS_KEY = "iv"
        self.IVS_PLURAL_KEY = "ivs"
        self.HELD_ITEM_KEY = "held_item"
        self.ABILITY_KEY = "ability"
        self.ABILITY_LIST_KEY = "abilities"
        self.WEIGHT_KEY = "weight"
        self.STAT_KEY = "stat"
        self.STATS_KEY = "stats"
        self.MODIFIER_KEY = "modifier"
        self.TARGET_KEY = "target"
        self.NATURE_KEY = "nature"

        self.LEVEL = "level"
        self.HP = "hp"
        self.ATK = "atk"
        self.DEF = "def"
        self.SPA = "spa"
        self.SPD = "spd"
        self.SPE = "spe"
        # TODO: remove
        # unified special, for gen 1 only
        self.SPC = "spc"
        self.EXPERIENCE_YIELD_KEY = "experience_yield"
        self.XP = "xp"
        self.MOVES = "moves"
        # less common, still stats
        self.EV = "ev"
        self.ACC = "acc"

        self.ATTACK = "attack"
        self.DEFENSE = "defense"
        self.SPEED = "speed"
        self.SPECIAL_ATTACK = "special_attack"
        self.SPECIAL_DEFENSE = "special_defense"

        self.TRAINER_NAME = "trainer_name"
        self.SECOND_TRAINER_NAME = "second_trainer_name"
        self.TRAINER_CLASS = "trainer_class"
        self.ROM_ID = "rom_id"
        self.TRAINER_ID = "trainer_id"
        self.TRAINER_LOC = "trainer_location"
        self.TRAINER_PARTY = "party"
        self.TRAINER_POKEMON = "pokemon"
        self.TRAINER_REFIGHTABLE = "refightable"
        self.TRAINER_DOUBLE_BATTLE = "is_double_battle"
        self.SPECIAL_MOVES = "special_moves"
        self.MONEY = "money"
        self.VERBOSE_KEY = "verbose"
        self.SETUP_MOVES_KEY = "setup_moves"
        self.ENEMY_SETUP_MOVES_KEY = "enemy_setup_moves"
        self.PLAYER_FIELD_MOVES_KEY = "player_field_moves"
        self.ENEMY_FIELD_MOVES_KEY = "enemy_field_moves"
        self.MIMIC_SELECTION = "mimic_selection"
        self.CUSTOM_MOVE_DATA = "custom_move_data"
        self.EXP_SPLIT = "exp_split"
        self.WEATHER = "weather"
        self.PAY_DAY_AMOUNT = "pay_day_amount"
        self.MON_ORDER = "mon_order"
        self.TRANSFORMED = "transformed"
        self.PLAYER_KEY = "player"
        self.ENEMY_KEY = "enemy"
        self.EVOLVED_SPECIES = "evolved_species"
        self.BY_STONE_KEY = "by_stone"

        self.MOVE_TYPE = "type"
        self.POWER = "power"
        self.BASE_POWER = "base_power"
        self.MOVE_PP = "pp"
        self.MOVE_ACCURACY = "accuracy"
        self.MOVE_EFFECTS = "effects"
        self.MOVE_EFFECT = "effect"
        self.MOVE_FLAVOR = "attack_flavor"
        self.MOVE_TARGET = "target"
        self.MOVE_CATEGORY = "category"
        self.CATEGORY_PHYSICAL = "Physical"
        self.CATEGORY_SPECIAL = "Special"
        self.MOVE_HAS_FIELD_EFFECT = "has_field_effect"

        self.GROWTH_RATE_FAST = "growth_fast"
        self.GROWTH_RATE_MEDIUM_FAST = "growth_medium_fast"
        self.GROWTH_RATE_MEDIUM_SLOW = "growth_medium_slow"
        self.GROWTH_RATE_SLOW = "growth_slow"
        self.GROWTH_RATE_ERRATIC = "growth_erratic"
        self.GROWTH_RATE_FLUCTUATING = "growth_fluctuating"

        self.HP_UP = "HP Up"
        self.CARBOS = "Carbos"
        self.IRON = "Iron"
        self.CALCIUM = "Calcium"
        self.ZINC = "Zinc"
        self.PROTEIN = "Protein"
        self.RARE_CANDY = "Rare Candy"

        self.HIGHLIGHT_NONE = "Don't Highlight"
        self.HIGHLIGHT_GUARANTEED_KILL = "Guaranteed Kill"
        self.HIGHLIGHT_CONSISTENT_KILL = "Consistent Kill"
        self.HIGHLIGHT_FASTEST_KILL = "Fastest Kill"

        self.ALL_HIGHLIGHT_STRATS = [
            self.HIGHLIGHT_GUARANTEED_KILL,
            self.HIGHLIGHT_CONSISTENT_KILL,
            self.HIGHLIGHT_FASTEST_KILL,
            self.HIGHLIGHT_NONE,
        ]

        self.DEFAULT_FOLDER_NAME = "Main"
        self.EVENT_FOLDER_NAME = "Event Folder Name"
        self.INVENTORY_EVENT_DEFINITON = "Inventory Event"

        self.TASK_TRAINER_BATTLE = "Fight Trainer"
        self.TASK_RARE_CANDY = "Use Rare Candy"
        self.TASK_VITAMIN = "Use Vitamin"
        self.TASK_FIGHT_WILD_PKMN = "Fight Wild Pkmn"
        self.TASK_GET_FREE_ITEM = "Acquire Item"
        self.TASK_PURCHASE_ITEM = "Purchase Item"
        self.TASK_USE_ITEM = "Use/Drop Item"
        self.TASK_SELL_ITEM = "Sell Item"
        self.TASK_HOLD_ITEM = "Hold Item"
        self.TASK_LEARN_MOVE_LEVELUP = "Learn Levelup Move"
        self.TASK_LEARN_MOVE_TM = "Learn TM/HM Move"
        self.TASK_SAVE = "Game Save"
        self.TASK_HEAL = "PkmnCenter Heal"
        self.TASK_BLACKOUT = "Blackout"
        self.TASK_EVOLUTION = "Evolution"
        self.TASK_NOTES_ONLY = "Just Notes"
        self.ERROR_SEARCH = "Invalid Events"

        self.ITEM_ROUTE_EVENT_TYPES = [
            self.TASK_GET_FREE_ITEM,
            self.TASK_PURCHASE_ITEM,
            self.TASK_USE_ITEM,
            self.TASK_SELL_ITEM,
            self.TASK_HOLD_ITEM,
        ]

        self.ROUTE_EVENT_TYPES = [
            self.TASK_TRAINER_BATTLE,
            self.TASK_FIGHT_WILD_PKMN,
            self.TASK_LEARN_MOVE_LEVELUP,
            self.TASK_LEARN_MOVE_TM,
            self.TASK_HOLD_ITEM,
            self.TASK_RARE_CANDY,
            self.TASK_VITAMIN,
            self.TASK_GET_FREE_ITEM,
            self.TASK_PURCHASE_ITEM,
            self.TASK_USE_ITEM,
            self.TASK_SELL_ITEM,
            self.TASK_SAVE,
            self.TASK_HEAL,
            self.TASK_BLACKOUT,
            self.TASK_EVOLUTION,
            self.TASK_NOTES_ONLY,
            # NOTE: not a full type, but we only use this list for populating the search component
            self.ERROR_SEARCH,
        ]

        self.ITEM_TYPE_ALL_ITEMS = "All Items"
        self.ITEM_TYPE_BACKPACK_ITEMS = "Items in Backpack"
        self.ITEM_TYPE_KEY_ITEMS = "Key Items"
        self.ITEM_TYPE_TM = "TMs"
        self.ITEM_TYPE_OTHER = "Other"

        self.ITEM_TYPES = [
            self.ITEM_TYPE_ALL_ITEMS,
            self.ITEM_TYPE_BACKPACK_ITEMS,
            self.ITEM_TYPE_KEY_ITEMS,
            self.ITEM_TYPE_TM,
            self.ITEM_TYPE_OTHER
        ]

        self.ALL_TRAINERS = "ALL"
        self.NO_TRAINERS = "No Valid Trainers"
        self.NO_POKEMON = "No Valid Pokemon"
        self.NO_ITEM = "No Valid Items"
        self.NO_MOVE = "No Valid Moves"
        self.UNUSED_TRAINER_LOC = "Unused"
        self.EVENTS = "events"
        self.ENABLED_KEY = "Enabled"
        self.EXPANDED_KEY = "Expanded"
        self.TAGS_KEY = "Tags"

        self.HIGHLIGHT_LABEL = "highlight"

        self.IS_KEY_ITEM = "key_item"
        self.PURCHASE_PRICE = "purchase_price"
        self.MARTS = "marts"

        self.EVENT_TAG_IMPORTANT = "important"
        self.EVENT_TAG_ERRORS = "errors"

        self.MOVE_KEY = "move"
        self.MOVE_DEST_KEY = "destination_slot"
        self.MOVE_SOURCE_KEY = "source"
        self.MOVE_LEVEL_KEY = "level_learned"
        self.MOVE_MON_KEY = "species_when_learned"

        self.LEARN_MOVE_KEY = "LearnMove"
        self.MOVE_SLOT_TEMPLATE = "Move #{} (Over {})"
        self.MOVE_DONT_LEARN = "Don't Learn"
        self.MOVE_SOURCE_LEVELUP = "LevelUp"
        self.MOVE_SOURCE_TUTOR = "Tutor/Deleter"
        self.MOVE_SOURCE_TM_HM = "TM/HM"
        self.LEVEL_ANY = "AnyLevel"
        self.DELETE_MOVE = "Delete Move"

        self.SUCCESS_COLOR_KEY = "success_color"
        self.WARNING_COLOR_KEY = "warning_color"
        self.FAILURE_COLOR_KEY = "failure_color"
        self.DIVIDER_COLOR_KEY = "divider_color"
        self.HEADER_COLOR_KEY = "header_color"
        self.PRIMARY_COLOR_KEY = "primary_color"
        self.SECONDARY_COLOR_KEY = "secondary_color"
        self.CONTRAST_COLOR_KEY = "contrast_color"
        self.BACKGROUND_COLOR_KEY = "background_color"
        self.TEXT_COLOR_KEY = "text_color"
        self.PLAYER_HIGHLIGHT_STRATEGY_KEY = "player_highlight_strategy"
        self.ENEMY_HIGHLIGHT_STRATEGY_KEY = "enemy_highlight_strategy"
        self.CONSISTENT_HIGHLIGHT_THRESHOLD = "consistent_highlight_threshold"
        self.IGNORE_ACCURACY_IN_DAMAGE_CALCS = "ignore_accuracy_in_damage_calcs"
        self.DAMAGE_SEARCH_DEPTH = "damage_search_depth"
        self.FORCE_FULL_SEARCH = "force_full_search"

        self.CUSTOM_FONT_NAME_KEY = "custom_font_name"
        self.DEBUG_MODE_KEY = "debug_mode"
        self.AUTO_SWITCH_KEY = "auto_switch"
        self.NOTES_VISIBILITY_KEY = "notes_visibility"

        # not configurable, just for important events in route list
        self.IMPORTANT_COLOR = "#b3b6b7"
        # not configurable, just for user flagged events in route list
        self.USER_FLAGGED_COLOR = "#ff8888"
        # not configurable, just for the top-right indicator
        self.VALID_COLOR = "#abebc6"
        self.ERROR_COLOR = "#f9e79f"

        self.CONFIG_ROUTE_ONE_PATH = "route_one_path"
        self.CONFIG_WINDOW_GEOMETRY = "tkinter_window_geometry"

        self.STATE_SUMMARY_LABEL = "State Summary"
        self.BADGE_BOOST_LABEL = "Badge Boost Calculator"

        self.ROOT_FOLDER_NAME = "ROOT"
        self.FORCE_QUIT_EVENT = "<<PkmnXpForceQuit>>"
        self.ROUTE_LIST_REFRESH_EVENT = "<<RouteListRefresh>>"
        self.BATTLE_SUMMARY_SHOWN_EVENT = "<<BattleSummaryShown>>"
        self.BATTLE_SUMMARY_HIDDEN_EVENT = "<<BattleSummaryHidden>>"

        self.EMPTY_ROUTE_NAME = "Empty Route"
        self.PRESET_ROUTE_PREFIX = "PRESET: "

        self.PKMN_VERSION_KEY = "Version"

        self.RED_VERSION = "Red"
        self.BLUE_VERSION = "Blue"
        self.YELLOW_VERSION = "Yellow"

        self.GOLD_VERSION = "Gold"
        self.SILVER_VERSION = "Silver"
        self.CRYSTAL_VERSION = "Crystal"

        self.RUBY_VERSION = "Ruby"
        self.SAPPHIRE_VERSION = "Sapphire"
        self.EMERALD_VERSION = "Emerald"

        self.FIRE_RED_VERSION = "FireRed"
        self.LEAF_GREEN_VERSION = "LeafGreen"

        self.DIAMOND_VERSION = "Diamond"
        self.PEARL_VERSION = "Pearl"
        self.PLATINUM_VERSION = "Platinum"

        self.HEART_GOLD_VERSION = "HeartGold"
        self.SOUL_SILVER_VERSION = "SoulSilver"

        self.VERSION_LIST = [
            self.YELLOW_VERSION,
            self.RED_VERSION,
            self.BLUE_VERSION,
            self.GOLD_VERSION,
            self.SILVER_VERSION,
            self.CRYSTAL_VERSION,
            self.RUBY_VERSION,
            self.SAPPHIRE_VERSION,
            self.EMERALD_VERSION,
            self.FIRE_RED_VERSION,
            self.LEAF_GREEN_VERSION,
            self.DIAMOND_VERSION,
            self.PEARL_VERSION,
            self.PLATINUM_VERSION,
            self.HEART_GOLD_VERSION,
            self.SOUL_SILVER_VERSION,
        ]

        self.FRLG_VERSIONS = [
            self.FIRE_RED_VERSION,
            self.LEAF_GREEN_VERSION,
        ]
        # not configurable, just for the version indicator
        self.VERSION_COLORS = {
            self.RED_VERSION: "#ff1111",
            self.BLUE_VERSION: "#1111ff",
            self.YELLOW_VERSION: "#ffd733",

            self.GOLD_VERSION: "#daa520",
            self.SILVER_VERSION: "#c0c0c0",
            self.CRYSTAL_VERSION: "#4FFFFF",

            self.RUBY_VERSION: "#a00000",
            self.SAPPHIRE_VERSION: "#0000a0",
            self.EMERALD_VERSION: "#00a000",

            self.FIRE_RED_VERSION: "#ff7327",
            self.LEAF_GREEN_VERSION: "#00dd00",

            self.DIAMOND_VERSION: "#90beed",
            self.PEARL_VERSION: "#e9aacc",
            self.PLATINUM_VERSION: "#a0a08d",

            self.HEART_GOLD_VERSION: "#e8b502",
            self.SOUL_SILVER_VERSION: "#c8d2e0",
        }

        self.NO_SAVED_ROUTES = "No Saved Routes"
        self.NO_FOLDERS = "No Matching Folders"

        self.TRANSFER_EXISTING_FOLDER = "Existing Folder"
        self.TRANSFER_NEW_FOLDER = "New Folder"

        self.MULTI_HIT_2 = "2 Hits"
        self.MULTI_HIT_3 = "3 Hits"
        self.MULTI_HIT_4 = "4 Hits"
        self.MULTI_HIT_5 = "5 Hits"

        self.MULTI_HIT_CUSTOM_DATA = [
            self.MULTI_HIT_2,
            self.MULTI_HIT_3,
            self.MULTI_HIT_4,
            self.MULTI_HIT_5,
        ]

        self.DOUBLE_HIT_FLAVOR = "two_hit"
        self.FLAVOR_MULTI_HIT = "multi_hit"
        self.FLAVOR_HIGH_CRIT = "high_crit"
        self.FLAVOR_FIXED_DAMAGE = "fixed_damage"
        self.FLAVOR_LEVEL_DAMAGE = "level_damage"
        self.FLAVOR_PSYWAVE = "psywave"
        self.FLAVOR_RECHARGE = "recharge"
        self.FLAVOR_TWO_TURN_INVULN = "two_turn_semi_invlunerable"
        self.FLAVOR_TWO_TURN = "two_turn"

        self.STRUGGLE_MOVE_NAME = "Struggle"
        self.MIMIC_MOVE_NAME = "Mimic"
        self.EXPLOSION_MOVE_NAME = "Explosion"
        self.SELFDESTRUCT_MOVE_NAME = "Selfdestruct"
        self.FLAIL_MOVE_NAME = "Flail"
        self.REVERSAL_MOVE_NAME = "Reversal"
        self.FUTURE_SIGHT_MOVE_NAME = "Future Sight"
        self.DOOM_DESIRE_MOVE_NAME = "Doom Desire"
        self.SPIT_UP_MOVE_NAME = "Spit Up"
        self.HIDDEN_POWER_MOVE_NAME = "Hidden Power"
        self.SOLAR_BEAM_MOVE_NAME = "SolarBeam"
        self.LIGHTSCREEN_SANITIZED_MOVE_NAME = "lightscreen"
        self.REFLECT_SANITIZED_MOVE_NAME = "reflect"
        self.GRAVITY_SANITIZED_MOVE_NAME = "gravity"
        self.MAGNET_RISE_SANITIZED_MOVE_NAME = "magnetrise"
        self.MIRACLE_EYE_SANITIZED_MOVE_NAME = "miracleeye"
        self.POWER_TRICK_SANITIZED_MOVE_NAME = "powertrick"
        self.ROOST_SANITIZED_MOVE_NAME = "roost"
        self.TAILWIND_SANITIZED_MOVE_NAME = "tailwind"
        self.TRICK_ROOM_SANITIZED_MOVE_NAME = "trickroom"
        self.WORRY_SEED_SANITIZED_MOVE_NAME = "worryseed"
        self.GASTRO_ACID_SANITIZED_MOVE_NAME = "gastroacid"
        self.SLOW_START_SANITIZED_NAME = "slowstart"

        self.AMULET_COIN_ITEM_NAME = "Amulet Coin"
        self.MACHO_BRACE_ITEM_NAME = "Macho Brace"
        self.POWER_ANKLET_ITEM_NAME = "Power Anklet"
        self.POWER_BAND_ITEM_NAME = "Power Band"
        self.POWER_BELT_ITEM_NAME = "Power Belt"
        self.POWER_BRACER_ITEM_NAME = "Power Bracer"
        self.POWER_LENS_ITEM_NAME = "Power Lens"
        self.POWER_WEIGHT_ITEM_NAME = "Power Weight"
        self.CHOICE_SCARF_ITEM_NAME = "Choice Scarf"
        self.SPEED_SLOWING_ITEMS = [
            self.MACHO_BRACE_ITEM_NAME,
            self.POWER_ANKLET_ITEM_NAME,
            self.POWER_BAND_ITEM_NAME,
            self.POWER_BELT_ITEM_NAME,
            self.POWER_BRACER_ITEM_NAME,
            self.POWER_LENS_ITEM_NAME,
            self.POWER_WEIGHT_ITEM_NAME,
        ]

        self.TARGETING_BOTH_ENEMIES = "target_both_enemies"

        self.TYPE_TYPELESS = "none"
        self.TYPE_NORMAL = "Normal"
        self.TYPE_FIGHTING = "Fighting"
        self.TYPE_FLYING = "Flying"
        self.TYPE_POISON = "Poison"
        self.TYPE_GROUND = "Ground"
        self.TYPE_ROCK = "Rock"
        self.TYPE_BUG = "Bug"
        self.TYPE_GHOST = "Ghost"
        self.TYPE_FIRE = "Fire"
        self.TYPE_WATER = "Water"
        self.TYPE_GRASS = "Grass"
        self.TYPE_ELECTRIC = "Electric"
        self.TYPE_PSYCHIC = "Psychic"
        self.TYPE_ICE = "Ice"
        self.TYPE_DRAGON = "Dragon"
        self.TYPE_STEEL = "Steel"
        self.TYPE_DARK = "Dark"

        self.SUPER_EFFECTIVE = "Super Effective"
        self.NOT_VERY_EFFECTIVE = "Not Very Effective"
        self.IMMUNE = "Immune"

        self.WEATHER_NONE = "None"
        self.WEATHER_RAIN = "Rain"
        self.WEATHER_SUN = "Harsh Sunlight"
        self.WEATHER_SANDSTORM = "Sandstorm"
        self.WEATHER_HAIL = "Hail"
        self.WEATHER_FOG = "Fog"

        # timing defaults
        self.DEFAULT_INTRO_TIME = 4.69
        self.DEFAULT_OUTRO_TIME = 1.195
        self.DEFAULT_KO_TIME = 1.84
        self.DEFAULT_SEND_OUT_TIME = 0.75

        self.GAME_SAVED_FRAGMENT = "Game Saved: "
        self.RECORDING_ERROR_FRAGMENT = "ERROR RECORDING! "
        self.BACKPORT_SPECIES_CHECK = "backport"

        self.RECORDING_STATUS_DISCONNECTED = "Disconnected"
        self.RECORDING_STATUS_CONNECTED = "Connected"
        self.RECORDING_STATUS_READY = "Ready"
        self.RECORDING_STATUS_NO_MAPPER = "Failed to load mapper. Have you loaded it in GameHook?"
        self.RECORDING_STATUS_WRONG_MAPPER = "Incorrect Mapper Loaded"
        self.RECORDING_STATUS_FAILED_CONNECTION = "Connection Failed. This usually means GameHook isn't running"
        self.RECORDING_STATUS_GAMEHOOK_FAILED = "Reading GameHook data failed. This version of GameHook may be incompatible with the router"

        self.EVENT_NAME_CHANGE = "<<RouteNameChange_{}>>"
        self.EVENT_VERSION_CHANGE = "<<GameVersionChange_{}>>"
        self.EVENT_ROUTE_CHANGE = "<<RouteChange_{}>>"
        self.EVENT_EVENT_CHANGE = "<<RouteEventChange_{}>>"
        self.EVENT_SELECTION_CHANGE = "<<EventSelectionChange_{}>>"
        self.EVENT_PREVIEW_CHANGE = "<<PreviewChange_{}>>"
        self.EVENT_RECORD_MODE_CHANGE = "<<RecordModeChange_{}>>"
        self.EVENT_EXCEPTION = "<<RouteException_{}>>"
        self.MESSAGE_EXCEPTION = "<<RouteMessage_{}>>"
        self.EVENT_RECORDER_STATUS_CHANGE = "<<RecorderStatusChange_{}>>"
        self.EVENT_RECORDER_READY_CHANGE = "<<RecorderReadyChange_{}>>"
        self.EVENT_RECORDER_GAME_STATE_CHANGE = "<<RecorderGameStateChange_{}>>"
        self.EVENT_MON_CHANGE = "<<MonChange_{}>>"
        self.EVENT_ACTIVE_MON_CHANGE = "<<ActiveMonChange_{}>>"
        self.EVENT_BADGE_CHANGE = "<<BadgeChange_{}>>"
        self.EVENT_TRAINER_CHANGE = "<<TrainerChange_{}>>"
        self.EVENT_BATTLE_SUMMARY_REFRESH = "<<BattleSummaryRefresh_{}>>"
        self.EVENT_BATTLE_SUMMARY_NONLOAD_CHANGE = "<<BattleSummaryNonloadChange_{}>>"
        self.EVENT_BATTLE_SUMMARY_MOVE_UPDATE = "<<BattleSummaryMoveUpdate_{}>>"
    
    def config_user_data_dir(self, user_data_dir):
        self.SAVED_ROUTES_DIR = os.path.realpath(os.path.join(user_data_dir, self._SAVED_ROUTES_FOLDER_NAME))
        self.OUTDATED_ROUTES_DIR = os.path.realpath(os.path.join(user_data_dir, self._OUTDATED_ROUTES_FOLDER_NAME))
        self.CUSTOM_GENS_DIR = os.path.realpath(os.path.join(user_data_dir, self._CUSTOM_GENS_FOLDER_NAME))

        self.ALL_USER_DATA_PATHS = [
            self.SAVED_ROUTES_DIR,
            self.OUTDATED_ROUTES_DIR,
            self.CUSTOM_GENS_DIR
        ]
    
    def get_potential_user_data_dirs(self, potential_user_data_dir):
        return [
            (self.SAVED_ROUTES_DIR, os.path.realpath(os.path.join(potential_user_data_dir, self._SAVED_ROUTES_FOLDER_NAME))),
            (self.OUTDATED_ROUTES_DIR, os.path.realpath(os.path.join(potential_user_data_dir, self._OUTDATED_ROUTES_FOLDER_NAME))),
            (self.CUSTOM_GENS_DIR, os.path.realpath(os.path.join(potential_user_data_dir, self._CUSTOM_GENS_FOLDER_NAME))),
        ]


const = Constants()
