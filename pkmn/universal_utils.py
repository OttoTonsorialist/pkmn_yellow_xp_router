
import math
import logging
from pkmn.universal_data_objects import Trainer, TrainerTimingStats

from utils.constants import const

logger = logging.getLogger(__name__)


STAT_MIN = 1
STAT_MAX = 999


def calc_xp_yield(base_yield, level, is_trainer_battle, exp_split=1):
    # NOTE: assumes player's pokemon are not traded
    result = base_yield * level
    result = math.floor(result / 7)
    result = math.floor(result / exp_split)

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
    elif growth_rate == const.GROWTH_RATE_ERRATIC:
        if target_level < 50:
            result = ((target_level ** 3) * (100 - target_level)) / 50
            return math.floor(result)
        elif target_level < 68:
            result = ((target_level ** 3) * (150 - target_level)) / 100
            return math.floor(result)
        elif target_level < 98:
            result = target_level ** 3
            result *= math.floor((1911 - (10 * target_level)) / 3)
            result /= 500
            return math.floor(result)
        else:
            result = ((target_level ** 3) * (160 - target_level)) / 100
            return math.floor(result)
    elif growth_rate == const.GROWTH_RATE_FLUCTUATING:
        if target_level < 15:
            result = target_level ** 3
            partial = math.floor((target_level + 1) / 3)
            result = (result * (partial + 24)) / 50
            return math.floor(result)
        elif target_level < 36:
            result = ((target_level ** 3) * (target_level + 14)) / 50
            return math.floor(result)
        else:
            result = target_level ** 3
            partial = math.floor(target_level / 2)
            result = (result * (partial + 32)) / 50
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
        
        if cur_level == 100:
            return 100, 0

        return cur_level, req_exp - cur_xp

level_lookups = {
    const.GROWTH_RATE_FAST: LevelLookup(const.GROWTH_RATE_FAST),
    const.GROWTH_RATE_MEDIUM_FAST: LevelLookup(const.GROWTH_RATE_MEDIUM_FAST),
    const.GROWTH_RATE_MEDIUM_SLOW: LevelLookup(const.GROWTH_RATE_MEDIUM_SLOW),
    const.GROWTH_RATE_SLOW: LevelLookup(const.GROWTH_RATE_SLOW),
    const.GROWTH_RATE_ERRATIC: LevelLookup(const.GROWTH_RATE_ERRATIC),
    const.GROWTH_RATE_FLUCTUATING: LevelLookup(const.GROWTH_RATE_FLUCTUATING),
}


def experience_per_second(timing_obj:TrainerTimingStats ,trainer_obj:Trainer):
    result = timing_obj.get_optimal_exp_per_second(
        len(trainer_obj.pkmn),
        sum([x.xp for x in trainer_obj.pkmn])
    )
    result = round(result)
    return str(result)
