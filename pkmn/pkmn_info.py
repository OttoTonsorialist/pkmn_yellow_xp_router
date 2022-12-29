
from typing import Dict, Tuple, List
from pkmn import universal_data_objects
from pkmn.damage_calc import DamageRange
from pkmn.pkmn_db import ItemDB, MinBattlesDB, MoveDB, PkmnDB, TrainerDB
from routing import route_state_objects
from route_recording.recorder import RecorderController, RecorderGameHookClient


class CurrentGen:
    def version_name(self) -> str:
        raise NotImplementedError()
    
    def get_generation(self) -> int:
        raise NotImplementedError()
        
    def pkmn_db(self) -> PkmnDB:
        raise NotImplementedError()

    def item_db(self) -> ItemDB:
        raise NotImplementedError()

    def trainer_db(self) -> TrainerDB:
        raise NotImplementedError()
    
    def move_db(self) -> MoveDB:
        raise NotImplementedError()
    
    def min_battles_db(self) -> MinBattlesDB:
        raise NotImplementedError()
    
    def get_recorder_client(self, recorder_controller:RecorderController) -> RecorderGameHookClient:
        raise NotImplementedError()
    
    def create_trainer_pkmn(self, pkmn_name, pkmn_level):
        raise NotImplementedError()

    def create_wild_pkmn(self, pkmn_name, pkmn_level):
        raise NotImplementedError()
    
    def calculate_damage(self,
        attacking_pkmn:universal_data_objects.EnemyPkmn,
        move:universal_data_objects.Move,
        defending_pkmn:universal_data_objects.EnemyPkmn,
        attacking_stage_modifiers:universal_data_objects.StageModifiers=None,
        defending_stage_modifiers:universal_data_objects.StageModifiers=None,
        is_crit:bool=False,
        custom_move_data:str=""
    ) -> DamageRange:
        raise NotImplementedError()

    def get_crit_rate(
        self,
        pkmn:universal_data_objects.EnemyPkmn,
        move:universal_data_objects.Move
    ) -> float:
        raise NotImplementedError()
    
    def make_stat_block(
        self,
        hp,
        attack,
        defense,
        special_attack,
        special_defense,
        speed,
        is_stat_xp=False
    ) -> universal_data_objects.StatBlock:
        raise NotImplementedError()
    
    def make_badge_list(self) -> universal_data_objects.BadgeList:
        raise NotImplementedError()
    
    def make_inventory(self) -> route_state_objects.Inventory:
        raise NotImplementedError()
    
    def get_stat_modifer_moves(self) -> List[str]:
        raise NotImplementedError()
    
    def get_fight_reward(self, trainer_name) -> str:
        raise NotImplementedError()

    def is_minor_fight(self, trainer_name) -> str:
        raise NotImplementedError()

    def is_major_fight(self, trainer_name) -> str:
        raise NotImplementedError()
    
    def get_move_custom_data(self, move_name) -> List[str]:
        raise NotImplementedError()
    
    def get_hidden_power(self, dvs:universal_data_objects.StatBlock) -> Tuple[str, int]:
        raise NotImplementedError()


