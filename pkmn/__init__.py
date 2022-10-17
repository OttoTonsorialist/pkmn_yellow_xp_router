
from pkmn.gen_factory import current_gen_info, change_version
__all__ = [current_gen_info, change_version]

# actually register the stuff
# Everything imported after this point we'll del to clear the namespace
from pkmn.gen_factory import gen_factory
from utils.constants import const
from pkmn.gen_1 import gen_one_object
from pkmn.gen_2 import gen_two_object

gen_factory.register_gen(gen_one_object.gen_one_red, const.RED_VERSION)
gen_factory.register_gen(gen_one_object.gen_one_blue, const.BLUE_VERSION)
gen_factory.register_gen(gen_one_object.gen_one_yellow, const.YELLOW_VERSION)

gen_factory.register_gen(gen_two_object.gen_two_gold, const.GOLD_VERSION)
gen_factory.register_gen(gen_two_object.gen_two_silver, const.SILVER_VERSION)
gen_factory.register_gen(gen_two_object.gen_two_crystal, const.CRYSTAL_VERSION)

# now clean up the namespace
del gen_factory
del const
del gen_one_object