import os


class Constants:
    def __init__(self):
        self.DEBUG_MODE = False

        self.SOURCE_ROOT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.CONFIG_PATH = os.path.join(self.SOURCE_ROOT_PATH, "config.json")
        self.ROUTE_ONE_OUTPUT_PATH = os.path.join(self.SOURCE_ROOT_PATH, "route_one_output")
        self.POKEMON_RAW_DATA = os.path.join(self.SOURCE_ROOT_PATH, "raw_pkmn_data")

        self.POKEMON_DB_PATH = os.path.join(self.POKEMON_RAW_DATA, "pokemon.json")
        self.ITEM_DB_PATH = os.path.join(self.POKEMON_RAW_DATA, "items.json")
        self.TRAINER_DB_PATH = os.path.join(self.POKEMON_RAW_DATA, "trainers.json")
        self.MIN_BATTLES_DIR = os.path.join(self.POKEMON_RAW_DATA, "min_battles")
        self.SAVED_ROUTES_DIR = os.path.join(self.SOURCE_ROOT_PATH, "saved_routes")

        self.NAME_KEY = "name"
        self.BASE_HP_KEY = "base_hp"
        self.BASE_ATK_KEY = "base_atk"
        self.BASE_DEF_KEY = "base_def"
        self.BASE_SPD_KEY = "base_spd"
        self.BASE_SPC_KEY = "base_spc"
        self.FIRST_TYPE_KEY = "type_1"
        self.SECOND_TYPE_KEY = "type_2"
        self.CATCH_RATE_KEY = "catch_rate"
        self.BASE_XP_KEY = "base_xp"
        self.INITIAL_MOVESET_KEY = "initial_moveset"
        self.LEARNED_MOVESET_KEY = "levelup_moveset"
        self.GROWTH_RATE_KEY = "growth_rate"
        self.TM_HM_LEARNSET_KEY = "tm_hm_learnset"

        self.LEVEL = "level"
        self.HP = "hp"
        self.ATK = "atk"
        self.DEF = "def"
        self.SPD = "spd"
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
            "Rival2 3 Jolteon",
            "Rival2 3 Flareon",
            "Rival2 3 Vaporeon",
            "Rival2 4 Jolteon",
            "Rival2 4 Flareon",
            "Rival2 4 Vaporeon",
            "Agatha 1",
            "Bruno 1",
            "Lorelei 1",
            "Lance 1",
            "Rival3 Jolteon",
            "Rival3 Flareon",
            "Rival3 Vaporeon",
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

        self.STAT_INCREASE_MOVES = {
            "Growth": (self.SPC, 1),
            "Swords Dance": (self.ATK, 2),
            "Meditate": (self.ATK, 1),
            "Agility": (self.SPD, 2),
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
            "String Shot": (self.SPD, -1),
            "Screech": (self.DEF, -2),
            # NOTE: all moves that have a secondary effect to drop a stat only proc 33.2% of the time
            "Acid": (self.DEF, -1),
            "BubbleBeam": (self.SPD, -1),
            "Bubble": (self.SPD, -1),
            "Constrict": (self.SPD, -1),
            "Aurora Beam": (self.ATK, -1),
            "Psychic": (self.SPC, -1),
        }

        self.STATE_SUMMARY_LABEL = "State Summary"
        self.BADGE_BOOST_LABEL = "Badge Boost Calculator"



const = Constants()
