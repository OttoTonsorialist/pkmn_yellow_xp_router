import math

from pkmn import universal_data_objects, damage_calc
import pkmn
from utils.constants import const

MIN_RANGE = 217
MAX_RANGE = 255
NUM_ROLLS = MAX_RANGE - MIN_RANGE + 1


def get_crit_rate(pkmn:universal_data_objects.EnemyPkmn, move:universal_data_objects.Move):
    crit_numerator = int(pkmn.base_stats.speed / 2)
    if move.attack_flavor == const.FLAVOR_HIGH_CRIT:
        crit_numerator *= 8
    
    crit_numerator = min(int(crit_numerator), 255)
    result = crit_numerator / 256
    return result


def calculate_damage(
    attacking_pkmn:universal_data_objects.EnemyPkmn,
    move:universal_data_objects.Move,
    defending_pkmn:universal_data_objects.EnemyPkmn,
    attacking_stage_modifiers:universal_data_objects.StageModifiers=None,
    defending_stage_modifiers:universal_data_objects.StageModifiers=None,
    is_crit:bool=False,
    defender_has_light_screen:bool=False,
    defender_has_reflect:bool=False
):
    if move.base_power is None or move.base_power == 0:
        return None
    
    # special move interactions
    if move.attack_flavor == const.FLAVOR_FIXED_DAMAGE:
        return damage_calc.DamageRange({move.base_power: 1})
    elif move.attack_flavor == const.FLAVOR_LEVEL_DAMAGE:
        return damage_calc.DamageRange({attacking_pkmn.level: 1})
    elif move.attack_flavor == const.FLAVOR_PSYWAVE:
        psywave_upper_limit = math.floor(attacking_pkmn.level * 1.5)
        return damage_calc.DamageRange({x:1 for x in range(1, psywave_upper_limit)})
    
    if attacking_stage_modifiers is None:
        attacking_stage_modifiers = universal_data_objects.StageModifiers()
    if defending_stage_modifiers is None:
        defending_stage_modifiers = universal_data_objects.StageModifiers()

    attacking_battle_stats = attacking_pkmn.get_battle_stats(attacking_stage_modifiers, is_crit=is_crit)
    defending_battle_stats = defending_pkmn.get_battle_stats(defending_stage_modifiers, is_crit=is_crit)

    attacking_species = pkmn.current_gen_info().pkmn_db().get_pkmn(attacking_pkmn.name)
    defending_species = pkmn.current_gen_info().pkmn_db().get_pkmn(defending_pkmn.name)
    first_type_effectiveness = const.TYPE_CHART.get(move.move_type).get(defending_species.first_type)
    second_type_effectiveness = None
    if defending_species.first_type != defending_species.second_type:
        second_type_effectiveness = const.TYPE_CHART.get(move.move_type).get(defending_species.second_type)
    
    if first_type_effectiveness == const.IMMUNE or second_type_effectiveness == const.IMMUNE:
        return None
    
    if move.move_type in const.SPECIAL_TYPES:
        attacking_stat = attacking_battle_stats.special_attack
        defending_stat = defending_battle_stats.special_defense
        if defender_has_light_screen and not is_crit:
            doubled_def = True
        else:
            doubled_def = False
    else:
        attacking_stat = attacking_battle_stats.attack
        defending_stat = defending_battle_stats.defense
        if defender_has_reflect and not is_crit:
            doubled_def = True
        else:
            doubled_def = False
    
    if doubled_def:
        defending_stat *= 2
    
    if  move.name == const.EXPLOSION_MOVE_NAME or move.name == const.SELFDESTRUCT_MOVE_NAME:
        defending_stat = max(math.floor(defending_stat / 2), 1)
    
    """
    if attacking_stat > 255 or defending_stat > 255:
        # divide each stat by 4, by using 2 integer divisions by 2
        attacking_stat = math.floor(attacking_stat / 2)
        attacking_stat = math.floor(attacking_stat / 2)

        defending_stat = math.floor(defending_stat / 2)
        defending_stat = math.floor(defending_stat / 2)
    """

    is_stab = (attacking_species.first_type == move.move_type) or (attacking_species.second_type == move.move_type)

    temp = 2 * attacking_pkmn.level
    if is_crit:
        temp *= 2
    temp = math.floor(temp / 5) + 2

    temp *= move.base_power
    temp *= attacking_stat
    temp = math.floor(temp / defending_stat)

    temp = math.floor(temp / 50)
    temp += 2

    stab_bonus = 0
    if is_stab:
        stab_bonus = math.floor(temp / 2)
    
    temp += stab_bonus

    if first_type_effectiveness == const.SUPER_EFFECTIVE:
        temp *= 2
    elif first_type_effectiveness == const.NOT_VERY_EFFECTIVE:
        temp = math.floor(temp / 2)

    if second_type_effectiveness == const.SUPER_EFFECTIVE:
        temp *= 2
    elif second_type_effectiveness == const.NOT_VERY_EFFECTIVE:
        temp = math.floor(temp / 2)
    
    if temp == 0:
        return None

    damage_vals = {}
    for numerator in range(MIN_RANGE, MAX_RANGE + 1):
        cur_damage = max(math.floor((temp * numerator) / MAX_RANGE), 1)

        if cur_damage not in damage_vals:
            damage_vals[cur_damage] = 0
        
        damage_vals[cur_damage] += 1
    
    return damage_calc.DamageRange(damage_vals)
