import logging

from utils.constants import const
from utils.io_utils import sanitize_string

logger = logging.getLogger(__name__)


class Gen3GameHookConstants:
    # NOTE: every key defined here is tied to a sepcific version of a GameHook mapper
    # if the keys in the mapper ever change such that they don't match anymore, the whole recorder will start to fail
    def __init__(self):
        self.RESET_FLAG = const.RECORDING_ERROR_FRAGMENT + "FLAG TO SIGNAL GAME RESET. USER SHOULD NEVER SEE THIS"
        self.TRAINER_LOSS_FLAG = const.RECORDING_ERROR_FRAGMENT + "FLAG TO SIGNAL LOSING TO TRAINER. USER SHOULD NEVER SEE THIS"
        self.ROAR_FLAG = const.RECORDING_ERROR_FRAGMENT + "FLAG TO SIGNAL ROARS NEED TO BE HANDLED. USER SHOULD NEVER SEE THIS"
        self.HELD_CHECK_FLAG = const.RECORDING_ERROR_FRAGMENT + "FLAG TO SIGNAL FOR DEEPER HELD ITEM CHECKING. USER SHOULD NEVER SEE THIS"

        self.KEY_DMA_A = "pointers.dma_1"
        self.KEY_DMA_B = "pointers.dma_2"
        self.KEY_DMA_C = "pointers.dma_3"
        self.KEY_OVERWORLD_MAP = "overworld.map_name"
        self.KEY_PLAYER_PLAYERID = "player.player_id"
        self.KEY_PLAYER_MONEY = "bag.money"
        self.KEY_PLAYER_MON_EXPPOINTS = "player.team.0.exp"
        self.KEY_PLAYER_MON_LEVEL = "player.team.0.level"
        self.KEY_PLAYER_MON_SPECIES = "player.team.0.species"
        self.KEY_PLAYER_MON_HELD_ITEM = "player.team.0.held_item"
        self.KEY_PLAYER_MON_FRIENDSHIP = "player.team.0.friendship"

        self.ALL_KEYS_PLAYER_TEAM_SPECIES = [f"player.team.{i}.species" for i in range(0, 6)]
        self.ALL_KEYS_PLAYER_TEAM_LEVEL = [f"player.team.{i}.level" for i in range(0, 6)]
        self.ALL_KEYS_PLAYER_TEAM_IV_ATTACK = [f"player.team.{i}.ivs.attack" for i in range(0, 6)]
        self.ALL_KEYS_PLAYER_TEAM_IV_DEFENSE = [f"player.team.{i}.ivs.defense" for i in range(0, 6)]
        self.ALL_KEYS_PLAYER_TEAM_IV_SPEED = [f"player.team.{i}.ivs.speed" for i in range(0, 6)]
        self.ALL_KEYS_PLAYER_TEAM_IV_SPECIAL_ATTACK = [f"player.team.{i}.ivs.special_attack" for i in range(0, 6)]
        self.ALL_KEYS_PLAYER_TEAM_IV_SPECIAL_DEFENSE = [f"player.team.{i}.ivs.special_defense" for i in range(0, 6)]

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
        self.KEY_PLAYER_MON_STAT_EXP_SPECIAL_ATTACK = "player.team.0.evs.special_attack"
        self.KEY_PLAYER_MON_STAT_EXP_SPECIAL_DEFENSE = "player.team.0.evs.special_defense"
        self.ALL_KEYS_STAT_EXP = [
            self.KEY_PLAYER_MON_STAT_EXP_HP,
            self.KEY_PLAYER_MON_STAT_EXP_ATTACK,
            self.KEY_PLAYER_MON_STAT_EXP_DEFENSE,
            self.KEY_PLAYER_MON_STAT_EXP_SPEED,
            self.KEY_PLAYER_MON_STAT_EXP_SPECIAL_ATTACK,
            self.KEY_PLAYER_MON_STAT_EXP_SPECIAL_DEFENSE,
        ]

        self.KEY_GAMETIME_SECONDS = "game_time.seconds"
        self.KEY_GAMETIME_FRAMES = "game_time.frames"
        self.KEY_BATTLE_FLAG = "battle.flags.is_battle"
        self.KEY_TRAINER_BATTLE_FLAG = "battle.flags.trainer"
        self.KEY_DOUBLE_BATTLE_FLAG = "battle.flags.double"
        self.KEY_TWO_OPPONENTS_BATTLE_FLAG = "battle.flags.two_opponents"
        self.KEY_BATTLE_OUTCOME = "battle.other.battle_outcomes"
        self.KEY_BATTLE_PLAYER_MON_PARTY_POS = "battle.player.party_position"
        self.KEY_BATTLE_PLAYER_MON_HP = "battle.player.active_pokemon.stats.hp"
        self.KEY_BATTLE_ALLY_MON_PARTY_POS = "battle.player.party_position_2"
        self.KEY_BATTLE_ALLY_MON_HP = "battle.player.active_pokemon_2.stats.hp"

        self.KEY_BATTLE_TRAINER_A_NUMBER = "battle.opponent.id"
        self.KEY_BATTLE_TRAINER_B_NUMBER = "battle.opponent_2.id"
        self.KEY_BATTLE_FIRST_ENEMY_SPECIES = "battle.opponent.active_pokemon.species"
        self.KEY_BATTLE_FIRST_ENEMY_LEVEL = "battle.opponent.active_pokemon.level"
        self.KEY_BATTLE_FIRST_ENEMY_HP = "battle.opponent.active_pokemon.stats.hp"
        self.KEY_BATTLE_FIRST_ENEMY_PARTY_POS = "battle.opponent.party_position"
        self.KEY_BATTLE_SECOND_ENEMY_SPECIES = "battle.opponent.active_pokemon_2.species"
        self.KEY_BATTLE_SECOND_ENEMY_LEVEL = "battle.opponent.active_pokemon_2.level"
        self.KEY_BATTLE_SECOND_ENEMY_HP = "battle.opponent.active_pokemon_2.stats.hp"
        self.KEY_BATTLE_SECOND_ENEMY_PARTY_POS = "battle.opponent.party_position_2"

        self.ALL_KEYS_ENEMY_TEAM_SPECIES = [f"battle.opponent.team.{i}.species" for i in range(0, 6)]

        self.KEY_AUDIO_SOUND_EFFECT_1 = "audio.sound_effect_1"
        self.KEY_AUDIO_SOUND_EFFECT_2 = "audio.sound_effect_2"
        # corresponds to 0x088fcdc4 in little endian bytes, or 143642052
        # expect this value to be in soundEffect1
        self.SAVE_SOUND_EFFECT_BYTES_VALUE = [196, 205, 143, 8]
        # corresponds to 0x0890dcc8 in little endian bytes, or 143711432
        # expect this value to be in soundEffect2
        self.HEAL_SOUND_EFFECT_BYTES_VALUE = [200, 220, 144, 8]

        self.KEY_ITEM_QUANTITY_DECRYPTION_KEY = "bag.quantity_decryption_key"
        self.ALL_KEYS_ITEM_TYPE = [f"bag.items.{i}.item" for i in range(0, 30)]
        self.ALL_KEYS_ITEM_QUANTITY = [f"bag.items.{i}.quantity" for i in range(0, 30)]
        self.ALL_KEYS_BALL_TYPE = [f"bag.balls.{i}.item" for i in range(0, 16)]
        self.ALL_KEYS_BALL_QUANTITY = [f"bag.balls.{i}.quantity" for i in range(0, 16)]
        self.ALL_KEYS_BERRY_TYPE = [f"bag.berries.{i}.item" for i in range(0, 46)]
        self.ALL_KEYS_BERRY_QUANTITY = [f"bag.berries.{i}.quantity" for i in range(0, 46)]
        self.ALL_KEYS_KEY_ITEMS = [f"bag.key_items.{i}.item" for i in range(0, 30)]

        self.ALL_KEYS_TMHM_TYPE = [f"bag.tmhm.{i}.item" for i in range(0, 64)]
        self.ALL_KEYS_TMHM_QUANTITY = [f"bag.tmhm.{i}.quantity" for i in range(0, 64)]

        self.ALL_KEYS_ALL_ITEM_FIELDS = set([])
        self.ALL_KEYS_ALL_ITEM_FIELDS.update(self.ALL_KEYS_ITEM_TYPE)
        self.ALL_KEYS_ALL_ITEM_FIELDS.update(self.ALL_KEYS_ITEM_QUANTITY)
        self.ALL_KEYS_ALL_ITEM_FIELDS.update(self.ALL_KEYS_BALL_TYPE)
        self.ALL_KEYS_ALL_ITEM_FIELDS.update(self.ALL_KEYS_BALL_QUANTITY)
        self.ALL_KEYS_ALL_ITEM_FIELDS.update(self.ALL_KEYS_BERRY_TYPE)
        self.ALL_KEYS_ALL_ITEM_FIELDS.update(self.ALL_KEYS_BERRY_QUANTITY)
        self.ALL_KEYS_ALL_ITEM_FIELDS.update(self.ALL_KEYS_KEY_ITEMS)
        self.ALL_KEYS_ALL_ITEM_FIELDS.update(self.ALL_KEYS_TMHM_TYPE)
        self.ALL_KEYS_ALL_ITEM_FIELDS.update(self.ALL_KEYS_TMHM_QUANTITY)

        self.ALL_KEYS_TO_REGISTER = [
            self.KEY_OVERWORLD_MAP,
            self.KEY_PLAYER_PLAYERID,
            self.KEY_PLAYER_MONEY,
            self.KEY_PLAYER_MON_EXPPOINTS,
            self.KEY_PLAYER_MON_LEVEL,
            self.KEY_PLAYER_MON_SPECIES,
            self.KEY_PLAYER_MON_HELD_ITEM,
            self.KEY_GAMETIME_SECONDS,
            self.KEY_BATTLE_FLAG,
            self.KEY_TRAINER_BATTLE_FLAG,
            self.KEY_DOUBLE_BATTLE_FLAG,
            self.KEY_TWO_OPPONENTS_BATTLE_FLAG,
            self.KEY_BATTLE_OUTCOME,
            self.KEY_BATTLE_TRAINER_A_NUMBER,
            self.KEY_BATTLE_TRAINER_B_NUMBER,
            self.KEY_BATTLE_PLAYER_MON_HP,
            self.KEY_BATTLE_PLAYER_MON_PARTY_POS,
            self.KEY_BATTLE_ALLY_MON_HP,
            self.KEY_BATTLE_ALLY_MON_PARTY_POS,
            self.KEY_BATTLE_FIRST_ENEMY_SPECIES,
            self.KEY_BATTLE_FIRST_ENEMY_LEVEL,
            self.KEY_BATTLE_FIRST_ENEMY_HP,
            self.KEY_BATTLE_FIRST_ENEMY_PARTY_POS,
            self.KEY_BATTLE_SECOND_ENEMY_SPECIES,
            self.KEY_BATTLE_SECOND_ENEMY_LEVEL,
            self.KEY_BATTLE_SECOND_ENEMY_HP,
            self.KEY_BATTLE_SECOND_ENEMY_PARTY_POS,
            self.KEY_AUDIO_SOUND_EFFECT_1,
            self.KEY_AUDIO_SOUND_EFFECT_2,
        ]
        self.ALL_KEYS_TO_REGISTER.extend(self.ALL_KEYS_PLAYER_MOVES)
        self.ALL_KEYS_TO_REGISTER.extend(self.ALL_KEYS_STAT_EXP)
        self.ALL_KEYS_TO_REGISTER.extend(self.ALL_KEYS_ALL_ITEM_FIELDS)
        self.ALL_KEYS_TO_REGISTER.extend(self.ALL_KEYS_PLAYER_TEAM_SPECIES)

        # for debugging
        self.ALL_KEYS_TO_REGISTER.extend([self.KEY_DMA_A, self.KEY_DMA_B, self.KEY_DMA_C])


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

    TUTOR_MOVES = set([
        "Body Slam", "Counter", "Double Edge", "Double-Edge", "Dream Eater",
        "Explosion", "Mega Kick", "Mega Punch", "Metronome", "Mimic", "Rock Slide",
        "Seismic Toss", "Softboiled", "Substitute", "Swords Dance", "Thunder Wave",
        "Blast Burn", "Frenzy Plant", "Hydro Cannon",
        "Dynamicpunch", "Dynamic Punch", "Fury Cutter", "Rollout", "Sleep Talk", "Swagger",
        "Defense Curl", "Snore", "Mud Slap", "Swift", "Icy Wind", "Endure", "Psych Up",
        "Ice Punch", "Thunderpunch", "Thunder Punch", "Fire Punch"
    ])
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
        elif gh_move_name == "Rock Smash":
            return "HM06 Rock Smash"
        elif gh_move_name == "Waterfall":
            return "HM07 Waterfall"
        elif gh_move_name == "Dive":
            return "HM08 Dive"
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
    
    def area_name_convert(self, area_name:str):
        area_name = area_name.split("-")[0].strip()

        return area_name


gh_gen_three_const = Gen3GameHookConstants()
