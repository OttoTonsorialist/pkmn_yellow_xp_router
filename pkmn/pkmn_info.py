
from typing import Tuple, List
from pkmn.pkmn_damage_calc import DamageRange
from pkmn.pkmn_db import ItemDB, MinBattlesDB, MoveDB, PkmnDB, TrainerDB


class CurrentGen:
    def pkmn_db() -> PkmnDB:
        raise NotImplementedError()

    def item_db() -> ItemDB:
        raise NotImplementedError()

    def trainer_db() -> TrainerDB:
        raise NotImplementedError()
    
    def move_db() -> MoveDB:
        raise NotImplementedError()
    
    def min_battles_db() -> MinBattlesDB:
        raise NotImplementedError()
    
    def calculate_damage() -> DamageRange:
        raise NotImplementedError()
    
    def find_kill() -> List[Tuple[float, int]]:
        raise NotImplementedError()

    def get_crit_rate() -> float:
        raise NotImplementedError()


class GenFactory:
    def __init__(self):
        raise NotImplementedError()
    
    def current_gen_info() -> CurrentGen:
        raise NotImplementedError()
    
    def change_version(new_version_name) -> None:
        raise NotImplementedError()


gen_factory = GenFactory()

def current_gen_info() -> CurrentGen:
    return gen_factory.current_gen_info()

def change_version(new_version_name):
    gen_factory.change_version(new_version_name)
