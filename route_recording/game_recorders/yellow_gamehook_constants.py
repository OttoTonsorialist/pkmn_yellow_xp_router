import logging

from utils.constants import const

logger = logging.getLogger(__name__)


class Gen1GameHookConstants:
    # NOTE: every key defined here is tied to a sepcific version of a GameHook mapper
    # if the keys in the mapper ever change such that they don't match anymore, the whole recorder will start to fail
    def __init__(self):
        self.RESET_FLAG = const.RECORDING_ERROR_FRAGMENT + "FLAG TO SIGNAL GAME RESET. USER SHOULD NEVER SEE THIS"
        self.TRAINER_LOSS_FLAG = const.RECORDING_ERROR_FRAGMENT + "FLAG TO SIGNAL LOSING TO TRAINER. USER SHOULD NEVER SEE THIS"
        self.OAKS_PARCEL = "Oak's Parcel"

        self.KEY_OVERWORLD_MAP = "overworld.map"
        self.KEY_AUDIO_CHANNEL_5 = "audio.channel5"
        self.KEY_PLAYER_PLAYERID = "player.playerId"
        self.KEY_PLAYER_MONEY = "player.money"
        self.KEY_PLAYER_MON_EXPPOINTS = "player.team.0.expPoints"
        self.KEY_PLAYER_MON_LEVEL = "player.team.0.level"
        self.KEY_PLAYER_MON_SPECIES = "player.team.0.species"

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
        self.KEY_BATTLE_TYPE = "battle.type"
        self.KEY_BATTLE_TRAINER_CLASS = "battle.trainer.class"
        self.KEY_BATTLE_TRAINER_NUMBER = "battle.trainer.number"
        self.KEY_BATTLE_PLAYER_MON_SPECIES = "battle.yourPokemon.species"
        self.KEY_BATTLE_PLAYER_MON_HP = "battle.yourPokemon.battleStatHp"
        self.KEY_BATTLE_ENEMY_SPECIES = "battle.enemyPokemon.species"
        self.KEY_BATTLE_ENEMY_LEVEL = "battle.enemyPokemon.level"

        self.KEY_ITEM_COUNT = "player.itemCount"
        self.ALL_KEYS_ITEM_TYPE = [f"player.items.{i}.item" for i in range(0, 20)]
        self.ALL_KEYS_ITEM_QUANTITY = [f"player.items.{i}.quantity" for i in range(0, 20)]

        self.ALL_KEYS_TO_REGISTER = [
            self.KEY_OVERWORLD_MAP,
            self.KEY_AUDIO_CHANNEL_5,
            self.KEY_PLAYER_PLAYERID,
            self.KEY_PLAYER_MONEY,
            self.KEY_PLAYER_MON_EXPPOINTS,
            self.KEY_PLAYER_MON_LEVEL,
            self.KEY_PLAYER_MON_SPECIES,
            self.KEY_GAMETIME_SECONDS,
            self.KEY_BATTLE_TYPE,
            self.KEY_BATTLE_PLAYER_MON_HP,
            self.KEY_BATTLE_ENEMY_SPECIES,
            self.KEY_BATTLE_ENEMY_LEVEL,
            self.KEY_ITEM_COUNT,
        ]
        self.ALL_KEYS_TO_REGISTER.extend(self.ALL_KEYS_PLAYER_MOVES)
        self.ALL_KEYS_TO_REGISTER.extend(self.ALL_KEYS_STAT_EXP)
        self.ALL_KEYS_TO_REGISTER.extend(self.ALL_KEYS_ITEM_TYPE)
        self.ALL_KEYS_TO_REGISTER.extend(self.ALL_KEYS_ITEM_QUANTITY)

        self.TRAINER_BATTLE_TYPE = "Trainer"
        self.WILD_BATTLE_TYPE = "Wild"
        self.NONE_BATTLE_TYPE = "None"
        self.END_OF_ITEM_LIST = "--End of list--"

        self.MAP_GAME_CORNER = "Celadon City - Game Corner"


