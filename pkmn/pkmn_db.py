import os
from typing import Dict, List, Tuple

from utils.constants import const
from pkmn import universal_data_objects


class MinBattlesDB:
    def __init__(self, path):
        self._path = path
        self.data = []
        if os.path.exists(path):
            for fragment in os.listdir(path):
                name, ext = os.path.splitext(fragment)
                if ext != ".json":
                    continue
                self.data.append(name)
    
    def get_dir(self):
        return self._path


class PkmnDB:
    def __init__(self, data:Dict[str, universal_data_objects.PokemonSpecies]):
        self._data = data
    
    def get_all_names(self) -> List[str]:
        return list(self._data.keys())
    
    def get_pkmn(self, name:str) -> universal_data_objects.PokemonSpecies:
        if name in self._data:
            return self._data.get(name)
        
        for test_name in self.get_all_names():
            if name.lower() == test_name.lower():
                return self._data.get(test_name)
        
        return None
    
    def get_filtered_names(self, filter_val=None) -> List[str]:
        if filter_val is None:
            return self.get_all_names()
        
        filter_val = filter_val.lower()
        result = [x for x in self._data.keys() if filter_val in x.lower()]
        if not result:
            result = [f"No Match: '{filter_val}'"]
        
        return result


class TrainerDB:
    def __init__(self, data:Dict[str, universal_data_objects.Trainer]):
        self._data = data
        self.loc_oriented_trainers:Dict[str, List[str]] = {}
        self.class_oriented_trainers:Dict[str, List[str]] = {}

        for trainer_obj in self._data.values():
            if trainer_obj.location not in self.loc_oriented_trainers:
                self.loc_oriented_trainers[trainer_obj.location] = []
            self.loc_oriented_trainers[trainer_obj.location].append(trainer_obj.name)

            if trainer_obj.trainer_class not in self.class_oriented_trainers:
                self.class_oriented_trainers[trainer_obj.trainer_class] = []
            self.class_oriented_trainers[trainer_obj.trainer_class].append(trainer_obj.name)
    
    def get_trainer(self, trainer_name):
        return self._data.get(trainer_name)
    
    def get_all_locations(self):
        return list(self.loc_oriented_trainers.keys())
    
    def get_all_classes(self):
        return list(self.class_oriented_trainers.keys())
    
    def get_valid_trainers(self, trainer_class=None, trainer_loc=None, defeated_trainers=None):
        if trainer_class == const.ALL_TRAINERS:
            trainer_class = None
        if trainer_loc == const.ALL_TRAINERS:
            trainer_loc = None
        if defeated_trainers is None:
            defeated_trainers = []

        valid_trainers = []
        for cur_trainer in self._data.values():
            if trainer_class is not None and cur_trainer.trainer_class != trainer_class:
                continue
            elif trainer_loc is not None and cur_trainer.location != trainer_loc:
                continue
            elif cur_trainer.name in defeated_trainers:
                continue

            valid_trainers.append(cur_trainer.name)
        
        return valid_trainers


class ItemDB:
    def __init__(self, data:Dict[str, universal_data_objects.BaseItem]):
        self._data = data
        self.mart_items = {}
        self.key_items = []
        self.tms = []
        self.other_items = []

        for cur_base_item in self._data.values():
            other_item = True
            if cur_base_item.is_key_item:
                self.key_items.append(cur_base_item.name)
                other_item = False
            if cur_base_item.name.startswith("TM") or cur_base_item.name.startswith("HM"):
                self.tms.append(cur_base_item.name)
                other_item = False
            if other_item:
                self.other_items.append(cur_base_item.name)

            for mart in cur_base_item.marts:
                if mart not in self.mart_items:
                    self.mart_items[mart] = []
                self.mart_items[mart].append(cur_base_item.name)
    
    def get_item(self, item_name):
        if item_name in self._data:
            return self._data.get(item_name)
        
        for test_name in self._data.keys():
            if item_name.lower() == test_name.lower():
                return self._data.get(test_name)
        
        return self._data.get(item_name)
    
    def get_filtered_names(self, item_type=const.ITEM_TYPE_ALL_ITEMS, source_mart=const.ITEM_TYPE_ALL_ITEMS):
        if item_type == const.ITEM_TYPE_ALL_ITEMS and source_mart == const.ITEM_TYPE_ALL_ITEMS:
            return list(self._data.keys())
        elif item_type == const.ITEM_TYPE_ALL_ITEMS:
            return self.mart_items[source_mart]
        elif source_mart == const.ITEM_TYPE_ALL_ITEMS:
            if item_type == const.ITEM_TYPE_KEY_ITEMS:
                return self.key_items
            elif item_type == const.ITEM_TYPE_TM:
                return self.tms
            else:
                return self.other_items
        else:
            if item_type == const.ITEM_TYPE_KEY_ITEMS:
                result = self.key_items
            elif item_type == const.ITEM_TYPE_TM:
                result = self.tms
            else:
                result = self.other_items
            
            return [x for x in result if x in self.mart_items[source_mart]]


class MoveDB:
    def __init__(self, data:Dict[str, universal_data_objects.Move], stat_mod_moves:Dict[str, List[Tuple[str, int]]]):
        self._data = data
        self.stat_mod_moves = stat_mod_moves
    
    def get_move(self, move_name):
        if move_name in self._data:
            return self._data.get(move_name)
        
        for test_name in self._data.keys():
            if move_name.lower() == test_name.lower():
                return self._data.get(test_name)
        
        return None
    
    def get_stat_mod(self, move_name) -> List[Tuple[str, int]]:
        return self.stat_mod_moves.get(move_name, [])

