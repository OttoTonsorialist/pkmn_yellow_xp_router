
import math
import copy

from utils.constants import const


STAT_MIN = 1
STAT_MAX = 999


def calc_xp_yield(base_yield, level, is_trainer_battle):
    # NOTE: assumes single battler, no XP all, player's pokemon are not traded
    result = base_yield * level
    result = math.floor(result / 7)

    if is_trainer_battle:
        result = math.floor((result * 3) / 2)

    return result


def xp_needed_for_level(target_level, growth_rate):
    if growth_rate == const.GROWTH_RATE_FAST:
        result = (4 * (target_level ** 3)) / 5
        return math.floor(result)
    elif growth_rate == const.GROWTH_RATE_MEDIUM_FAST:
        return target_level ** 3
    elif growth_rate == const.GROWTH_RATE_MEDIUM_SLOW:
        result = (6 * (target_level ** 3)) / 5
        result -= 15 * (target_level ** 2)
        result += 100 * target_level
        result -= 140
        return math.floor(result)
    elif growth_rate == const.GROWTH_RATE_SLOW:
        result = (5 * (target_level ** 3)) / 4
        return math.floor(result)

    raise ValueError(f"Unknown growth rate: {growth_rate}")


class LevelLookup:
    def __init__(self, growth_rate):
        self.grow_rate = growth_rate
        self.thresholds = []
        
        for i in range(100):
            self.thresholds.append(xp_needed_for_level(i + 1, self.grow_rate))
    
    def get_xp_for_level(self, target_level):
        if target_level <= 0 or target_level > 100:
            raise ValueError(f"Pkmn cannot be level {target_level}, cannot get XP needed for invalid level")
        return self.thresholds[target_level - 1]
    
    def get_level_info(self, cur_xp):
        did_break = False
        for cur_level, req_exp in enumerate(self.thresholds):
            if cur_xp < req_exp:
                # list indices are 0-index, levels are 1-index
                # so breaking out like this means cur_level is the correct level of the pokemon
                did_break = True
                break
        
        if not did_break:
            cur_level = 100

        return cur_level, req_exp - cur_xp

level_lookups = {
    const.GROWTH_RATE_FAST: LevelLookup(const.GROWTH_RATE_FAST),
    const.GROWTH_RATE_MEDIUM_FAST: LevelLookup(const.GROWTH_RATE_MEDIUM_FAST),
    const.GROWTH_RATE_MEDIUM_SLOW: LevelLookup(const.GROWTH_RATE_MEDIUM_SLOW),
    const.GROWTH_RATE_SLOW: LevelLookup(const.GROWTH_RATE_SLOW),
}