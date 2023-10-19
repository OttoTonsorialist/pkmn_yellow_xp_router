import math
import logging
from typing import Dict, List

from pkmn import universal_data_objects, damage_calc
from pkmn.gen_3.data_objects import GenThreeBadgeList, get_hidden_power_type, get_hidden_power_base_power
from utils.constants import const
from pkmn.gen_3.gen_three_constants import gen_three_const


logger = logging.getLogger(__name__)


MIN_RANGE = 217
MAX_RANGE = 255
NUM_ROLLS = MAX_RANGE - MIN_RANGE + 1


def get_crit_rate(pkmn:universal_data_objects.EnemyPkmn, move:universal_data_objects.Move):
    if const.FLAVOR_HIGH_CRIT in move.attack_flavor:
        return (1/4)
    return (17 / 256)


def calculate_gen_three_damage(
    attacking_pkmn:universal_data_objects.EnemyPkmn,
    attacking_species:universal_data_objects.PokemonSpecies,
    move:universal_data_objects.Move,
    defending_pkmn:universal_data_objects.EnemyPkmn,
    defending_species:universal_data_objects.PokemonSpecies,
    special_types:List[str],
    type_chart:Dict[str, Dict[str, str]],
    held_item_boost_table:Dict[str, str],
    attacking_stage_modifiers:universal_data_objects.StageModifiers=None,
    defending_stage_modifiers:universal_data_objects.StageModifiers=None,
    is_crit:bool=False,
    defender_has_light_screen:bool=False,
    defender_has_reflect:bool=False,
    custom_move_data:str="",
    weather:str=const.WEATHER_NONE,
):
    if move.name == const.HIDDEN_POWER_MOVE_NAME:
        move_type = get_hidden_power_type(attacking_pkmn.dvs)
        base_power = get_hidden_power_base_power(attacking_pkmn.dvs)
    else:
        move_type = move.move_type
        base_power = move.base_power

    if base_power is None or base_power == 0:
        return None
    
    # special move interactions
    if const.FLAVOR_FIXED_DAMAGE in move.attack_flavor:
        return damage_calc.DamageRange({base_power: 1})
    elif const.FLAVOR_LEVEL_DAMAGE in move.attack_flavor:
        return damage_calc.DamageRange({attacking_pkmn.level: 1})
    elif const.FLAVOR_PSYWAVE in move.attack_flavor:
        psywave_upper_limit = math.floor(attacking_pkmn.level * 1.5)
        return damage_calc.DamageRange({x:1 for x in range(1, psywave_upper_limit)})
    
    if attacking_stage_modifiers is None:
        attacking_stage_modifiers = universal_data_objects.StageModifiers()
    if defending_stage_modifiers is None:
        defending_stage_modifiers = universal_data_objects.StageModifiers()

    # for gen two, the "is_crit" flag in the upcoming get_battle_stats call is effectively a flag to ignore badge boosts
    # always calculate badge boosts during a non crit
    # during a crit, if the stage modifiers are in favor of the attack, calculate badge boosts and stage modifiers
    # during a crit, if the stage modifiers are equal or in favor of the defender, calculate stats without any badge boosts and without any stage modifiers
    ignore_badge_boosts = False
    if is_crit:
        if move_type in special_types and attacking_stage_modifiers.special_attack_stage <= defending_stage_modifiers.special_defense_stage:
            # stage modifiers do not favor the attacker for a special move: zero out the stage modifiers
            ignore_badge_boosts = True
            attacking_stage_modifiers = universal_data_objects.StageModifiers()
            defending_stage_modifiers = universal_data_objects.StageModifiers()
        elif move_type not in special_types and attacking_stage_modifiers.attack_stage <= defending_stage_modifiers.defense_stage:
            # stage modifiers do not favor the attacker for a physical move: zero out the stage modifiers
            ignore_badge_boosts = True
            attacking_stage_modifiers = universal_data_objects.StageModifiers()
            defending_stage_modifiers = universal_data_objects.StageModifiers()

    attacking_battle_stats = attacking_pkmn.get_battle_stats(attacking_stage_modifiers, is_crit=ignore_badge_boosts)
    defending_battle_stats = defending_pkmn.get_battle_stats(defending_stage_modifiers, is_crit=ignore_badge_boosts)

    if attacking_pkmn.name == gen_three_const.MAROWAK_NAME and attacking_pkmn.held_item == gen_three_const.THICK_CLUB_NAME:
        attacking_battle_stats.attack *= 2
    elif attacking_pkmn.name == gen_three_const.PIKACHU_NAME and attacking_pkmn.held_item == gen_three_const.LIGHT_BALL_NAME:
        attacking_battle_stats.special_attack *= 2
    elif defending_pkmn.name == gen_three_const.DITTO_NAME and defending_pkmn.held_item == gen_three_const.METAL_POWDER_NAME:
        defending_battle_stats.defense = math.floor(defending_battle_stats.defense * 1.5)
    
    if (
        type_chart.get(move_type).get(defending_species.first_type) == const.IMMUNE or 
        type_chart.get(move_type).get(defending_species.second_type) == const.IMMUNE
    ):
        return None
    
    if move_type in special_types:
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

    is_stab = (attacking_species.first_type == move_type) or (attacking_species.second_type == move_type)
    if move.name == const.FUTURE_SIGHT_MOVE_NAME:
        is_stab = False

    held_item_boost = held_item_boost_table.get(attacking_pkmn.held_item) == move_type

    if move.name == gen_three_const.MAGNITUDE_MOVE_NAME:
        if gen_three_const.MAGNITUDE_4 in custom_move_data:
            base_power = 10
        elif gen_three_const.MAGNITUDE_5 in custom_move_data:
            base_power = 30
        elif gen_three_const.MAGNITUDE_6 in custom_move_data:
            base_power = 50
        elif gen_three_const.MAGNITUDE_7 in custom_move_data:
            base_power = 70
        elif gen_three_const.MAGNITUDE_8 in custom_move_data:
            base_power = 90
        elif gen_three_const.MAGNITUDE_9 in custom_move_data:
            base_power = 110
        elif gen_three_const.MAGNITUDE_10 in custom_move_data:
            base_power = 150
    elif move.name in [const.FLAIL_MOVE_NAME, const.REVERSAL_MOVE_NAME]:
        if gen_three_const.FLAIL_FULL_HP in custom_move_data:
            base_power = 20
        elif gen_three_const.FLAIL_HALF_HP in custom_move_data:
            base_power = 40
        elif gen_three_const.FLAIL_QUARTER_HP in custom_move_data:
            base_power = 80
        elif gen_three_const.FLAIL_TEN_PERCENT_HP in custom_move_data:
            base_power = 100
        elif gen_three_const.FLAIL_FIVE_PERCENT_HP in custom_move_data:
            base_power = 150
        elif gen_three_const.FLAIL_MIN_HP in custom_move_data:
            base_power = 200
    elif move.name == gen_three_const.RETURN_MOVE_NAME:
        try:
            base_power = int(custom_move_data)
        except Exception as e:
            logger.warning(f"Failed to convert return move power to an int: {custom_move_data}")

    # begin actual formula
    temp = 2 * attacking_pkmn.level
    temp = math.floor(temp / 5) + 2

    temp *= base_power
    temp *= attacking_stat
    temp = math.floor(temp / defending_stat)

    temp = math.floor(temp / 50)

    if held_item_boost:
        temp = math.floor(temp * 1.1)

    # forcibly prevent crits for Flail, Reversal, and Future sight
    if is_crit and move.name not in [const.FLAIL_MOVE_NAME, const.REVERSAL_MOVE_NAME, const.FUTURE_SIGHT_MOVE_NAME]:
        temp *= 2

    temp += 2

    weather_boost = False
    weather_penalty = False
    if weather == const.WEATHER_RAIN:
        weather_boost = (move_type == const.TYPE_WATER)
        weather_penalty = (
            move_type == const.TYPE_FIRE or
            move.name == const.SOLAR_BEAM_MOVE_NAME
        )
    elif weather == const.WEATHER_SUN:
        weather_boost = (move_type == const.TYPE_FIRE)
        weather_penalty = (move_type == const.TYPE_WATER)

    
    if weather_boost:
        temp = math.floor(temp * 1.5)
    elif weather_penalty:
        temp = math.floor(temp * 0.5)
    
    stab_bonus = 0
    if is_stab:
        stab_bonus = math.floor(temp / 2)
    
    temp += stab_bonus
    
    # the order type effectiveness gets applied is based on an ordering in an internal table
    # the order is NOT based on which type is "first" or "second" for the defending mon
    # this usually doesn't matter, but there's one specific case where it can
    # specifically, if the move is both super effective and not very effective, the effective power will be neutral
    # but you may lose 1 point of power due to rounding if the division happens first
    for test_type in type_chart.get(move_type):
        if test_type == defending_species.first_type or test_type == defending_species.second_type:
            effectiveness = type_chart.get(move_type).get(test_type)
            if effectiveness == const.SUPER_EFFECTIVE:
                temp *= 2
            elif effectiveness == const.NOT_VERY_EFFECTIVE:
                temp = math.floor(temp / 2)

    move_modifier = 1

    if move.name == gen_three_const.ROLLOUT_MOVE_NAME:
        # ugh, dumb hack. String is either just an int, or the special case of last turn + defense curl
        try:
            num_rollout_turns = int(custom_move_data)
        except ValueError:
            num_rollout_turns = 6
        
        move_modifier = math.pow(2, num_rollout_turns)
    elif move.name == gen_three_const.FURY_CUTTER_MOVE_NAME:
        move_modifier = math.pow(2, int(custom_move_data))
    elif move.name == gen_three_const.RAGE_MOVE_NAME:
        move_modifier = int(custom_move_data)
    elif move.name == gen_three_const.TRIPLE_KICK_MOVE_NAME:
        move_modifier = int(custom_move_data)
    
    temp *= move_modifier

    if move.name in [
        gen_three_const.GUST_MOVE_NAME,
        gen_three_const.TWISTER_MOVE_NAME,
        gen_three_const.EARTHQUAKE_MOVE_NAME,
        gen_three_const.STOMP_MOVE_NAME,
        gen_three_const.PURSUIT_MOVE_NAME,
        gen_three_const.MAGNITUDE_MOVE_NAME,
    ]:
        double_damage = (gen_three_const.NO_BONUS not in custom_move_data)
    else:
        double_damage = False

    if double_damage:
        temp *= 2
    
    if temp <= 0:
        # damage must be at least 1
        temp = 1

    multi_hit_multiplier = 1
    if const.DOUBLE_HIT_FLAVOR in move.attack_flavor:
        multi_hit_multiplier = 2
    elif const.FLAVOR_MULTI_HIT in move.attack_flavor:
        # NOTE: if no custom_move_data is provided, we will only calculate one strike
        # this is intentional
        if const.MULTI_HIT_2 in custom_move_data:
            multi_hit_multiplier = 2
        elif const.MULTI_HIT_3 in custom_move_data:
            multi_hit_multiplier = 3
        elif const.MULTI_HIT_4 in custom_move_data:
            multi_hit_multiplier = 4
        elif const.MULTI_HIT_5 in custom_move_data:
            multi_hit_multiplier = 5

    damage_vals = {}
    if move.name in [const.FLAIL_MOVE_NAME, const.REVERSAL_MOVE_NAME]:
        damage_vals[temp] = 1
        result = damage_calc.DamageRange(damage_vals)
    else:
        for numerator in range(MIN_RANGE, MAX_RANGE + 1):
            cur_damage = max(math.floor((temp * numerator) / MAX_RANGE), 1)

            if cur_damage not in damage_vals:
                damage_vals[cur_damage] = 0
            
            damage_vals[cur_damage] += 1
        
        result = damage_calc.DamageRange(damage_vals)
        if multi_hit_multiplier > 1:
            if is_crit:
                # Currently forcing "crit" calculations to assume only one crit out of all strikes
                # So, when calculating full damage, need to get the damage of a single non-crit strike as well
                # intentionally overwriting custom_move_data to make sure we get the damage of only a single strike
                other_damage = calculate_gen_three_damage(
                    attacking_pkmn,
                    attacking_species,
                    move,
                    defending_pkmn,
                    defending_species,
                    special_types,
                    type_chart,
                    held_item_boost_table,
                    attacking_stage_modifiers,
                    defending_stage_modifiers,
                    defender_has_light_screen=defender_has_light_screen,
                    defender_has_reflect=defender_has_reflect,
                    custom_move_data=""
                )
            else:
                other_damage = result
            
            for _ in range(1, multi_hit_multiplier):
                result = result + other_damage
    
    return result
