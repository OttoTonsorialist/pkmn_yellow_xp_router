import math

from pkmn import universal_data_objects, damage_calc
import pkmn
from utils.constants import const
from pkmn.gen_2.gen_two_constants import gen_two_const

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
    first_type_effectiveness = gen_two_const.TYPE_CHART.get(move.move_type).get(defending_species.first_type)
    second_type_effectiveness = None
    if defending_species.first_type != defending_species.second_type:
        second_type_effectiveness = gen_two_const.TYPE_CHART.get(move.move_type).get(defending_species.second_type)
    
    if first_type_effectiveness == const.IMMUNE or second_type_effectiveness == const.IMMUNE:
        return None
    
    if move.move_type in gen_two_const.SPECIAL_TYPES:
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

    is_stab = (attacking_species.first_type == move.move_type) or (attacking_species.second_type == move.move_type)

    temp = 2 * attacking_pkmn.level
    temp = math.floor(temp / 5) + 2

    temp *= move.base_power
    temp *= attacking_stat
    temp = math.floor(temp / defending_stat)

    temp = math.floor(temp / 50)

    # TODO: Held item boost goes here
    if False:
        temp *= 1.1

    # forcibly prevent crits for Flail, Reversal, and Future sight
    if is_crit and move.name not in [const.FLAIL_MOVE_NAME, const.REVERSAL_MOVE_NAME, const.FUTURE_SIGHT_MOVE_NAME]:
        temp *= 2

    temp += 2
    
    # TODO: weather check goes here
    weather_boost = False
    weather_penalty = False
    
    if weather_boost:
        temp = math.floor(temp * 1.5)
    elif weather_penalty:
        temp = math.floor(temp * 0.5)
    
    # TODO: badge type boost check goes here
    badge_type_boost = False
    if badge_type_boost:
        temp = math.floor(temp * 1.125)

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

    move_modifier = 1

    # TODO: rollout logic goes here
    if False:
        num_rollout_turns = 0
        defense_curl_used = false
        if defense_curl_used:
            num_rollout_turns += 1
        
        move_modifier = math.pow(2, num_rollout_turns)
    # TODO: fury cutter logic goes here
    elif False:
        num_fury_cutter_turns = 0
        move_modifier = math.pow(2, num_fury_cutter_turns)
    # TODO: rage logic goes here
    elif False:
        num_times_hit_during_rage = 0
        move_modifier = num_times_hit_during_rage
    
    temp *= move_modifier

    # TODO: gust/twister + enemy flying logic goes here
    # TODO: earthquake/magnitude + enemy digging logic goes here
    # TODO: stomp + enemy minimized logic goes here
    # TODO: pursuit + enemy switching logic goes here
    double_damage = False

    if double_damage:
        temp *= 2
    
    if temp == 0:
        return None

    damage_vals = {}

    # TODO: flail and reversal don't get randomized
    if False:
        damage_vals[temp] = 1
    else:
        for numerator in range(MIN_RANGE, MAX_RANGE + 1):
            cur_damage = max(math.floor((temp * numerator) / MAX_RANGE), 1)

            if cur_damage not in damage_vals:
                damage_vals[cur_damage] = 0
            
            damage_vals[cur_damage] += 1
    
    return damage_calc.DamageRange(damage_vals)