class GameHookConstantConverter:
    def __init__(self):
        self._game_vitamins = [
            "HP UP",
            "PROTEIN",
            "IRON",
            "CARBOS",
            "CALCIUM",
        ]
        self._game_rare_candy = "RARE CANDY"
    
    def is_game_vitamin(self, item_name):
        return item_name in self._game_vitamins
    
    def is_game_rare_candy(self, item_name):
        return item_name == self._game_rare_candy
    
    def is_game_tm(self, item_name):
        return item_name.startswith("TM")
    
    def _name_prettify(self, item_name:str):
        return " ".join([x.capitalize() for x in item_name.lower().split(" ")])
    
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
        return None
    
    def item_name_convert(self, gh_item_name:str):
        if gh_item_name is None:
            return None
        converted_name:str = self._name_prettify(gh_item_name.replace("é", "e"))
        if converted_name.startswith("Tm"):
            converted_name = "TM" + converted_name[2:]
        if converted_name.startswith("Hm"):
            converted_name = "HM" + converted_name[2:]

        if converted_name.startswith("HM") or converted_name.startswith("TM"):
            [tm_id, move_name] = converted_name.split(":")
            move_name = self.move_name_convert(move_name.strip())
            converted_name = " ".join([tm_id, move_name])
        elif converted_name == "Thunderstone":
            converted_name = "Thunder Stone"
        elif converted_name == "Hp Up":
            converted_name = "HP Up"
        elif converted_name == "Pp Up":
            converted_name = "PP Up"
        elif converted_name == "Guard Spec.":
            converted_name = "Guard Spec"
        elif converted_name == "S.s.ticket":
            converted_name = "SS Anne Ticket"

        return converted_name
    
    def move_name_convert(self, gh_move_name:str):
        if gh_move_name is None:
            return None
        converted_name:str = self._name_prettify(gh_move_name.replace("-", " "))

        if converted_name == "Thunderpunch":
            converted_name = "ThunderPunch"
        elif converted_name == "Sonicboom":
            converted_name = "SonicBoom"
        elif converted_name == "Bubblebeam":
            converted_name = "BubbleBeam"
        elif converted_name == "Solarbeam":
            converted_name = "Solar Beam"
        elif converted_name == "Poisonpowder":
            converted_name = "PoisonPowder"

        return converted_name
    
    def pkmn_name_convert(self, gh_pkmn_name:str):
        if gh_pkmn_name is None:
            return None
        converted_name = gh_pkmn_name

        if converted_name == "NidoranM":
            converted_name = "Nidoran_M"
        elif converted_name == "NidoranF":
            converted_name = "Nidoran_F"
        elif converted_name == "Mr. Mime":
            converted_name = "Mr_Mime"
        elif converted_name == "Farfetch'd":
            converted_name = "Farfetchd"

        return converted_name
    
    def _trainer_class_convert(self, gh_trainer_class:str):
        if gh_trainer_class is None:
            return None
        converted_name:str = self._name_prettify(gh_trainer_class).replace(" ", "")

        if converted_name == "Lt.surge":
            converted_name = "LtSurge"
        
        return converted_name

    def trainer_name_convert(self, trainer_class:str, trainer_num:int, overworld_map:str):
        trainer_class = self._trainer_class_convert(trainer_class)

        converted_name = f"{trainer_class} {trainer_num}"
        if converted_name == "JrTrainerM 2" and overworld_map == "Route 25":
            converted_name += " Duplicate"
        elif converted_name == "Hiker 11" and overworld_map.startswith("Rock Tunnel"):
            converted_name += " Duplicate"
        elif converted_name == "Scientist 4" and overworld_map.startswith("Cinnabar Mansion"):
            converted_name += " Duplicate"
        elif converted_name == "Gentleman 3" and overworld_map == "Vermilion City - Gym":
            converted_name += " Duplicate"
        elif converted_name == "Rival2 2":
            converted_name = "Rival2 2 Jolteon"
        elif converted_name == "Rival2 3":
            converted_name = "Rival2 2 Flareon"
        elif converted_name == "Rival2 4":
            converted_name = "Rival2 2 Vaporeon"
        elif converted_name == "Rival2 5":
            converted_name = "Rival2 3 Jolteon"
        elif converted_name == "Rival2 6":
            converted_name = "Rival2 3 Flareon"
        elif converted_name == "Rival2 7":
            converted_name = "Rival2 3 Vaporeon"
        elif converted_name == "Rival2 8":
            converted_name = "Rival2 4 Jolteon"
        elif converted_name == "Rival2 9":
            converted_name = "Rival2 4 Flareon"
        elif converted_name == "Rival2 10":
            converted_name = "Rival2 4 Vaporeon"
        elif converted_name == "Rival3 1":
            converted_name = "Rival3 Jolteon"
        elif converted_name == "Rival3 2":
            converted_name = "Rival3 Flareon"
        elif converted_name == "Rival3 3":
            converted_name = "Rival3 Vaporeon"
        elif converted_name == "Rocket 42":
            converted_name = "Jessie & James 1"
        elif converted_name == "Rocket 43":
            converted_name = "Jessie & James 2"
        elif converted_name == "Rocket 44":
            converted_name = "Jessie & James 3"
        elif converted_name == "Rocket 45":
            converted_name = "Jessie & James 4"
        
        return converted_name
    
    def area_name_convert(self, area_name:str):
        area_name = area_name.split("-")[0].strip()

        if area_name == "Vermilion Dock":
            area_name = "Vermilion City"
        elif area_name == "Bill's House":
            area_name = "Route 25"
        elif area_name.startswith("Rock Tunnel"):
            area_name ="Rock Tunnel"
        elif area_name.startswith("Safari Zone"):
            area_name ="Safari Zone"
        elif area_name == "Lorelei's Room":
            area_name = "Indigo Plateau"
        elif area_name == "Bruno's Room":
            area_name = "Indigo Plateau"
        elif area_name == "Agatha's Room":
            area_name = "Indigo Plateau"
        elif area_name == "Lance's Room":
            area_name = "Indigo Plateau"
        elif area_name == "Champions Room":
            area_name = "Indigo Plateau"
        
        return area_name


gh_gen_one_const = Gen1GameHookConstants()
gh_converter = GameHookConstantConverter()



