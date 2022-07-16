import os


class Constants:
    def __init__(self):
        self.POKEMON_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pokemon.json")
        self.TRAINER_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trainers.json")
        self.MIN_BATTLES_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "min_battles.json")
        self.SAVED_ROUTES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_routes")

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

        self.TRAINER_NAME = "trainer_name"
        self.TRAINER_CLASS = "trainer_class"
        self.TRAINER_ID = "trainer_id"
        self.TRAINER_LOC = "trainer_location"
        self.TRAINER_POKEMON = "pokemon"
        self.SPECIAL_MOVES = "special_moves"
        self.MONEY = "money"

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

        self.HP_UP = "HP Up"
        self.CARBOS = "Carbos"
        self.IRON = "Iron"
        self.CALCIUM = "Calcium"
        self.PROTEIN = "Protein"

        self.VITAMIN_TYPES = [
            self.HP_UP,
            self.CARBOS,
            self.IRON,
            self.CALCIUM,
            self.PROTEIN
        ]

        self.TASK_TRAINER_BATTLE = "Fight Trainer"
        self.TASK_RARE_CANDY = "Use Rare Candy"
        self.TASK_VITAMIN = "Use Vitamin"

        self.ROUTE_EVENT_TYPES = [
            self.TASK_TRAINER_BATTLE,
            self.TASK_RARE_CANDY,
            self.TASK_VITAMIN
        ]

        self.ALL_TRAINERS = "ALL"
        self.NO_TRAINERS = "No Valid Trainers"
        self.UNUSED_TRAINER_LOC = "Unused"
        self.EVENTS = "events"
        self.EVENT_ID_COUNTER = "event_id_counter"



const = Constants()
