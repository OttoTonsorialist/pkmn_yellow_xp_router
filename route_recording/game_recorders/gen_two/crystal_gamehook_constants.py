import logging

from utils.constants import const
from utils.io_utils import sanitize_string

logger = logging.getLogger(__name__)


class Gen2GameHookConstants:
    # NOTE: every key defined here is tied to a sepcific version of a GameHook mapper
    # if the keys in the mapper ever change such that they don't match anymore, the whole recorder will start to fail
    def __init__(self):
        self.RESET_FLAG = const.RECORDING_ERROR_FRAGMENT + "FLAG TO SIGNAL GAME RESET. USER SHOULD NEVER SEE THIS"
        self.TRAINER_LOSS_FLAG = const.RECORDING_ERROR_FRAGMENT + "FLAG TO SIGNAL LOSING TO TRAINER. USER SHOULD NEVER SEE THIS"
        self.ROAR_FLAG = const.RECORDING_ERROR_FRAGMENT + "FLAG TO SIGNAL ROARS NEED TO BE HANDLED. USER SHOULD NEVER SEE THIS"
        self.HELD_CHECK_FLAG = const.RECORDING_ERROR_FRAGMENT + "FLAG TO SIGNAL FOR DEEPER HELD ITEM CHECKING. USER SHOULD NEVER SEE THIS"

        self.KEY_OVERWORLD_MAP = "overworld.mapGroup"
        self.KEY_OVERWORLD_MAP_NUM = "overworld.mapNumber"
        self.KEY_OVERWORLD_X_POS = "overworld.x"
        self.KEY_OVERWORLD_Y_POS = "overworld.y"
        self.KEY_PLAYER_PLAYERID = "player.playerId"
        self.KEY_PLAYER_MONEY = "player.money"
        self.KEY_PLAYER_MON_EXPPOINTS = "player.team.0.expPoints"
        self.KEY_PLAYER_MON_LEVEL = "player.team.0.level"
        self.KEY_PLAYER_MON_SPECIES = "player.team.0.species"
        self.KEY_PLAYER_MON_HELD_ITEM = "player.team.0.heldItem"
        self.KEY_PLAYER_MON_FRIENDSHIP = "player.team.0.friendship"

        self.KEY_PLAYER_MON_MOVE_1 = "player.team.0.move1"
        self.KEY_PLAYER_MON_MOVE_2 = "player.team.0.move2"
        self.KEY_PLAYER_MON_MOVE_3 = "player.team.0.move3"
        self.KEY_PLAYER_MON_MOVE_4 = "player.team.0.move4"
        self.ALL_KEYS_PLAYER_MOVES = [
            self.KEY_PLAYER_MON_MOVE_1,
            self.KEY_PLAYER_MON_MOVE_2,
            self.KEY_PLAYER_MON_MOVE_3,
            self.KEY_PLAYER_MON_MOVE_4,
        ]

        self.KEY_PLAYER_MON_STAT_EXP_HP = "player.team.0.statExpHp"
        self.KEY_PLAYER_MON_STAT_EXP_ATTACK = "player.team.0.statExpAttack"
        self.KEY_PLAYER_MON_STAT_EXP_DEFENSE = "player.team.0.statExpDefense"
        self.KEY_PLAYER_MON_STAT_EXP_SPEED = "player.team.0.statExpSpeed"
        self.KEY_PLAYER_MON_STAT_EXP_SPECIAL = "player.team.0.statExpSpecial"
        self.ALL_KEYS_STAT_EXP = [
            self.KEY_PLAYER_MON_STAT_EXP_HP,
            self.KEY_PLAYER_MON_STAT_EXP_ATTACK,
            self.KEY_PLAYER_MON_STAT_EXP_DEFENSE,
            self.KEY_PLAYER_MON_STAT_EXP_SPEED,
            self.KEY_PLAYER_MON_STAT_EXP_SPECIAL,
        ]

        self.KEY_GAMETIME_SECONDS = "gameTime.seconds"
        self.KEY_GAMETIME_FRAMES = "gameTime.frames"
        self.KEY_AUDIO_CURRENT_SOUND = "audio.currentSound"
        self.PKMN_CENTER_HEAL_SOUND_ID = 18
        self.SAVE_HEAL_SOUND_ID = 37
        self.KEY_BATTLE_MODE = "battle.mode"
        self.KEY_BATTLE_TYPE = "battle.type"
        self.KEY_BATTLE_TEXT_BUFFER = "battle.textBuffer"
        self.KEY_BATTLE_RESULT = "battle.result"
        self.KEY_BATTLE_START = "battle.battleStart"
        self.KEY_BATTLE_TRAINER_CLASS = "battle.trainer.class"
        self.KEY_BATTLE_TRAINER_NAME = "battle.trainer.name"
        self.KEY_BATTLE_TRAINER_NUMBER = "battle.trainer.id"
        self.KEY_BATTLE_TRAINER_TOTAL_POKEMON = "battle.trainer.totalPokemon"
        self.KEY_BATTLE_PLAYER_MON_PARTY_POS = "battle.yourPokemon.partyPos"
        self.KEY_BATTLE_PLAYER_MON_SPECIES = "battle.yourPokemon.species"
        self.KEY_BATTLE_PLAYER_MON_HP = "battle.yourPokemon.hp"
        self.KEY_BATTLE_ENEMY_SPECIES = "battle.enemyPokemon.species"
        self.KEY_BATTLE_ENEMY_LEVEL = "battle.enemyPokemon.level"
        self.KEY_BATTLE_ENEMY_HP = "battle.enemyPokemon.hp"
        self.KEY_BATTLE_ENEMY_MON_PARTY_POS = "battle.enemyPokemon.partyPos"

        self.KEY_ITEM_COUNT = "player.itemCount"
        self.ALL_KEYS_ITEM_TYPE = [f"player.items.{i}.item" for i in range(0, 20)]
        self.ALL_KEYS_ITEM_QUANTITY = [f"player.items.{i}.quantity" for i in range(0, 20)]
        self.KEY_BALL_COUNT = "player.pokeBallCount"
        self.ALL_KEYS_BALL_TYPE = [f"player.pokeBalls.{i}.item" for i in range(0, 12)]
        self.ALL_KEYS_BALL_QUANTITY = [f"player.pokeBalls.{i}.quantity" for i in range(0, 12)]
        self.KEY_KEY_ITEM_COUNT = "player.totalKeyItems"
        self.ALL_KEYS_KEY_ITEMS = [f"player.keyItems.{i}" for i in range(0, 26)]

        self.ALL_TM_KEYS = [
            "player.tms.TM01-DynamicPunch",
            "player.tms.TM02-Headbutt",
            "player.tms.TM03-Curse",
            "player.tms.TM04-Rollout",
            "player.tms.TM05-Roar",
            "player.tms.TM06-Toxic",
            "player.tms.TM07-Zap Cannon",
            "player.tms.TM08-Rock Smash",
            "player.tms.TM09-Psych Up",
            "player.tms.TM10-Hidden Power",
            "player.tms.TM11-Sunny Day",
            "player.tms.TM12-Sweet Scent",
            "player.tms.TM13-Snore",
            "player.tms.TM14-Blizzard",
            "player.tms.TM15-Hyper Beam",
            "player.tms.TM16-Icy Wind",
            "player.tms.TM17-Protect",
            "player.tms.TM18-Rain Dance",
            "player.tms.TM19-Giga Drain",
            "player.tms.TM20-Endure",
            "player.tms.TM21-Frustration",
            "player.tms.TM22-SolarBeam",
            "player.tms.TM23-Iron Tail",
            "player.tms.TM24-Dragonbreath",
            "player.tms.TM25-Thunder",
            "player.tms.TM26-Earthquake",
            "player.tms.TM27-Return",
            "player.tms.TM28-Dig",
            "player.tms.TM29-Psychic",
            "player.tms.TM30-Shadow Ball",
            "player.tms.TM31-Mud-Slap",
            "player.tms.TM32-Double Team",
            "player.tms.TM33-Ice Punch",
            "player.tms.TM34-Swagger",
            "player.tms.TM35-Sleep Talk",
            "player.tms.TM36-Sludge Bomb",
            "player.tms.TM37-Sandstorm",
            "player.tms.TM38-Fire Blast",
            "player.tms.TM39-Swift",
            "player.tms.TM40-Defense Curl",
            "player.tms.TM41-ThunderPunch",
            "player.tms.TM42-Dream Eater",
            "player.tms.TM43-Detect",
            "player.tms.TM44-Rest",
            "player.tms.TM45-Attract",
            "player.tms.TM46-Thief",
            "player.tms.TM47-Steel Wing",
            "player.tms.TM48-Fire Punch",
            "player.tms.TM49-Fury Cutter",
            "player.tms.TM50-Nightmare",
        ]

        self.ALL_HM_KEYS = [
            "player.hms.HM01-Cut",
            "player.hms.HM02-Fly",
            "player.hms.HM03-Surf",
            "player.hms.HM04-Strength",
            "player.hms.HM05-Flash",
            "player.hms.HM06-Whirlpool",
            "player.hms.HM07-Waterfall",
        ]

        #self.ALL_KEYS_ALL_ITEM_FIELDS = set([self.KEY_ITEM_COUNT, self.KEY_BALL_COUNT, self.KEY_KEY_ITEM_COUNT])
        self.ALL_KEYS_ALL_ITEM_FIELDS = set([self.KEY_ITEM_COUNT, self.KEY_KEY_ITEM_COUNT])
        self.ALL_KEYS_ALL_ITEM_FIELDS.update(self.ALL_KEYS_ITEM_TYPE)
        self.ALL_KEYS_ALL_ITEM_FIELDS.update(self.ALL_KEYS_ITEM_QUANTITY)
        self.ALL_KEYS_ALL_ITEM_FIELDS.update(self.ALL_KEYS_BALL_TYPE)
        self.ALL_KEYS_ALL_ITEM_FIELDS.update(self.ALL_KEYS_BALL_QUANTITY)
        self.ALL_KEYS_ALL_ITEM_FIELDS.update(self.ALL_KEYS_KEY_ITEMS)
        self.ALL_KEYS_ALL_ITEM_FIELDS.update(self.ALL_TM_KEYS)
        self.ALL_KEYS_ALL_ITEM_FIELDS.update(self.ALL_HM_KEYS)

        self.ALL_KEYS_TO_REGISTER = [
            self.KEY_OVERWORLD_MAP,
            self.KEY_OVERWORLD_X_POS,
            self.KEY_OVERWORLD_Y_POS,
            self.KEY_PLAYER_PLAYERID,
            self.KEY_PLAYER_MONEY,
            self.KEY_PLAYER_MON_EXPPOINTS,
            self.KEY_PLAYER_MON_LEVEL,
            self.KEY_PLAYER_MON_SPECIES,
            self.KEY_PLAYER_MON_HELD_ITEM,
            self.KEY_GAMETIME_SECONDS,
            self.KEY_BATTLE_MODE,
            self.KEY_BATTLE_TYPE,
            self.KEY_BATTLE_TEXT_BUFFER,
            self.KEY_BATTLE_RESULT,
            self.KEY_BATTLE_START,
            self.KEY_BATTLE_PLAYER_MON_HP,
            self.KEY_BATTLE_PLAYER_MON_PARTY_POS,
            self.KEY_BATTLE_ENEMY_SPECIES,
            self.KEY_BATTLE_ENEMY_LEVEL,
            self.KEY_BATTLE_ENEMY_HP,
            self.KEY_BATTLE_ENEMY_MON_PARTY_POS,
            self.KEY_AUDIO_CURRENT_SOUND,
        ]
        self.ALL_KEYS_TO_REGISTER.extend(self.ALL_KEYS_PLAYER_MOVES)
        self.ALL_KEYS_TO_REGISTER.extend(self.ALL_KEYS_STAT_EXP)
        self.ALL_KEYS_TO_REGISTER.extend(self.ALL_KEYS_ALL_ITEM_FIELDS)

        self.TRAINER_BATTLE_TYPE = "Trainer"
        self.WILD_BATTLE_TYPE = "Wild"
        self.BATTLE_RESULT_DRAW = "DRAW"


