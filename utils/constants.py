import os
import appdirs
import sys


class Constants:
    def __init__(self):
        self.APP_VERSION = "v2.3d"
        self.APP_RELEASE_DATE = "2023-Jan-17"

        self.DEBUG_MODE = False
        self.APP_NAME = "pkmn_xp_router"
        self.APP_DATA_FOLDER_DEFAULT_NAME = "pkmn_xp_router_data"
        self.USER_LOCATION_DATA_KEY = "user_data_location"

        self.SOURCE_ROOT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.GLOBAL_CONFIG_DIR = os.path.realpath(appdirs.user_data_dir(appname=self.APP_NAME, appauthor=self.APP_NAME))
        self.GLOBAL_CONFIG_FILE = os.path.join(self.GLOBAL_CONFIG_DIR, "config.json")
        self.POKEMON_RAW_DATA = os.path.join(self.SOURCE_ROOT_PATH, "raw_pkmn_data")
        self.ASSETS_PATH = os.path.join(self.SOURCE_ROOT_PATH, "assets")

        # internal constants for configurable locations
        self._SAVED_ROUTES_FOLDER_NAME = "saved_routes"
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

        # file names (without full paths)
        self.ITEM_DB_FILE_NAME = "items.json"
        self.MOVE_DB_FILE_NAME = "moves.json"
        self.POKEMON_DB_FILE_NAME = "pokemon.json"
        self.TRAINERS_DB_FILE_NAME = "trainers.json"
        self.TYPE_INFO_FILE_NAME = "type_info.json"
        self.FIGHTS_INFO_FILE_NAME = "fights_info.json"

        self.NAME_KEY = "name"
        self.BASE_HP_KEY = "base_hp"
        self.BASE_ATK_KEY = "base_atk"
        self.BASE_DEF_KEY = "base_def"
        self.BASE_SPA_KEY = "base_spc_atk"
        self.BASE_SPD_KEY = "base_spc_def"
        self.OLD_BASE_SPD_KEY = "base_spd"
        self.BASE_SPE_KEY = "base_spe"
        self.BASE_SPC_KEY = "base_spc"
        self.FIRST_TYPE_KEY = "type_1"
        self.SECOND_TYPE_KEY = "type_2"
        self.CATCH_RATE_KEY = "catch_rate"
        self.BASE_XP_KEY = "base_xp"
        self.INITIAL_MOVESET_KEY = "initial_moveset"
        self.LEARNED_MOVESET_KEY = "levelup_moveset"
        self.GROWTH_RATE_KEY = "growth_rate"
        self.TM_HM_LEARNSET_KEY = "tm_hm_learnset"
        self.DVS_KEY = "dv"
        self.HELD_ITEM_KEY = "held_item"
        self.STAT_KEY = "stat"
        self.MODIFIER_KEY = "modifier"
        self.TARGET_KEY = "target"

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
        self.XP = "xp"
        self.MOVES = "moves"
        # less common, still stats
        self.EV = "ev"
        self.ACC = "acc"

        self.TRAINER_NAME = "trainer_name"
        self.TRAINER_CLASS = "trainer_class"
        self.TRAINER_ID = "trainer_id"
        self.TRAINER_LOC = "trainer_location"
        self.TRAINER_POKEMON = "pokemon"
        self.SPECIAL_MOVES = "special_moves"
        self.MONEY = "money"
        self.VERBOSE_KEY = "verbose"
        self.SETUP_MOVES_KEY = "setup_moves"
        self.MIMIC_SELECTION = "mimic_selection"
        self.CUSTOM_MOVE_DATA = "custom_move_data"
        self.PLAYER_KEY = "player"
        self.ENEMY_KEY = "enemy"

        self.MOVE_TYPE = "type"
        self.BASE_POWER = "base_power"
        self.MOVE_PP = "pp"
        self.MOVE_ACCURACY = "accuracy"
        self.MOVE_EFFECTS = "effects"
        self.MOVE_FLAVOR = "attack_flavor"

        self.GROWTH_RATE_FAST = "growth_fast"
        self.GROWTH_RATE_MEDIUM_FAST = "growth_medium_fast"
        self.GROWTH_RATE_MEDIUM_SLOW = "growth_medium_slow"
        self.GROWTH_RATE_SLOW = "growth_slow"

        self.HP_UP = "HP Up"
        self.CARBOS = "Carbos"
        self.IRON = "Iron"
        self.CALCIUM = "Calcium"
        self.PROTEIN = "Protein"
        self.RARE_CANDY = "Rare Candy"

        self.VITAMIN_TYPES = [
            self.HP_UP,
            self.CARBOS,
            self.IRON,
            self.CALCIUM,
            self.PROTEIN
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
        self.TASK_NOTES_ONLY = "Just Notes"

        self.ITEM_ROUTE_EVENT_TYPES = [
            self.TASK_GET_FREE_ITEM,
            self.TASK_PURCHASE_ITEM,
            self.TASK_USE_ITEM,
            self.TASK_SELL_ITEM,
            self.TASK_HOLD_ITEM,
        ]

        self.ROUTE_EVENT_TYPES = [
            self.TASK_TRAINER_BATTLE,
            self.TASK_RARE_CANDY,
            self.TASK_VITAMIN,
            self.TASK_FIGHT_WILD_PKMN,
            self.TASK_GET_FREE_ITEM,
            self.TASK_PURCHASE_ITEM,
            self.TASK_USE_ITEM,
            self.TASK_SELL_ITEM,
            self.TASK_LEARN_MOVE_TM,
            self.TASK_NOTES_ONLY,
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

        self.LEARN_MOVE_KEY = "LearnMove"
        self.MOVE_SLOT_TEMPLATE = "Move #{} (Over {})"
        self.MOVE_DONT_LEARN = "Don't Learn"
        self.MOVE_SOURCE_LEVELUP = "LevelUp"
        self.LEVEL_ANY = "AnyLevel"

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

        self.CUSTOM_FONT_NAME_KEY = "custom_font_name"

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

        self.VERSION_LIST = [
            self.YELLOW_VERSION,
            self.RED_VERSION,
            self.BLUE_VERSION,
            self.GOLD_VERSION,
            self.SILVER_VERSION,
            self.CRYSTAL_VERSION,
        ]
        # not configurable, just for the version indicator
        self.VERSION_COLORS = {
            self.RED_VERSION: "#ff8888",
            self.BLUE_VERSION: "#88b4ff",
            self.YELLOW_VERSION: "yellow",

            self.GOLD_VERSION: "#aa9c66",
            self.SILVER_VERSION: "#bbc3c8",
            self.CRYSTAL_VERSION: "#4d96b9",
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

        self.STRUGGLE_MOVE_NAME = "Struggle"
        self.MIMIC_MOVE_NAME = "Mimic"
        self.EXPLOSION_MOVE_NAME = "Explosion"
        self.SELFDESTRUCT_MOVE_NAME = "Selfdestruct"
        self.FLAIL_MOVE_NAME = "Flail"
        self.REVERSAL_MOVE_NAME = "Reversal"
        self.FUTURE_SIGHT_MOVE_NAME = "Future Sight"
        self.HIDDEN_POWER_MOVE_NAME = "Hidden Power"

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

        self.GAME_SAVED_FRAGMENT = "Game Saved: "
        self.RECORDING_ERROR_FRAGMENT = "ERROR RECORDING! "

        self.RECORDING_STATUS_DISCONNECTED = "Disconnected"
        self.RECORDING_STATUS_CONNECTED = "Connected"
        self.RECORDING_STATUS_READY = "Ready"
        self.RECORDING_STATUS_NO_MAPPER = "Failed to load mapper. Have you loaded it in GameHook?"
        self.RECORDING_STATUS_WRONG_MAPPER = "Incorrect Mapper Loaded"
        self.RECORDING_STATUS_FAILED_CONNECTION = "Connection Failed. This usually means GameHook isn't running"

        self.EVENT_NAME_CHANGE = "<<RouteNameChange_{}>>"
        self.EVENT_VERSION_CHANGE = "<<GameVersionChange_{}>>"
        self.EVENT_ROUTE_CHANGE = "<<RouteChange_{}>>"
        self.EVENT_EVENT_CHANGE = "<<RouteEventChange_{}>>"
        self.EVENT_SELECTION_CHANGE = "<<EventSelectionChange_{}>>"
        self.EVENT_PREVIEW_CHANGE = "<<PreviewChange_{}>>"
        self.EVENT_RECORD_MODE_CHANGE = "<<RecordModeChange_{}>>"
        self.EVENT_EXCEPTION = "<<RouteException_{}>>"
        self.EVENT_RECORDER_STATUS_CHANGE = "<<RecorderStatusChange_{}>>"
        self.EVENT_RECORDER_READY_CHANGE = "<<RecorderReadyChange_{}>>"
        self.EVENT_RECORDER_GAME_STATE_CHANGE = "<<RecorderGameStateChange_{}>>"
    
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
