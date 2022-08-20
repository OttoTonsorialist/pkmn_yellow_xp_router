import json
import os

from utils.constants import const
import pkmn.data_objects as data_objects
from pkmn import pkmn_utils


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


class PkmnDB:
    def __init__(self, path):
        self._path = path
        self._data = {}

        with open(path, 'r') as f:
            raw_db = json.load(f)

        for cur_pkmn in raw_db.values():
            self._data[cur_pkmn[const.NAME_KEY]] = data_objects.PokemonSpecies(cur_pkmn)
    
    def get_all_names(self):
        return list(self._data.keys())
    
    def get_pkmn(self, name):
        if name in self._data:
            return self._data.get(name)
        
        for test_name in self.get_all_names():
            if name.lower() == test_name.lower():
                return self._data.get(test_name)
        
        return None
    
    def create_wild_pkmn(self, pkmn_name, pkmn_level):
        raw_pkmn = self.get_pkmn(pkmn_name)
        return data_objects.EnemyPkmn(
            pkmn_utils.instantiate_wild_pokemon(raw_pkmn.to_dict(), pkmn_level),
            raw_pkmn.stats
        )
    
    def get_filtered_names(self, filter_val=None):
        if filter_val is None:
            return self.get_all_names()
        
        filter_val = filter_val.lower()
        result = [x for x in self._data.keys() if filter_val in x.lower()]
        if not result:
            result = [f"No Match: '{filter_val}'"]
        
        return result


class TrainerDB:
    def __init__(self, path, pkmn_db):
        self._path = path
        self._data = {}
        self.loc_oriented_trainers = {}
        self.class_oriented_trainers = {}

        with open(path, 'r') as f:
            raw_db = json.load(f)

        for raw_trainer in raw_db.values():
            # TODO: currently just blindly ignoring all unused trainers. Not sure if I ever care about that
            if raw_trainer[const.TRAINER_LOC] == const.UNUSED_TRAINER_LOC:
                continue

            trainer_obj = self._create_trainer(raw_trainer, pkmn_db)

            self._data[trainer_obj.name] = trainer_obj

            if trainer_obj.location not in self.loc_oriented_trainers:
                self.loc_oriented_trainers[trainer_obj.location] = []
            self.loc_oriented_trainers[trainer_obj.location].append(trainer_obj.name)

            if trainer_obj.trainer_class not in self.class_oriented_trainers:
                self.class_oriented_trainers[trainer_obj.trainer_class] = []
            self.class_oriented_trainers[trainer_obj.trainer_class].append(trainer_obj.name)
    
    def _create_trainer(self, trainer_dict, pkmn_db):
        return data_objects.Trainer(
            trainer_dict,
            [data_objects.EnemyPkmn(x, pkmn_db.get_pkmn(x[const.NAME_KEY]).stats) for x in trainer_dict[const.TRAINER_POKEMON]]
        )
    
    def get_trainer(self, trainer_name):
        return self._data.get(trainer_name)
    
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
        for cur_trainer in self._data.values():
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
        self._data = {}
        self.mart_items = {}
        self.key_items = []
        self.tms = []
        self.other_items = []

        with open(const.ITEM_DB_PATH, 'r') as f:
            raw_db = json.load(f)

        for cur_dict_item in raw_db.values():
            cur_base_item = data_objects.BaseItem(cur_dict_item)
            self._data[cur_base_item.name] = cur_base_item

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


item_db = ItemDB()
pkmn_db:PkmnDB = None
trainer_db:TrainerDB = None
min_battles_db:MinBattlesDB = None
cur_version = None

def change_version(new_version):
    global cur_version
    if cur_version == new_version:
        return
    
    cur_version = new_version
    global pkmn_db
    global trainer_db
    global min_battles_db

    if cur_version == const.YELLOW_VERSION:
        pkmn_db = PkmnDB(const.YELLOW_POKEMON_DB_PATH)
        trainer_db = TrainerDB(const.YELLOW_TRAINER_DB_PATH, pkmn_db)
        min_battles_db = MinBattlesDB(const.YELLOW_MIN_BATTLES_DIR)
    elif cur_version == const.RED_VERSION or cur_version == const.BLUE_VERSION:
        pkmn_db = PkmnDB(const.RB_POKEMON_DB_PATH)
        trainer_db = TrainerDB(const.RB_TRAINER_DB_PATH, pkmn_db)
        min_battles_db = MinBattlesDB(const.RB_MIN_BATTLES_DIR)
    else:
        raise ValueError(f"Unknown Pkmn Game version: {cur_version}")


def get_min_battles_dir(version):
    if version == const.YELLOW_VERSION:
        return const.YELLOW_MIN_BATTLES_DIR
    elif version == const.RED_VERSION or version == const.BLUE_VERSION:
        return const.RB_MIN_BATTLES_DIR
    else:
        raise ValueError(f"Unknown Pkmn Game version: {cur_version}")
    


