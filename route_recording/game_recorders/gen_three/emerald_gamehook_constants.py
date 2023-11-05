import logging

from utils.constants import const
from pkmn.pkmn_db import sanitize_string

logger = logging.getLogger(__name__)


class Gen3GameHookConstants:
    # NOTE: every key defined here is tied to a sepcific version of a GameHook mapper
    # if the keys in the mapper ever change such that they don't match anymore, the whole recorder will start to fail
    def __init__(self):
        self.RESET_FLAG = const.RECORDING_ERROR_FRAGMENT + "FLAG TO SIGNAL GAME RESET. USER SHOULD NEVER SEE THIS"
        self.TRAINER_LOSS_FLAG = const.RECORDING_ERROR_FRAGMENT + "FLAG TO SIGNAL LOSING TO TRAINER. USER SHOULD NEVER SEE THIS"
        self.ROAR_FLAG = const.RECORDING_ERROR_FRAGMENT + "FLAG TO SIGNAL ROARS NEED TO BE HANDLED. USER SHOULD NEVER SEE THIS"
        self.HELD_CHECK_FLAG = const.RECORDING_ERROR_FRAGMENT + "FLAG TO SIGNAL FOR DEEPER HELD ITEM CHECKING. USER SHOULD NEVER SEE THIS"

        self.KEY_DMA_A = "apointers.dma1"
        self.KEY_DMA_B = "apointers.dma2"
        self.KEY_DMA_C = "apointers.dma3"
        self.KEY_STATE_1 = "apointers.callback1"
        self.KEY_STATE_2 = "apointers.callback2"
        self.KEY_OVERWORLD_MAP = "overworld.mapName"
        self.KEY_PLAYER_PLAYERID = "player.playerId"
        self.KEY_PLAYER_MONEY = "player.money"
        self.KEY_PLAYER_MON_EXPPOINTS = "player.team.0.expPoints"
        self.KEY_PLAYER_MON_LEVEL = "player.team.0.level"
        self.KEY_PLAYER_MON_SPECIES = "player.team.0.species"
        self.KEY_PLAYER_MON_HELD_ITEM = "player.team.0.itemHeld"
        self.KEY_PLAYER_MON_FRIENDSHIP = "player.team.0.friendship"

        self.KEY_PLAYER_MON_MOVE_1 = "player.team.0.moves.0.move"
        self.KEY_PLAYER_MON_MOVE_2 = "player.team.0.moves.1.move"
        self.KEY_PLAYER_MON_MOVE_3 = "player.team.0.moves.2.move"
        self.KEY_PLAYER_MON_MOVE_4 = "player.team.0.moves.3.move"
        self.ALL_KEYS_PLAYER_MOVES = [
            self.KEY_PLAYER_MON_MOVE_1,
            self.KEY_PLAYER_MON_MOVE_2,
            self.KEY_PLAYER_MON_MOVE_3,
            self.KEY_PLAYER_MON_MOVE_4,
        ]

        self.KEY_PLAYER_MON_STAT_EXP_HP = "player.team.0.evs.hp"
        self.KEY_PLAYER_MON_STAT_EXP_ATTACK = "player.team.0.evs.attack"
        self.KEY_PLAYER_MON_STAT_EXP_DEFENSE = "player.team.0.evs.defense"
        self.KEY_PLAYER_MON_STAT_EXP_SPEED = "player.team.0.evs.speed"
        self.KEY_PLAYER_MON_STAT_EXP_SPECIAL_ATTACK = "player.team.0.evs.specialAttack"
        self.KEY_PLAYER_MON_STAT_EXP_SPECIAL_DEFENSE = "player.team.0.evs.specialDefense"
        self.ALL_KEYS_STAT_EXP = [
            self.KEY_PLAYER_MON_STAT_EXP_HP,
            self.KEY_PLAYER_MON_STAT_EXP_ATTACK,
            self.KEY_PLAYER_MON_STAT_EXP_DEFENSE,
            self.KEY_PLAYER_MON_STAT_EXP_SPEED,
            self.KEY_PLAYER_MON_STAT_EXP_SPECIAL_ATTACK,
            self.KEY_PLAYER_MON_STAT_EXP_SPECIAL_DEFENSE,
        ]

        self.KEY_GAMETIME_SECONDS = "gameTime.seconds"
        self.KEY_GAMETIME_FRAMES = "gameTime.frames"
        self.KEY_BATTLE_FLAG = "battle.turnInfo.type.is_battle"
        self.KEY_TRAINER_BATTLE_FLAG = "battle.turnInfo.type.trainer"
        self.KEY_DOUBLE_BATTLE_FLAG = "battle.turnInfo.type.double"
        self.KEY_MULTI_BATTLE_FLAG = "battle.turnInfo.type.multi"
        self.KEY_BATTLE_OUTCOME = "battle.turnInfo.battleOutcome"
        self.KEY_BATTLE_TRAINER_TOTAL_POKEMON = "battle.opponentA.teamCount"
        self.KEY_BATTLE_PLAYER_MON_PARTY_POS = "battle.player.activePokemon.partyPos"
        self.KEY_BATTLE_PLAYER_MON_HP = "battle.player.activePokemon.stats.hp"

        self.KEY_BATTLE_TRAINER_A_NUMBER = "battle.opponentA.id"
        self.KEY_BATTLE_A_FIRST_ENEMY_SPECIES = "battle.opponentA.activePokemon.species"
        self.KEY_BATTLE_A_FIRST_ENEMY_LEVEL = "battle.opponentA.activePokemon.level"
        self.KEY_BATTLE_A_FIRST_ENEMY_HP = "battle.opponentA.activePokemon.stats.hp"
        self.KEY_BATTLE_A_FIRST_ENEMY_PARTY_POS = "battle.opponentA.activePokemon.partyPos"
        self.KEY_BATTLE_A_SECOND_ENEMY_SPECIES = "battle.opponentA.activePokemon2.species"
        self.KEY_BATTLE_A_SECOND_ENEMY_LEVEL = "battle.opponentA.activePokemon2.level"
        self.KEY_BATTLE_A_SECOND_ENEMY_HP = "battle.opponentA.activePokemon2.stats.hp"
        self.KEY_BATTLE_A_SECOND_ENEMY_PARTY_POS = "battle.opponentA.activePokemon2.partyPos"

        self.KEY_BATTLE_TRAINER_B_NUMBER = "battle.opponentB.id"
        self.KEY_BATTLE_B_FIRST_ENEMY_SPECIES = "battle.opponentB.activePokemon.species"
        self.KEY_BATTLE_B_FIRST_ENEMY_LEVEL = "battle.opponentB.activePokemon.level"
        self.KEY_BATTLE_B_FIRST_ENEMY_HP = "battle.opponentB.activePokemon.stats.hp"
        self.KEY_BATTLE_B_FIRST_ENEMY_PARTY_POS = "battle.opponentB.activePokemon.partyPos"

        self.KEY_ITEM_COUNT = "player.itemCount"
        self.KEY_ITEM_QUANTITY_DECRYPTION_KEY = "bag.quantityDecryptionKey"
        self.ALL_KEYS_ITEM_TYPE = [f"bag.items.{i}.item" for i in range(0, 30)]
        self.ALL_KEYS_ITEM_QUANTITY = [f"bag.items.{i}.quantity" for i in range(0, 30)]
        self.ALL_KEYS_BALL_TYPE = [f"bag.pokeBalls.{i}.item" for i in range(0, 16)]
        self.ALL_KEYS_BALL_QUANTITY = [f"bag.pokeBalls.{i}.quantity" for i in range(0, 16)]
        self.ALL_KEYS_KEY_ITEMS = [f"bag.keyItems.{i}.item" for i in range(0, 30)]

        self.ALL_TM_KEYS = [
            "bag.tmhm.TM01-Focus Punch.quantity",
            "bag.tmhm.TM02-Dragon Claw.quantity",
            "bag.tmhm.TM03-Water Pulse.quantity",
            "bag.tmhm.TM04-Calm Mind.quantity",
            "bag.tmhm.TM05-Roar.quantity",
            "bag.tmhm.TM06-Toxic.quantity",
            "bag.tmhm.TM07-Hail.quantity",
            "bag.tmhm.TM08-Bulk Up.quantity",
            "bag.tmhm.TM09-Bullet Seed.quantity",
            "bag.tmhm.TM10-Hidden Power.quantity",
            "bag.tmhm.TM11-Sunny Day.quantity",
            "bag.tmhm.TM12-Taunt.quantity",
            "bag.tmhm.TM13-Ice Beam.quantity",
            "bag.tmhm.TM14-Blizzard.quantity",
            "bag.tmhm.TM15-Hyper Beam.quantity",
            "bag.tmhm.TM16-Light Screen.quantity",
            "bag.tmhm.TM17-Protect.quantity",
            "bag.tmhm.TM18-Rain Dance.quantity",
            "bag.tmhm.TM19-Giga Drain.quantity",
            "bag.tmhm.TM20-Safeguard.quantity",
            "bag.tmhm.TM21-Frustration.quantity",
            "bag.tmhm.TM22-SolarBeam.quantity",
            "bag.tmhm.TM23-Iron Tail.quantity",
            "bag.tmhm.TM24-Thunderbolt.quantity",
            "bag.tmhm.TM25-Thunder.quantity",
            "bag.tmhm.TM26-Earthquake.quantity",
            "bag.tmhm.TM27-Return.quantity",
            "bag.tmhm.TM28-Dig.quantity",
            "bag.tmhm.TM29-Psychic.quantity",
            "bag.tmhm.TM30-Shadow Ball.quantity",
            "bag.tmhm.TM31-Brick Break.quantity",
            "bag.tmhm.TM32-Double Team.quantity",
            "bag.tmhm.TM33-Reflect.quantity",
            "bag.tmhm.TM34-Shock Wave.quantity",
            "bag.tmhm.TM35-Flamethrower.quantity",
            "bag.tmhm.TM36-Sludge Bomb.quantity",
            "bag.tmhm.TM37-Sandstorm.quantity",
            "bag.tmhm.TM38-Fire Blast.quantity",
            "bag.tmhm.TM39-Rock Tomb.quantity",
            "bag.tmhm.TM40-Aerial Ace.quantity",
            "bag.tmhm.TM41-Torment.quantity",
            "bag.tmhm.TM42-Facade.quantity",
            "bag.tmhm.TM43-Secret Power.quantity",
            "bag.tmhm.TM44-Rest.quantity",
            "bag.tmhm.TM45-Attract.quantity",
            "bag.tmhm.TM46-Thief.quantity",
            "bag.tmhm.TM47-Steel Wing.quantity",
            "bag.tmhm.TM48-Skill Swap.quantity",
            "bag.tmhm.TM49-Snatch.quantity",
            "bag.tmhm.TM50-Overheat.quantity",
        ]

        self.ALL_HM_KEYS = [
            "bag.tmhm.HM01-Cut.quantity",
            "bag.tmhm.HM02-Fly.quantity",
            "bag.tmhm.HM03-Surf.quantity",
            "bag.tmhm.HM04-Strength.quantity",
            "bag.tmhm.HM05-Flash.quantity",
            "bag.tmhm.HM06-Rock Smash.quantity",
            "bag.tmhm.HM07-Waterfall.quantity",
            "bag.tmhm.HM08-Dive.quantity",
        ]

        self.ALL_KEYS_ALL_ITEM_FIELDS = set([self.KEY_ITEM_QUANTITY_DECRYPTION_KEY])
        self.ALL_KEYS_ALL_ITEM_FIELDS.update(self.ALL_KEYS_ITEM_TYPE)
        self.ALL_KEYS_ALL_ITEM_FIELDS.update(self.ALL_KEYS_ITEM_QUANTITY)
        self.ALL_KEYS_ALL_ITEM_FIELDS.update(self.ALL_KEYS_BALL_TYPE)
        self.ALL_KEYS_ALL_ITEM_FIELDS.update(self.ALL_KEYS_BALL_QUANTITY)
        self.ALL_KEYS_ALL_ITEM_FIELDS.update(self.ALL_KEYS_KEY_ITEMS)
        self.ALL_KEYS_ALL_ITEM_FIELDS.update(self.ALL_TM_KEYS)
        self.ALL_KEYS_ALL_ITEM_FIELDS.update(self.ALL_HM_KEYS)

        self.DMA_A_KEYS = set()
        #self.DMA_A_KEYS = set(["bag.items.0.item", "bag.items.1.item", "bag.items.2.item", "bag.items.3.item", "bag.items.4.item"])
        self.DMA_A_KEYS.update(self.ALL_KEYS_ALL_ITEM_FIELDS)

        self.ALL_KEYS_TO_REGISTER = [
            self.KEY_DMA_A,
            self.KEY_DMA_B,
            self.KEY_DMA_C,
            self.KEY_STATE_1,
            self.KEY_STATE_2,
            self.KEY_OVERWORLD_MAP,
            #self.KEY_PLAYER_PLAYERID,
            #self.KEY_PLAYER_MONEY,
            self.KEY_PLAYER_MON_EXPPOINTS,
            self.KEY_PLAYER_MON_LEVEL,
            self.KEY_PLAYER_MON_SPECIES,
            self.KEY_PLAYER_MON_HELD_ITEM,
            self.KEY_GAMETIME_SECONDS,
            self.KEY_BATTLE_FLAG,
            self.KEY_TRAINER_BATTLE_FLAG,
            self.KEY_DOUBLE_BATTLE_FLAG,
            self.KEY_MULTI_BATTLE_FLAG,
            self.KEY_BATTLE_OUTCOME,
            self.KEY_BATTLE_TRAINER_A_NUMBER,
            self.KEY_BATTLE_TRAINER_B_NUMBER,
            self.KEY_BATTLE_PLAYER_MON_HP,
            self.KEY_BATTLE_PLAYER_MON_PARTY_POS,
            self.KEY_BATTLE_A_FIRST_ENEMY_SPECIES,
            self.KEY_BATTLE_A_FIRST_ENEMY_LEVEL,
            self.KEY_BATTLE_A_FIRST_ENEMY_HP,
            self.KEY_BATTLE_A_FIRST_ENEMY_PARTY_POS,
            self.KEY_BATTLE_A_SECOND_ENEMY_SPECIES,
            self.KEY_BATTLE_A_SECOND_ENEMY_LEVEL,
            self.KEY_BATTLE_A_SECOND_ENEMY_HP,
            self.KEY_BATTLE_A_SECOND_ENEMY_PARTY_POS,
            self.KEY_BATTLE_B_FIRST_ENEMY_SPECIES,
            self.KEY_BATTLE_B_FIRST_ENEMY_LEVEL,
            self.KEY_BATTLE_B_FIRST_ENEMY_HP,
            self.KEY_BATTLE_B_FIRST_ENEMY_PARTY_POS,
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
            sanitize_string("ZINC"),
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


gh_gen_three_const = Gen3GameHookConstants()
