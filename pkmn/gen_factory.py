import os
import json
from typing import Dict, List, Tuple
import logging

from utils.constants import const
from pkmn.pkmn_info import CurrentGen

logger = logging.getLogger(__name__)


class GenFactory:
    def __init__(self):
        self._all_gens:Dict[str, CurrentGen] = {}
        self._custom_gens = {}
        self._cur_gen = None
        self._cur_version = None
    
    def register_gen(self, gen:CurrentGen, gen_name:str) -> None:
        if gen_name in self._all_gens:
            raise ValueError(f"Gen already present: {gen_name}")
        self._all_gens[gen_name] = gen
    
    def current_gen_info(self) -> CurrentGen:
        return self._cur_gen
    
    def get_specific_version(self, version_name) -> CurrentGen:
        new_gen = self._all_gens.get(version_name)
        if new_gen is None:
            new_gen = self._custom_gens.get(version_name)
        
        return new_gen
    
    def change_version(self, new_version_name) -> None:
        logger.info(f"Changing to version: {new_version_name}")
        if new_version_name == self._cur_version:
            return
        
        new_gen = self.get_specific_version(new_version_name)
        if new_gen is None:
            raise ValueError(f"Unknown version: {new_version_name}")
        
        self._cur_gen = new_gen
        self._cur_version = new_version_name
    
    def get_gen_names(self, real_gens=True, custom_gens=True) -> List[str]:
        result = []

        if real_gens:
            result.extend([x for x in self._all_gens.keys()])
        if custom_gens:
            result.extend([x for x in self._custom_gens.keys()])

        return result
    
    def reload_all_custom_gens(self):
        # NOTE: assumes all base versions have been registered already
        invalid_custom_gens = []
        self._custom_gens = {}
        for cur_path, cur_base_version, cur_custom_gen_name in self.get_all_custom_gen_info():
            try:
                base_gen = self._all_gens.get(cur_base_version)
                if base_gen == None:
                    raise ValueError(f"Invalid base gen specified: {cur_base_version}")
                self._custom_gens[cur_custom_gen_name] = base_gen.load_custom_gen(
                    cur_custom_gen_name,
                    cur_path
                )

            except Exception as e:
                logger.error(f"Failed to load custom gen with path: {cur_path}")
                logger.exception(e)
                invalid_custom_gens.append((cur_custom_gen_name, str(e)))
        
        if len(invalid_custom_gens) > 0:
            err_msg = "\n".join([f"Custom gen: {x[0]}, error: {x[1]}" for x in invalid_custom_gens])
            raise ValueError(f"Error(s) loading custom gens:\n\n{err_msg}")
    
    def get_all_custom_gen_info(self) -> List[Tuple[str, str, str]]:
        result = []

        if not os.path.exists(const.CUSTOM_GENS_DIR):
            return result

        for custom_gen_folder in os.listdir(const.CUSTOM_GENS_DIR):
            try:
                with open(os.path.join(const.CUSTOM_GENS_DIR, custom_gen_folder, const.CUSTOM_GEN_META_FILE_NAME), 'r') as f:
                    metadata = json.load(f)
                
                cur_custom_gen_name = metadata[const.CUSTOM_GEN_NAME_KEY]
                base_version = metadata[const.BASE_GEN_NAME_KEY]
                result.append(
                    (
                        os.path.join(const.CUSTOM_GENS_DIR, custom_gen_folder), 
                        base_version,
                        cur_custom_gen_name
                    )
                )
            except Exception as e:
                logger.error(f"Failed to load metadata for custom gen with path: {os.path.join(const.CUSTOM_GENS_DIR, custom_gen_folder)}")
                logger.exception(e)
        
        return result


_gen_factory = GenFactory()

#####
# expose interface for easier access
#####
def current_gen_info() -> CurrentGen:
    return _gen_factory.current_gen_info()

def change_version(new_version_name):
    _gen_factory.change_version(new_version_name)

def specific_gen_info(version_name) -> CurrentGen:
    return _gen_factory.get_specific_version(version_name)
