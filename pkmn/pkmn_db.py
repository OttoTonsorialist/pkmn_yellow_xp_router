import json

from utils.constants import const
import pkmn.data_objects as data_objects
from pkmn import pkmn_utils


class MinBattlesDB:
    def __init__(self):

        with open(const.MIN_BATTLES_DB_PATH, 'r') as f:
            self.data = json.load(f)


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
            # TODO: currently just blindly ignoring all unused trainers. Not sure if I ever care about that
            if raw_trainer[const.TRAINER_LOC] == const.UNUSED_TRAINER_LOC:
                continue

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


pkmn_db = PkmnDB()
trainer_db = TrainerDB(pkmn_db)
min_battles_db = MinBattlesDB()
