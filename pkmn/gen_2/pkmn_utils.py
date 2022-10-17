import math
import copy
from pkmn.gen_2.data_objects import GenTwoStatBlock
from pkmn.universal_data_objects import EnemyPkmn, PokemonSpecies

from utils.constants import const
from pkmn import universal_utils

VIT_AMT = 2560
VIT_CAP = 25600
STAT_XP_CAP = 65535

STAT_MIN = 1
STAT_MAX = 999
BASE_STAGE_INDEX = 6
STAGE_MOFIDIERS = [
    (25, 100),
    (28, 100),
    (33, 100),
    (40, 100),
    (50, 100),
    (66, 100),
    (1, 1),
    (15, 10),
    (2, 1),
    (25, 10),
    (3, 1),
    (35, 10),
    (4, 1),
]


def calc_battle_stat(base_val, level, dv, stat_xp, stage, is_badge_boosted=False):
    """
    Fully recalculates a stat that has been modified by a stage modifier. This is the
    primary function that should be used when a pokemon's stat's stage has changed, 
    and needs to be recalculated
    """
    result = calc_unboosted_stat(base_val, level, dv, stat_xp)

    result = modify_stat_by_stage(result, stage)

    if is_badge_boosted:
        result = badge_boost_single_stat(result)
    
    return result


def modify_stat_by_stage(raw_stat, stage):
    """
    Helper function for the stage modifier math
    """
    if stage == 0:
        return raw_stat

    try:
        cur_stage = STAGE_MOFIDIERS[BASE_STAGE_INDEX + stage]
    except Exception:
        raise ValueError(f"Invalid stage modifier: {stage}")


    return int(math.floor((raw_stat * cur_stage[0]) / cur_stage[1]))


def get_to_hit(base_acc, ev_stage, acc_stage):
    """
    Returns the number (1-255) to check a random number against

    NOTE: This is the "normal" case ONLY!  Assuming immunities, fly/dig invlun status, and guaranteed misses/hits
    have already been handled already. Also does not handle special AI status failure chance
    """
    # base_acc is a number, 0-100, of the percent accuracy
    result = math.floor((base_acc * 255) / 100)

    # first, penalize for lowered accuracy (accuracy must have a negative stage, but it just uses the same boost table as other stats)
    result = modify_stat_by_stage(result, acc_stage)

    # reverse evasion to a penalty (evasion must have a positive stage, but it just uses the same boost table as other stats)
    result = modify_stat_by_stage(result, -1 * ev_stage)

    # clamp to valid values, just in case
    result = min(result, 255)
    result = max(result, 1)

    return result


def calc_unboosted_stat(base_val, level, dv, stat_xp, is_hp=False):
    temp = (base_val + dv) * 2
    temp += math.floor(math.ceil(math.sqrt(stat_xp)) / 4)
    temp = math.floor(temp * level / 100)

    if is_hp:
        return temp + level + 10

    return temp + 5

def calc_stat(base_val, level, dv, stat_xp, is_hp=False, is_badge_bosted=False):
    result = calc_unboosted_stat(base_val, level, dv, stat_xp, is_hp=is_hp)

    if is_badge_bosted:
        result = badge_boost_single_stat(result)

    return result


def badge_boost_single_stat(cur_stat_val):
    # very basic function, just giving it a name so it's obvious when using the function
    return math.floor(cur_stat_val * 1.125)


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
    

def instantiate_trainer_pokemon(pkmn_data:PokemonSpecies, target_level, special_moves=None) -> EnemyPkmn:
    return EnemyPkmn(
        pkmn_data.name,
        target_level,
        universal_utils.calc_xp_yield(pkmn_data.base_xp, target_level, True),
        get_move_list(pkmn_data.initial_moves, pkmn_data.levelup_moves, target_level, special_moves=special_moves),
        GenTwoStatBlock(
            calc_stat(pkmn_data.stats.hp, target_level, 8, 0, is_hp=True),
            calc_stat(pkmn_data.stats.attack, target_level, 9, 0),
            calc_stat(pkmn_data.stats.defense, target_level, 8, 0),
            calc_stat(pkmn_data.stats.special_attack, target_level, 8, 0),
            calc_stat(pkmn_data.stats.special_defense, target_level, 8, 0),
            calc_stat(pkmn_data.stats.speed, target_level, 8, 0),
        ),
        pkmn_data.stats,
        GenTwoStatBlock(8, 9, 8, 8, 8, 8),
        GenTwoStatBlock(0, 0, 0, 0, 0, 0),
        None
    )


def instantiate_wild_pokemon(pkmn_data:PokemonSpecies, target_level) -> EnemyPkmn:
    # NOTE: wild pokemon have random DVs. just setting to max to get highest possible stats for now
    return EnemyPkmn(
        pkmn_data.name,
        target_level,
        universal_utils.calc_xp_yield(pkmn_data.base_xp, target_level, False),
        get_move_list(pkmn_data.initial_moves, pkmn_data.levelup_moves, target_level),
        GenTwoStatBlock(
            calc_stat(pkmn_data.stats.hp, target_level, 15, 0, is_hp=True),
            calc_stat(pkmn_data.stats.attack, target_level, 15, 0),
            calc_stat(pkmn_data.stats.defense, target_level, 15, 0),
            calc_stat(pkmn_data.stats.special_attack, target_level, 15, 0),
            calc_stat(pkmn_data.stats.special_defense, target_level, 15, 0),
            calc_stat(pkmn_data.stats.speed, target_level, 15, 0),
        ),
        pkmn_data.stats,
        GenTwoStatBlock(15, 15, 15, 15, 15, 15),
        GenTwoStatBlock(0, 0, 0, 0, 0, 0),
        None
    )
