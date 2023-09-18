from __future__ import annotations

from typing import Dict, Tuple, List
from pkmn import universal_data_objects
from pkmn.damage_calc import DamageRange
from pkmn.pkmn_db import ItemDB, MinBattlesDB, MoveDB, PkmnDB, TrainerDB
import routing.state_objects
from route_recording.recorder import RecorderController, RecorderGameHookClient
from utils.constants import const


class CurrentGen:
    def version_name(self) -> str:
        raise NotImplementedError()

    def base_version_name(self) -> str:
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
    
    def create_trainer_pkmn(self, pkmn_name, pkmn_level) -> universal_data_objects.EnemyPkmn:
        raise NotImplementedError()

    def create_wild_pkmn(self, pkmn_name, pkmn_level) -> universal_data_objects.EnemyPkmn:
        raise NotImplementedError()
    
    def calculate_damage(self,
        attacking_pkmn:universal_data_objects.EnemyPkmn,
        move:universal_data_objects.Move,
        defending_pkmn:universal_data_objects.EnemyPkmn,
        attacking_stage_modifiers:universal_data_objects.StageModifiers=None,
        defending_stage_modifiers:universal_data_objects.StageModifiers=None,
        is_crit:bool=False,
        custom_move_data:str="",
        weather:str=const.WEATHER_NONE
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
    
    def make_inventory(self) -> routing.state_objects.Inventory:
        raise NotImplementedError()
    
    def get_stat_modifer_moves(self) -> List[str]:
        raise NotImplementedError()
    
    def get_fight_reward(self, trainer_name) -> str:
        raise NotImplementedError()

    def is_major_fight(self, trainer_name) -> str:
        raise NotImplementedError()
    
    def get_move_custom_data(self, move_name) -> List[str]:
        raise NotImplementedError()
    
    def get_hidden_power(self, dvs:universal_data_objects.StatBlock) -> Tuple[str, int]:
        raise NotImplementedError()

    def get_valid_weather(self) -> List[str]:
        raise NotImplementedError()
    
    def get_stats_boosted_by_vitamin(self, vit_name:str) -> List[str]:
        raise NotImplementedError()
    
    def get_vitamin_amount(self) -> int:
        raise NotImplementedError()
    
    def get_vitamin_cap(self) -> int:
        raise NotImplementedError()
    
    def create_new_custom_gen(self, new_version_name):
        raise NotImplementedError()
    
    def load_custom_gen(self, custom_version_name, root_path) -> CurrentGen:
        raise NotImplementedError()
    
    def get_trainer_timing_info(self) -> universal_data_objects.TrainerTimingStats:
        raise NotImplementedError()

