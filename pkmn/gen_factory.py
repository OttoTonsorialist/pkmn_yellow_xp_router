
from pkmn.pkmn_info import CurrentGen


class GenFactory:
    def __init__(self):
        self._all_gens = {}
        self._cur_gen = None
        self._cur_version = None
    
    def register_gen(self, gen:CurrentGen, gen_name:str) -> None:
        if gen_name in self._all_gens:
            raise ValueError(f"Gen already present: {gen_name}")
        self._all_gens[gen_name] = gen
    
    def current_gen_info(self) -> CurrentGen:
        return self._cur_gen
    
    def change_version(self, new_version_name) -> None:
        print(f"Changing to version: {new_version_name}")
        if new_version_name == self._cur_version:
            return
        elif new_version_name not in self._all_gens:
            raise ValueError(f"Unknown version: {new_version_name}")
        
        self._cur_gen = self._all_gens[new_version_name]
        self._cur_version = new_version_name

gen_factory = GenFactory()

#####
# expose interface for easier access
#####
def current_gen_info() -> CurrentGen:
    return gen_factory.current_gen_info()

def change_version(new_version_name):
    gen_factory.change_version(new_version_name)
