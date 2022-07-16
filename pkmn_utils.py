import math
import copy

from constants import const

VIT_AMT = 2560
VIT_CAP = 25600
STAT_XP_CAP = 65535


def calc_stat(base_val, level, dv, stat_xp, is_hp=False, is_badge_bosted=False):
    temp = (base_val + dv) * 2
    temp += (math.sqrt(stat_xp) / 4)
    temp = math.floor(temp * level / 100)

    if is_hp:
        return temp + level + 10

    temp += 5
    if is_badge_bosted:
        temp = math.floor(temp * 1.125)

    return temp


def calc_xp_yield(base_yield, level, is_trainer_battle):
    # NOTE: assumes single battler, no XP all, player's pokemon are not traded
    result = base_yield * level
    result = math.floor(result / 7)

    if is_trainer_battle:
        result = math.floor((result * 3) / 2)

    return result


def get_move_list(initial_moves, learned_moves, target_level, special_moves=None):
    result = copy.deepcopy(initial_moves)
    for move_info in learned_moves:
        if move_info[1] in result:
            continue
        if target_level < move_info[0]:
            break
        result.append(move_info[1])
    
    if len(result) > 4:
        result = result[-4:]
    
    if special_moves:
        # pad if necessary so we can just do direct index lookups
        if len(result) < 4:
            result.extend([None] * (4 - len(result)))

        for idx, new_move in enumerate(special_moves):
            if new_move is not None:
                result[idx] = new_move
        
        # remove any leftover padding, if it exists
        result = [x for x in result if x]
    
    return result
    

def instantiate_trainer_pokemon(pkmn_data, target_level, special_moves=None):
    return {
        const.NAME_KEY: pkmn_data[const.NAME_KEY],
        const.LEVEL: target_level,
        const.HP: calc_stat(pkmn_data[const.BASE_HP_KEY], target_level, 8, 0, is_hp=True),
        const.ATK: calc_stat(pkmn_data[const.BASE_ATK_KEY], target_level, 9, 0),
        const.DEF: calc_stat(pkmn_data[const.BASE_DEF_KEY], target_level, 8, 0),
        const.SPD: calc_stat(pkmn_data[const.BASE_SPD_KEY], target_level, 8, 0),
        const.SPC: calc_stat(pkmn_data[const.BASE_SPC_KEY], target_level, 8, 0),
        const.XP: calc_xp_yield(pkmn_data[const.BASE_XP_KEY], target_level, True),
        const.MOVES: get_move_list(pkmn_data, target_level, special_moves=special_moves)
    }


def instantiate_wild_pokemon(pkmn_data, target_level):
    # NOTE: wild pokemon have random DVs. just setting to max to get highest possible stats for now
    return {
        const.NAME_KEY: pkmn_data[const.NAME_KEY],
        const.LEVEL: target_level,
        const.HP: calc_stat(pkmn_data[const.BASE_HP_KEY], target_level, 15, 0, is_hp=True),
        const.ATK: calc_stat(pkmn_data[const.BASE_ATK_KEY], target_level, 15, 0),
        const.DEF: calc_stat(pkmn_data[const.BASE_DEF_KEY], target_level, 15, 0),
        const.SPD: calc_stat(pkmn_data[const.BASE_SPD_KEY], target_level, 15, 0),
        const.SPC: calc_stat(pkmn_data[const.BASE_SPC_KEY], target_level, 15, 0),
        const.XP: calc_xp_yield(pkmn_data[const.BASE_XP_KEY], target_level, False),
        const.MOVES: get_move_list(pkmn_data, target_level)
    }


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