import math

from pkmn import universal_data_objects, damage_calc
import pkmn
from pkmn.gen_2.data_objects import GenTwoBadgeList
from utils.constants import const
from pkmn.gen_2.gen_two_constants import gen_two_const

MIN_RANGE = 217
MAX_RANGE = 255
NUM_ROLLS = MAX_RANGE - MIN_RANGE + 1


def get_crit_rate(pkmn:universal_data_objects.EnemyPkmn, move:universal_data_objects.Move):
    if const.FLAVOR_HIGH_CRIT in move.attack_flavor:
        return (1/4)
    return (17 / 256)


def calculate_damage(
    attacking_pkmn:universal_data_objects.EnemyPkmn,
    move:universal_data_objects.Move,
    defending_pkmn:universal_data_objects.EnemyPkmn,
    attacking_stage_modifiers:universal_data_objects.StageModifiers=None,
    defending_stage_modifiers:universal_data_objects.StageModifiers=None,
    is_crit:bool=False,
    defender_has_light_screen:bool=False,
    defender_has_reflect:bool=False,
    custom_move_data:str=""
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
    if move.name == const.FUTURE_SIGHT_MOVE_NAME:
        is_stab = False

    held_item_boost = gen_two_const.HELD_ITEM_BOOSTS.get(attacking_pkmn.held_item) == move.move_type

    badges:GenTwoBadgeList = attacking_pkmn.badges

    if badges is None:
        badge_type_boost = False
    elif move.move_type == const.TYPE_FLYING and badges.zephyr:
        badge_type_boost = True
    elif move.move_type == const.TYPE_BUG and badges.hive:
        badge_type_boost = True
    elif move.move_type == const.TYPE_NORMAL and badges.plain:
        badge_type_boost = True
    elif move.move_type == const.TYPE_GHOST and badges.fog:
        badge_type_boost = True
    elif move.move_type == const.TYPE_FIGHTING and badges.storm:
        badge_type_boost = True
    elif move.move_type == const.TYPE_STEEL and badges.mineral:
        badge_type_boost = True
    elif move.move_type == const.TYPE_ICE and badges.glacier:
        badge_type_boost = True
    elif move.move_type == const.TYPE_DRAGON and badges.rising:
        badge_type_boost = True
    elif move.move_type == const.TYPE_ROCK and badges.boulder:
        badge_type_boost = True
    elif move.move_type == const.TYPE_WATER and badges.cascade:
        badge_type_boost = True
    elif move.move_type == const.TYPE_ELECTRIC and badges.thunder:
        badge_type_boost = True
    elif move.move_type == const.TYPE_GRASS and badges.rainbow:
        badge_type_boost = True
    elif move.move_type == const.TYPE_PSYCHIC and badges.marsh:
        badge_type_boost = True
    elif move.move_type == const.TYPE_FIGHTING and badges.volcano:
        badge_type_boost = True
    elif move.move_type == const.TYPE_GROUND and badges.earth:
        badge_type_boost = True
    else:
        badge_type_boost = False
    
    base_power = move.base_power
    if move.name == gen_two_const.MAGNITUDE_MOVE_NAME:
        if gen_two_const.MAGNITUDE_4 in custom_move_data:
            base_power = 10
        elif gen_two_const.MAGNITUDE_5 in custom_move_data:
            base_power = 30
        elif gen_two_const.MAGNITUDE_6 in custom_move_data:
            base_power = 50
        elif gen_two_const.MAGNITUDE_7 in custom_move_data:
            base_power = 70
        elif gen_two_const.MAGNITUDE_8 in custom_move_data:
            base_power = 90
        elif gen_two_const.MAGNITUDE_9 in custom_move_data:
            base_power = 110
        elif gen_two_const.MAGNITUDE_10 in custom_move_data:
            base_power = 150
    elif move.name in [const.FLAIL_MOVE_NAME, const.REVERSAL_MOVE_NAME]:
        if gen_two_const.FLAIL_FULL_HP in custom_move_data:
            base_power = 20
        elif gen_two_const.FLAIL_HALF_HP in custom_move_data:
            base_power = 40
        elif gen_two_const.FLAIL_QUARTER_HP in custom_move_data:
            base_power = 80
        elif gen_two_const.FLAIL_TEN_PERCENT_HP in custom_move_data:
            base_power = 100
        elif gen_two_const.FLAIL_FIVE_PERCENT_HP in custom_move_data:
            base_power = 150
        elif gen_two_const.FLAIL_MIN_HP in custom_move_data:
            base_power = 200

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
    
    # TODO: weather check goes here
    weather_boost = False
    weather_penalty = False
    
    if weather_boost:
        temp = math.floor(temp * 1.5)
    elif weather_penalty:
        temp = math.floor(temp * 0.5)
    
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

    if move.name == gen_two_const.ROLLOUT_MOVE_NAME:
        # ugh, dumb hack. String is either just an int, or the special case of last turn + defense curl
        try:
            num_rollout_turns = int(custom_move_data)
        except ValueError:
            num_rollout_turns = 6
        
        move_modifier = math.pow(2, num_rollout_turns)
    elif move.name == gen_two_const.FURY_CUTTER_MOVE_NAME:
        move_modifier = math.pow(2, int(custom_move_data))
    elif move.name == gen_two_const.RAGE_MOVE_NAME:
        move_modifier = int(custom_move_data)
    elif move.name == gen_two_const.TRIPLE_KICK_MOVE_NAME:
        move_modifier = int(custom_move_data)
    
    temp *= move_modifier

    if move.name in [
        gen_two_const.GUST_MOVE_NAME,
        gen_two_const.TWISTER_MOVE_NAME,
        gen_two_const.EARTHQUAKE_MOVE_NAME,
        gen_two_const.STOMP_MOVE_NAME,
        gen_two_const.PURSUIT_MOVE_NAME,
        gen_two_const.MAGNITUDE_MOVE_NAME,
    ]:
        double_damage = (gen_two_const.NO_BONUS not in custom_move_data)
    else:
        double_damage = False

    if double_damage:
        temp *= 2
    
    if temp == 0:
        return None

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
                other_damage = calculate_damage(
                    attacking_pkmn,
                    move,
                    defending_pkmn,
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