class GameHookConstantConverter:
    def __init__(self):
        self._game_vitamins = [
            sanitize_string("HP UP"),
            sanitize_string("PROTEIN"),
            sanitize_string("IRON"),
            sanitize_string("CARBOS"),
            sanitize_string("CALCIUM"),
        ]
        self._game_rare_candy = sanitize_string("RARE CANDY")
    
    def is_game_vitamin(self, item_name):
        return sanitize_string(item_name) in self._game_vitamins
    
    def is_game_rare_candy(self, item_name):
        return sanitize_string(item_name) == self._game_rare_candy
    
    def is_game_tm(self, item_name):
        return item_name.startswith("TM")
    
    def _name_prettify(self, item_name:str):
        return " ".join([x.capitalize() for x in item_name.lower().split(" ")])

    TUTOR_MOVES = ["Thunderbolt", "Flamethrower", "Ice Beam"]
    def is_tutor_move(self, gh_move_name):
        return self._name_prettify(gh_move_name) in self.TUTOR_MOVES
    
    def get_hm_name(self, gh_move_name):
        gh_move_name = self._name_prettify(gh_move_name)
        if gh_move_name == "Cut":
            return "HM01 Cut"
        elif gh_move_name == "Fly":
            return "HM02 Fly"
        elif gh_move_name == "Surf":
            return "HM03 Surf"
        elif gh_move_name == "Strength":
            return "HM04 Strength"
        elif gh_move_name == "Flash":
            return "HM05 Flash"
        elif gh_move_name == "Whirlpool":
            return "HM06 Whirlpool"
        elif gh_move_name == "Waterfall":
            return "HM07 Waterfall"
        return None

    def get_tmhm_name_from_path(self, gh_path:str):
        # result should be TM## or HM##
        return gh_path.split(".")[-1].split("-")[0].upper()
    
    def item_name_convert(self, gh_item_name:str):
        if gh_item_name is None:
            return None
        
        if gh_item_name.startswith("TM") or gh_item_name.startswith("HM"):
            return gh_item_name

        converted_name:str = self._name_prettify(gh_item_name.replace("é", "e"))
        if converted_name == "Thunderstone":
            converted_name = "Thunder Stone"
        elif converted_name == "Hp Up":
            converted_name = "HP Up"
        elif converted_name == "Guard Spec.":
            converted_name = "Guard Spec"
        elif converted_name == "Exp.share":
            converted_name = "Exp Share"
        elif converted_name == "S.s.ticket":
            converted_name = "S S Ticket"
        elif converted_name == "King's Rock":
            converted_name = "Kings Rock"
        elif converted_name == "Silverpowder":
            converted_name = "SilverPowder"
        elif converted_name == "Twistedspoon":
            converted_name = "TwistedSpoon"
        elif converted_name == "Blackbelt":
            converted_name = "Black Belt"
        elif converted_name == "Blackglasses":
            converted_name = "BlackGlasses"
        elif converted_name == "Up-grade":
            converted_name = "Up Grade"
        elif converted_name == "Paralyze Heal":
            converted_name = "Parlyz Heal"

        return converted_name
    
    def move_name_convert(self, gh_move_name:str):
        if gh_move_name is None:
            return None
        converted_name:str = self._name_prettify(gh_move_name.replace("-", " "))

        if converted_name == "Doubleslap":
            converted_name = "DoubleSlap"
        elif converted_name == "Thunderpunch":
            converted_name = "ThunderPunch"
        elif converted_name == "Sand-attack":
            converted_name = "Sand Attack"
        elif converted_name == "Double-edge":
            converted_name = "Double-Edge"
        elif converted_name == "Sonicboom":
            converted_name = "SonicBoom"
        elif converted_name == "Bubblebeam":
            converted_name = "BubbleBeam"
        elif converted_name == "Solarbeam":
            converted_name = "SolarBeam"
        elif converted_name == "Poisonpowder":
            converted_name = "PoisonPowder"
        elif converted_name == "Thundershock":
            converted_name = "ThunderShock"
        elif converted_name == "Conversion2":
            converted_name = "Conversion 2"
        elif converted_name == "Mud-slap":
            converted_name = "Mud-Slap"
        elif converted_name == "Lock-on":
            converted_name = "Lock-On"
        elif converted_name == "Dynamicpunch":
            converted_name = "DynamicPunch"
        elif converted_name == "Dragonbreath":
            converted_name = "DragonBreath"
        elif converted_name == "Extremespeed":
            converted_name = "ExtremeSpeed"
        elif converted_name == "Ancientpower":
            converted_name = "AncientPower"
        elif converted_name == "Headbeutt":
            converted_name = "Headbutt"

        return converted_name
    
    def pkmn_name_convert(self, gh_pkmn_name:str):
        if gh_pkmn_name is None:
            return None
        converted_name = gh_pkmn_name

        if converted_name == "Mr. Mime":
            converted_name = "MrMime"
        elif converted_name == "Farfetch'd":
            converted_name = "FarfetchD"
        elif converted_name == "Ho-oh":
            converted_name = "HoOh"

        return converted_name
    
    LEADER_CLASSES = [
        "Falkner", "Whitney", "Bugsy", "Morty", "Pryce", "Jasmine", "Chuck", "Clair", "Brock", "Misty", "Lt.Surge",
        "Erika", "Janine", "Sabrina", "Blaine", "Blue", "Red"
    ]
    ELITE_FOUR_CLASSES = ["Will", "Bruno", "Karen", "Koga"]
    def _trainer_class_convert(self, gh_trainer_class:str):
        if gh_trainer_class is None:
            return None
        converted_name:str = self._name_prettify(gh_trainer_class)

        if converted_name == "Cal":
            converted_name = "PkmnTrainer"
        elif converted_name == "Cooltrainer M":
            converted_name = "CoolTrainerM"
        elif converted_name == "Cooltrainer F":
            converted_name = "CoolTrainerF"
        elif converted_name == "Grunt M":
            converted_name = "GruntM"
        elif converted_name == "Grunt F":
            converted_name = "GruntF"
        elif converted_name == "Swimmer M":
            converted_name = "SwimmerM"
        elif converted_name == "Swimmer F":
            converted_name = "SwimmerF"
        elif converted_name == "Executive M":
            converted_name = "ExecutiveM"
        elif converted_name == "Executive F":
            converted_name = "ExecutiveF"
        elif converted_name == "Pokefan M":
            converted_name = "PokefanM"
        elif converted_name == "Pokefan F":
            converted_name = "PokefanF"
        elif converted_name == "Mystical Man":
            converted_name = "Mysticalman"
        elif converted_name == "Lt. Surge":
            converted_name = "Lt.Surge"
        
        return converted_name

    def trainer_name_convert(self, trainer_class:str, trainer_num:int):
        trainer_class = self._trainer_class_convert(trainer_class)

        if trainer_class in self.LEADER_CLASSES:
            return f"Leader {trainer_class}"
        elif trainer_class in self.ELITE_FOUR_CLASSES:
            return f"Elite Four {trainer_class}"

        return f"{trainer_class}:{trainer_num}"
    
    def area_name_convert(self, area_name:str):
        area_name = area_name.split("-")[0].strip()

        return area_name


gh_gen_two_const = Gen2GameHookConstants()
