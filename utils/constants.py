import os


class Constants:
    def __init__(self):
        self.DEBUG_MODE = False

        self.SOURCE_ROOT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.CONFIG_PATH = os.path.join(self.SOURCE_ROOT_PATH, "config.json")
        self.ROUTE_ONE_OUTPUT_PATH = os.path.join(self.SOURCE_ROOT_PATH, "route_one_output")
        self.POKEMON_RAW_DATA = os.path.join(self.SOURCE_ROOT_PATH, "raw_pkmn_data")
        self.ASSETS_PATH = os.path.join(self.SOURCE_ROOT_PATH, "assets")

        self.ITEM_DB_PATH = os.path.join(self.POKEMON_RAW_DATA, "items.json")
        self.MOVE_DB_PATH = os.path.join(self.POKEMON_RAW_DATA, "moves.json")
        self.SAVED_ROUTES_DIR = os.path.join(self.SOURCE_ROOT_PATH, "saved_routes")
        self.OUTDATED_ROUTES_DIR = os.path.join(self.SOURCE_ROOT_PATH, "outdated_routes")

        self.YELLOW_ASSETS_PATH = os.path.join(self.POKEMON_RAW_DATA, "yellow")
        self.YELLOW_POKEMON_DB_PATH = os.path.join(self.YELLOW_ASSETS_PATH, "pokemon.json")
        self.YELLOW_TRAINER_DB_PATH = os.path.join(self.YELLOW_ASSETS_PATH, "trainers.json")
        self.YELLOW_MIN_BATTLES_DIR = os.path.join(self.YELLOW_ASSETS_PATH, "min_battles")

        self.RB_ASSETS_PATH = os.path.join(self.POKEMON_RAW_DATA, "red_blue")
        self.RB_POKEMON_DB_PATH = os.path.join(self.RB_ASSETS_PATH, "pokemon.json")
        self.RB_TRAINER_DB_PATH = os.path.join(self.RB_ASSETS_PATH, "trainers.json")
        self.RB_MIN_BATTLES_DIR = os.path.join(self.RB_ASSETS_PATH, "min_battles")

        self.NAME_KEY = "name"
        self.BASE_HP_KEY = "base_hp"
        self.BASE_ATK_KEY = "base_atk"
        self.BASE_DEF_KEY = "base_def"
        self.BASE_SPA_KEY = "base_spa"
        self.BASE_SPD_KEY = "base_spd"
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

        self.LEVEL = "level"
        self.HP = "hp"
        self.ATK = "atk"
        self.DEF = "def"
        self.SPA = "spa"
        self.SPD = "spd"
        self.SPE = "spe"
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
        self.ROUTE_ONE_OFFSET = "route_one_offset"
        self.VERBOSE_KEY = "verbose"
        self.SETUP_MOVES_KEY = "setup_moves"
        self.MIMIC_SELECTION = "mimic_selection"

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

        self.BOULDER_BADGE = "boulder"
        self.CASCADE_BADGE = "cascade"
        self.THUNDER_BADGE = "thunder"
        self.RAINDBOW_BADGE = "rainbow"
        self.SOUL_BADGE = "soul"
        self.MARSH_BADGE = "marsh"
        self.VOLCANO_BADGE = "volcano"
        self.EARTH_BADGE = "earth"

        self.MAJOR_FIGHTS = [
            "Brock 1",
            "Misty 1",
            "LtSurge 1",
            "Erika 1",
            "Koga 1",
            "Sabrina 1",
            "Blaine 1",
            "Giovanni 3",
            "Agatha 1",
            "Bruno 1",
            "Lorelei 1",
            "Lance 1",
            "Rival3 Jolteon",
            "Rival3 Flareon",
            "Rival3 Vaporeon",
            "Rival3 Squirtle",
            "Rival3 Bulbasaur",
            "Rival3 Charmander",
        ]

        self.MINOR_FIGHTS = [
            "Giovanni 1",
            "Giovanni 2",
            # rb yival fights
            "Rival1 Squirtle 1",
            "Rival1 Bulbasaur 1",
            "Rival1 Charmander 1",
            "Rival1 Squirtle 2",
            "Rival1 Bulbasaur 2",
            "Rival1 Charmander 2",
            "Rival1 Squirtle 3",
            "Rival1 Bulbasaur 3",
            "Rival1 Charmander 3",
            "Rival2 Squirtle 1",
            "Rival2 Bulbasaur 1",
            "Rival2 Charmander 1",
            "Rival2 Squirtle 2",
            "Rival2 Bulbasaur 2",
            "Rival2 Charmander 2",
            "Rival2 Squirtle 3",
            "Rival2 Bulbasaur 3",
            "Rival2 Charmander 3",
            "Rival2 Squirtle 4",
            "Rival2 Bulbasaur 4",
            "Rival2 Charmander 4",
            # yellow rival fights
            "Rival1 1",
            "Rival1 2",
            "Rival1 3",
            "Rival2 1",
            "Rival2 2 Jolteon",
            "Rival2 2 Flareon",
            "Rival2 2 Vaporeon",
            "Rival2 3 Jolteon",
            "Rival2 3 Flareon",
            "Rival2 3 Vaporeon",
            "Rival2 4 Jolteon",
            "Rival2 4 Flareon",
            "Rival2 4 Vaporeon",
        ]

        self.BADGE_REWARDS = {
            "Brock 1": self.BOULDER_BADGE,
            "Misty 1": self.CASCADE_BADGE,
            "LtSurge 1": self.THUNDER_BADGE,
            "Erika 1": self.RAINDBOW_BADGE,
            "Koga 1": self.SOUL_BADGE,
            "Sabrina 1": self.MARSH_BADGE,
            "Blaine 1": self.VOLCANO_BADGE,
            "Giovanni 3": self.EARTH_BADGE,
        }

        self.FIGHT_REWARDS = {
            "Brock 1": "TM34 Bide",
            "Misty 1": "TM11 Bubblebeam",
            "LtSurge 1": "TM24 Thunderbolt",
            "Erika 1": "TM21 Mega Drain",
            "Koga 1": "TM06 Toxic",
            "Sabrina 1": "TM46 Psywave",
            "Blaine 1": "TM38 Fire Blast",
            "Giovanni 3": "TM27 Fissure",
            "SuperNerd 2": "Helix Fossil",
            "Rocket 6": "Nugget",
            "Rocket 5": "TM28 Dig",
            "Rocket 28": "Card Key",
            "Jessie & James 3": "Poke Flute",
        }

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
        self.TASK_LEARN_MOVE_LEVELUP = "Learn Levelup Move"
        self.TASK_LEARN_MOVE_TM = "Learn TM/HM Move"
        self.TASK_NOTES_ONLY = "Just Notes"

        self.ITEM_ROUTE_EVENT_TYPES = [
            self.TASK_GET_FREE_ITEM,
            self.TASK_PURCHASE_ITEM,
            self.TASK_USE_ITEM,
            self.TASK_SELL_ITEM,
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

        self.SPEED_WIN_COLOR = "#abebc6"
        self.SPEED_TIE_COLOR = "#f9e79f"
        self.SPEED_LOSS_COLOR = "#f5b7b1"

        self.VALID_COLOR = "#abebc6"
        self.ERROR_COLOR = "#f9e79f"
        self.IMPORTANT_COLOR = "#b3b6b7"

        self.BAG_LIMIT = 20

        self.CONFIG_ROUTE_ONE_PATH = "route_one_path"
        self.CONFIG_WINDOW_GEOMETRY = "tkinter_window_geometry"

        self.STAT_INCREASE_MOVES = {
            "Growth": (self.SPC, 1),
            "Swords Dance": (self.ATK, 2),
            "Meditate": (self.ATK, 1),
            "Agility": (self.SPE, 2),
            "Double Team": (self.EV, 1),
            "Harden": (self.DEF, 1),
            "Minimize": (self.EV, 1),
            "Withdraw": (self.DEF, 1),
            "Barrier": (self.DEF, 2),
            "Amnesia": (self.SPC, 2),
            "Acid Armor": (self.DEF, 2),
            "Sharpen": (self.ATK, 1),
        }

        # still source of badge boost, but not controlled by player
        self.STAT_DECREASE_MOVES = {
            "Sand Attack": (self.ACC, -1),
            "Smokescreen": (self.ACC, -1),
            "Kinesis": (self.ACC, -1),
            "Flash": (self.ACC, -1),
            "Tail Whip": (self.DEF, -1),
            "Leer": (self.DEF, -1),
            "Growl": (self.ATK, -1),
            "String Shot": (self.SPE, -1),
            "Screech": (self.DEF, -2),
            "Acid": (self.DEF, -1),
            "BubbleBeam": (self.SPE, -1),
            "Bubble": (self.SPE, -1),
            "Constrict": (self.SPE, -1),
            "Aurora Beam": (self.ATK, -1),
            "Psychic": (self.SPC, -1),
        }

        self.STATE_SUMMARY_LABEL = "State Summary"
        self.BADGE_BOOST_LABEL = "Badge Boost Calculator"

        self.ROOT_FOLDER_NAME = "ROOT"
        self.ROUTE_LIST_REFRESH_EVENT = "<<RouteListRefresh>>"
        self.BATTLE_SUMMARY_SHOWN_EVENT = "<<BattleSummaryShown>>"
        self.BATTLE_SUMMARY_HIDDEN_EVENT = "<<BattleSummaryHidden>>"

        self.EMPTY_ROUTE_NAME = "Empty Route"

        self.PKMN_VERSION_KEY = "Version"
        self.RED_VERSION = "Red"
        self.BLUE_VERSION = "Blue"
        self.YELLOW_VERSION = "Yellow"
        self.VERSION_LIST = [
            self.YELLOW_VERSION,
            self.RED_VERSION,
            self.BLUE_VERSION,
        ]

        self.YELLOW_COLOR = "yellow"
        self.RED_COLOR = "#ff8888"
        self.BLUE_COLOR = "#88b4ff"

        self.STAT_BG_COLOR = "#f0f3f4"
        self.MOVE_BG_COLOR = "#d4e6f1"
        self.HEADER_BG_COLOR = "#f6ddcc"

        self.NO_SAVED_ROUTES = "No Saved Routes"
        self.NO_FOLDERS = "No Matching Folders"

        self.TRANSFER_EXISTING_FOLDER = "Existing Folder"
        self.TRANSFER_NEW_FOLDER = "New Folder"

        self.FLAVOR_HIGH_CRIT = "high_crit"
        self.FLAVOR_FIXED_DAMAGE = "fixed_damage"
        self.FLAVOR_LEVEL_DAMAGE = "level_damage"
        self.FLAVOR_PSYWAVE = "psywave"

        self.SPECIAL_TYPES = [
            "water",
            "grass",
            "fire",
            "ice",
            "electric",
            "psychic",
            "dragon"
        ]

        self.STRUGGLE_MOVE_NAME = "Struggle"
        self.MIMIC_MOVE_NAME = "Mimic"
        self.EXPLOSION_MOVE_NAME = "Explosion"
        self.SELFDESTRUCT_MOVE_NAME = "Selfdestruct"

        self.TYPE_NORMAL = "normal"
        self.TYPE_FIGHTING = "fighting"
        self.TYPE_FLYING = "flying"
        self.TYPE_POISON = "poison"
        self.TYPE_GROUND = "ground"
        self.TYPE_ROCK = "rock"
        self.TYPE_BUG = "bug"
        self.TYPE_GHOST = "ghost"
        self.TYPE_FIRE = "fire"
        self.TYPE_WATER = "water"
        self.TYPE_GRASS = "grass"
        self.TYPE_ELECTRIC = "electric"
        self.TYPE_PSYCHIC = "psychic"
        self.TYPE_ICE = "ice"
        self.TYPE_DRAGON = "dragon"

        self.SUPER_EFFECTIVE = "Super Effective"
        self.NOT_VERY_EFFECTIVE = "Not Very Effective"
        self.IMMUNE = "Immune"

        self.TYPE_CHART = {
            self.TYPE_NORMAL: {
                self.TYPE_ROCK: self.NOT_VERY_EFFECTIVE,
                self.TYPE_GHOST: self.IMMUNE
            },
            self.TYPE_FIGHTING: {
                self.TYPE_NORMAL: self.SUPER_EFFECTIVE,
                self.TYPE_FLYING: self.NOT_VERY_EFFECTIVE,
                self.TYPE_POISON: self.NOT_VERY_EFFECTIVE,
                self.TYPE_ROCK: self.SUPER_EFFECTIVE,
                self.TYPE_BUG: self.NOT_VERY_EFFECTIVE,
                self.TYPE_GHOST: self.IMMUNE,
                self.TYPE_PSYCHIC: self.NOT_VERY_EFFECTIVE,
                self.TYPE_ICE: self.SUPER_EFFECTIVE,
            },
            self.TYPE_FLYING: {
                self.TYPE_FIGHTING: self.SUPER_EFFECTIVE,
                self.TYPE_ROCK: self.NOT_VERY_EFFECTIVE,
                self.TYPE_BUG: self.SUPER_EFFECTIVE,
                self.TYPE_GRASS: self.SUPER_EFFECTIVE,
                self.TYPE_ELECTRIC: self.NOT_VERY_EFFECTIVE,
            },
            self.TYPE_POISON: {
                self.TYPE_POISON: self.NOT_VERY_EFFECTIVE,
                self.TYPE_GROUND: self.NOT_VERY_EFFECTIVE,
                self.TYPE_ROCK: self.NOT_VERY_EFFECTIVE,
                self.TYPE_BUG: self.SUPER_EFFECTIVE,
                self.TYPE_GHOST: self.NOT_VERY_EFFECTIVE,
                self.TYPE_GRASS: self.SUPER_EFFECTIVE,
            },
            self.TYPE_GROUND: {
                self.TYPE_FLYING: self.IMMUNE,
                self.TYPE_POISON: self.SUPER_EFFECTIVE,
                self.TYPE_ROCK: self.SUPER_EFFECTIVE,
                self.TYPE_BUG: self.NOT_VERY_EFFECTIVE,
                self.TYPE_FIRE: self.SUPER_EFFECTIVE,
                self.TYPE_GRASS: self.NOT_VERY_EFFECTIVE,
                self.TYPE_ELECTRIC: self.SUPER_EFFECTIVE,
            },
            self.TYPE_ROCK: {
                self.TYPE_FIGHTING: self.NOT_VERY_EFFECTIVE,
                self.TYPE_FLYING: self.SUPER_EFFECTIVE,
                self.TYPE_GROUND: self.NOT_VERY_EFFECTIVE,
                self.TYPE_BUG: self.SUPER_EFFECTIVE,
                self.TYPE_FIRE: self.SUPER_EFFECTIVE,
                self.TYPE_ICE: self.SUPER_EFFECTIVE,
            },
            self.TYPE_BUG: {
                self.TYPE_FIGHTING: self.NOT_VERY_EFFECTIVE,
                self.TYPE_FLYING: self.NOT_VERY_EFFECTIVE,
                self.TYPE_POISON: self.SUPER_EFFECTIVE,
                self.TYPE_GHOST: self.NOT_VERY_EFFECTIVE,
                self.TYPE_FIRE: self.NOT_VERY_EFFECTIVE,
                self.TYPE_GRASS: self.SUPER_EFFECTIVE,
                self.TYPE_PSYCHIC: self.SUPER_EFFECTIVE,
            },
            self.TYPE_GHOST: {
                self.TYPE_NORMAL: self.IMMUNE,
                self.TYPE_GHOST: self.SUPER_EFFECTIVE,
                self.TYPE_PSYCHIC: self.IMMUNE,
            },
            self.TYPE_FIRE: {
                self.TYPE_ROCK: self.NOT_VERY_EFFECTIVE,
                self.TYPE_BUG: self.SUPER_EFFECTIVE,
                self.TYPE_FIRE: self.NOT_VERY_EFFECTIVE,
                self.TYPE_WATER: self.NOT_VERY_EFFECTIVE,
                self.TYPE_GRASS: self.SUPER_EFFECTIVE,
                self.TYPE_ICE: self.SUPER_EFFECTIVE,
                self.TYPE_DRAGON: self.NOT_VERY_EFFECTIVE,
            },
            self.TYPE_WATER: {
                self.TYPE_GROUND: self.SUPER_EFFECTIVE,
                self.TYPE_ROCK: self.SUPER_EFFECTIVE,
                self.TYPE_FIRE: self.SUPER_EFFECTIVE,
                self.TYPE_WATER: self.NOT_VERY_EFFECTIVE,
                self.TYPE_GRASS: self.NOT_VERY_EFFECTIVE,
                self.TYPE_DRAGON: self.NOT_VERY_EFFECTIVE,
            },
            self.TYPE_GRASS: {
                self.TYPE_FLYING: self.NOT_VERY_EFFECTIVE,
                self.TYPE_POISON: self.NOT_VERY_EFFECTIVE,
                self.TYPE_GROUND: self.SUPER_EFFECTIVE,
                self.TYPE_ROCK: self.SUPER_EFFECTIVE,
                self.TYPE_BUG: self.NOT_VERY_EFFECTIVE,
                self.TYPE_FIRE: self.NOT_VERY_EFFECTIVE,
                self.TYPE_WATER: self.SUPER_EFFECTIVE,
                self.TYPE_GRASS: self.NOT_VERY_EFFECTIVE,
                self.TYPE_DRAGON: self.NOT_VERY_EFFECTIVE,
            },
            self.TYPE_ELECTRIC: {
                self.TYPE_FLYING: self.SUPER_EFFECTIVE,
                self.TYPE_GROUND: self.IMMUNE,
                self.TYPE_WATER: self.SUPER_EFFECTIVE,
                self.TYPE_GRASS: self.NOT_VERY_EFFECTIVE,
                self.TYPE_ELECTRIC: self.NOT_VERY_EFFECTIVE,
                self.TYPE_DRAGON: self.NOT_VERY_EFFECTIVE,
            },
            self.TYPE_PSYCHIC: {
                self.TYPE_FIGHTING: self.SUPER_EFFECTIVE,
                self.TYPE_POISON: self.SUPER_EFFECTIVE,
                self.TYPE_PSYCHIC: self.NOT_VERY_EFFECTIVE,
            },
            self.TYPE_ICE: {
                self.TYPE_FLYING: self.SUPER_EFFECTIVE,
                self.TYPE_GROUND: self.SUPER_EFFECTIVE,
                self.TYPE_WATER: self.NOT_VERY_EFFECTIVE,
                self.TYPE_GRASS: self.SUPER_EFFECTIVE,
                self.TYPE_ICE: self.NOT_VERY_EFFECTIVE,
                self.TYPE_DRAGON: self.SUPER_EFFECTIVE,
            },
            self.TYPE_DRAGON: {
                self.TYPE_DRAGON: self.SUPER_EFFECTIVE,
            },
        }




const = Constants()
