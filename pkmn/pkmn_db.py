from __future__ import annotations
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
    
    def validate_moves(self, move_db:MoveDB):
        invalid_mons = []

        for cur_mon in self._data.values():
            for move in cur_mon.initial_moves + cur_mon.tmhm_moves:
                if move_db.get_move(move) == None:
                    invalid_mons.append((cur_mon.name, move))

            for [_, move] in cur_mon.levelup_moves:
                if move_db.get_move(move) == None:
                    invalid_mons.append((cur_mon.name, move))
        
        if len(invalid_mons) > 0:
            raise ValueError(f"Invalid mons detected with unsupported moves: {invalid_mons}")
    
    def validate_types(self, supported_types):
        invalid_mons = []

        for cur_mon in self._data.values():
            if cur_mon.first_type not in supported_types:
                invalid_mons.append((cur_mon.name, cur_mon.first_type))
            if cur_mon.second_type not in supported_types:
                invalid_mons.append((cur_mon.name, cur_mon.second_type))
        
        if len(invalid_mons) > 0:
            raise ValueError(f"Invalid mons detected with unsupported types: {invalid_mons}")
    
    def get_all_names(self) -> List[str]:
        return list(self._data.keys())
    
    def get_pkmn(self, name:str) -> universal_data_objects.PokemonSpecies:
        if name is None:
            return None

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
    
    def validate_trainers(self, pkmn_db:PkmnDB, move_db:MoveDB):
        invalid_trainers = []

        for cur_trainer in self._data.values():
            for cur_mon in cur_trainer.pkmn:
                if pkmn_db.get_pkmn(cur_mon.name) is None:
                    invalid_trainers.append((cur_trainer.name, cur_mon.name))
                
                for cur_move in cur_mon.move_list:
                    if move_db.get_move(cur_move) is None:
                        invalid_trainers.append((cur_trainer.name, cur_mon.name, cur_move))
        
        if len(invalid_trainers) > 0:
            raise ValueError(f"Invalid trainers found with invalid mons/moves: {invalid_trainers}")
    
    def get_trainer(self, trainer_name):
        return self._data.get(trainer_name)
    
    def get_all_locations(self):
        return list(self.loc_oriented_trainers.keys())
    
    def get_all_classes(self):
        return list(self.class_oriented_trainers.keys())
    
    def get_valid_trainers(self, trainer_class=None, trainer_loc=None, defeated_trainers=None, show_rematches=True):
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
            elif not show_rematches and cur_trainer.rematch:
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
    
    def validate_tms_hms(self, move_db:MoveDB):
        invalid_tms_hms = []
        for cur_item_name in self.tms:
            move_name = self.get_item(cur_item_name).move_name
            if move_db.get_move(move_name) is None:
                invalid_tms_hms.append((cur_item_name, move_name))
        
        if len(invalid_tms_hms) > 0:
            raise ValueError(f"Found TM/HM(s) with invalid moves: {invalid_tms_hms}")
    
    def get_item(self, item_name):
        if item_name is None:
            return None

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
    def __init__(self, data:Dict[str, universal_data_objects.Move]):
        self._data = data
        self.stat_mod_moves = {}

        # doing some weird stuff to make sure boosting moves appear at the top
        stat_reduction_moves = {}
        for cur_move in self._data.values():
            cur_stat_mods = []
            is_reduction = False
            for cur_effect in cur_move.effects:
                if const.STAT_KEY in cur_effect and const.MODIFIER_KEY in cur_effect:
                    if cur_effect[const.MODIFIER_KEY] > 0:
                        is_reduction = True
                    
                    cur_stat_mods.append((cur_effect[const.STAT_KEY], cur_effect[const.MODIFIER_KEY]))

            if cur_stat_mods:
                if is_reduction:
                    self.stat_mod_moves[cur_move.name] = cur_stat_mods
                else:
                    stat_reduction_moves[cur_move.name] = cur_stat_mods

        self.stat_mod_moves.update(stat_reduction_moves)
    
    def validate_move_types(self, supported_types):
        invalid_moves = []
        for cur_move in self._data.values():
            if cur_move.move_type not in supported_types:
                invalid_moves.append((cur_move.name, cur_move.move_type))
        
        if len(invalid_moves) > 0:
            raise ValueError(f"Detected moves with invalid types: {invalid_moves}")
    
    def get_move(self, move_name):
        if move_name is None:
            return None

        if move_name in self._data:
            return self._data.get(move_name)
        
        for test_name in self._data.keys():
            if move_name.lower() == test_name.lower():
                return self._data.get(test_name)
        
        return None
    
    def get_filtered_names(self, filter=None):
        if filter is None:
            return list(self._data.keys())
        
        result = []
        filter = filter.lower()
        for test_name in self._data.keys():
            if filter in test_name.lower():
                result.append(test_name)
        
        if len(result) == 0:
            result.append(const.NO_MOVE)
        
        return result
    
    def get_stat_mod(self, move_name) -> List[Tuple[str, int]]:
        return self.stat_mod_moves.get(move_name, [])

