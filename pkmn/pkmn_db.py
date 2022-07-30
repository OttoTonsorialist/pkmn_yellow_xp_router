import json
import os

from utils.constants import const
import pkmn.data_objects as data_objects
from pkmn import pkmn_utils


class MinBattlesDB:
    def __init__(self):
        self.data = []
        if os.path.exists(const.MIN_BATTLES_DIR):
            for fragment in os.listdir(const.MIN_BATTLES_DIR):
                name, ext = os.path.splitext(fragment)
                if ext != ".json":
                    continue
                self.data.append(name)


class PkmnDB:
    def __init__(self):
        self.data = {}

        with open(const.POKEMON_DB_PATH, 'r') as f:
            raw_db = json.load(f)

        for cur_pkmn in raw_db.values():
            self.data[cur_pkmn[const.NAME_KEY]] = data_objects.PokemonSpecies(cur_pkmn)
    
    def create_wild_pkmn(self, pkmn_name, pkmn_level):
        return data_objects.EnemyPkmn(
            pkmn_utils.instantiate_wild_pokemon(self.data[pkmn_name].to_dict(), pkmn_level),
            self.data[pkmn_name].stats
        )
    
    def get_filtered_names(self, filter_val=None):
        if filter_val is None:
            return list(self.data.keys())
        
        filter_val = filter_val.lower()
        result = [x for x in self.data.keys() if filter_val in x]
        if not result:
            result = [f"{const.NO_POKEMON} match filter: '{filter_val}'"]
        
        return result


class TrainerDB:
    def __init__(self, pkmn_db):
        self.data = {}
        self.loc_oriented_trainers = {}
        self.class_oriented_trainers = {}

        with open(const.TRAINER_DB_PATH, 'r') as f:
            raw_db = json.load(f)

        for raw_trainer in raw_db.values():
            """
            # TODO: currently just blindly ignoring all unused trainers. Not sure if I ever care about that
            if raw_trainer[const.TRAINER_LOC] == const.UNUSED_TRAINER_LOC:
                continue
            """

            trainer_obj = self._create_trainer(raw_trainer, pkmn_db)

            self.data[trainer_obj.name] = trainer_obj

            if trainer_obj.location not in self.loc_oriented_trainers:
                self.loc_oriented_trainers[trainer_obj.location] = []
            self.loc_oriented_trainers[trainer_obj.location].append(trainer_obj.name)

            if trainer_obj.trainer_class not in self.class_oriented_trainers:
                self.class_oriented_trainers[trainer_obj.trainer_class] = []
            self.class_oriented_trainers[trainer_obj.trainer_class].append(trainer_obj.name)
    
    def _create_trainer(self, trainer_dict, pkmn_db):
        return data_objects.Trainer(
            trainer_dict,
            [data_objects.EnemyPkmn(x, pkmn_db.data[x[const.NAME_KEY]].stats) for x in trainer_dict[const.TRAINER_POKEMON]]
        )
    
    def get_all_locations(self):
        result = list(self.loc_oriented_trainers.keys())
        if const.UNUSED_TRAINER_LOC in result:
            result.remove(const.UNUSED_TRAINER_LOC)

        return result
    
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
        for cur_trainer in self.data.values():
            if trainer_class is not None and cur_trainer.trainer_class != trainer_class:
                continue
            if trainer_loc is not None and cur_trainer.location != trainer_loc:
                continue
            elif trainer_loc == const.UNUSED_TRAINER_LOC:
                continue
            elif cur_trainer.name in defeated_trainers:
                continue

            valid_trainers.append(cur_trainer.name)
        
        return valid_trainers


class ItemDB:
    def __init__(self):
        self.data = {}
        self.mart_items = {}
        self.key_items = []
        self.tms = []
        self.other_items = []

        with open(const.ITEM_DB_PATH, 'r') as f:
            raw_db = json.load(f)

        for cur_dict_item in raw_db.values():
            cur_base_item = data_objects.BaseItem(cur_dict_item)
            self.data[cur_base_item.name] = cur_base_item

            if cur_base_item.is_key_item:
                self.key_items.append(cur_base_item.name)
            elif cur_base_item.name.startswith("TM") or cur_base_item.name.startswith("HM"):
                self.tms.append(cur_base_item.name)
            else:
                self.other_items.append(cur_base_item.name)

            for mart in cur_base_item.marts:
                if mart not in self.mart_items:
                    self.mart_items[mart] = []
                self.mart_items[mart].append(cur_base_item.name)
    
    def get_filtered_names(self, item_type=const.ITEM_TYPE_ALL_ITEMS, source_mart=const.ITEM_TYPE_ALL_ITEMS):
        if item_type == const.ITEM_TYPE_ALL_ITEMS and source_mart == const.ITEM_TYPE_ALL_ITEMS:
            return list(self.data.keys())
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


pkmn_db = PkmnDB()
trainer_db = TrainerDB(pkmn_db)
min_battles_db = MinBattlesDB()
item_db = ItemDB()
