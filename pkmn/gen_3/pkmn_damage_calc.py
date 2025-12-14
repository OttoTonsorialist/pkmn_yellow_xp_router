import math
import logging
from typing import Dict, List

from pkmn import universal_data_objects, damage_calc
from pkmn.gen_3.data_objects import GenThreeBadgeList, get_hidden_power_type, get_hidden_power_base_power
from utils.constants import const
from pkmn.gen_3.gen_three_constants import gen_three_const


logger = logging.getLogger(__name__)


MIN_RANGE = 85
MAX_RANGE = 100
NUM_ROLLS = MAX_RANGE - MIN_RANGE + 1


def get_crit_rate(pkmn:universal_data_objects.EnemyPkmn, move:universal_data_objects.Move, custom_move_data:str):
    if const.FLAVOR_HIGH_CRIT in move.attack_flavor:
        return (1/4)
    elif move.name == gen_three_const.NATURE_POWER_MOVE_NAME and custom_move_data == gen_three_const.LONG_GRASS_TERRAIN:
        return (1/4)
    return (1/16)


def get_move_accuracy(pkmn:universal_data_objects.EnemyPkmn, move:universal_data_objects.Move, custom_move_data:str, defending_pkmn:universal_data_objects.EnemyPkmn, weather:str, special_types:List[str]):
    if move.name == gen_three_const.NATURE_POWER_MOVE_NAME:
        if custom_move_data == gen_three_const.TALL_GRASS_TERRAIN:
            result = 75
        elif custom_move_data == gen_three_const.LONG_GRASS_TERRAIN:
            result = 95
        elif custom_move_data == gen_three_const.UNDERWATER_TERRAIN:
            result = 80
        elif custom_move_data == gen_three_const.PLAIN_TERRAIN:
            result = None
        result = 100
    else:
        result = move.accuracy
    
    if result is None:
        return None
    
    if pkmn.ability == gen_three_const.COMPOUND_EYES_ABILITY:
        result = min(
            math.floor(result * 1.3),
            100
        )
    elif pkmn.ability == gen_three_const.HUSTLE_ABILITY:
        is_physical = False
        if move.name == gen_three_const.NATURE_POWER_MOVE_NAME:
            is_physical = custom_move_data in [gen_three_const.PLAIN_TERRAIN, gen_three_const.SAND_TERRAIN, gen_three_const.CAVE_TERRAIN, gen_three_const.ROCK_TERRAIN]
        elif move.move_type not in special_types:
            is_physical = True

        if is_physical:
            result = math.floor(result * 3277 / 4096)
    
    if defending_pkmn.ability == gen_three_const.SAND_VEIL_ABILITY and weather == const.WEATHER_SANDSTORM:
        result = math.floor(result * 3277 / 4096)

    return result


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
    is_double_battle:bool=False
):
    if move.name == const.HIDDEN_POWER_MOVE_NAME:
        move_type = get_hidden_power_type(attacking_pkmn.dvs)
        base_power = get_hidden_power_base_power(attacking_pkmn.dvs)
    else:
        move_type = move.move_type
        base_power = move.base_power

    if base_power is None or base_power == 0:
        return None
    
    if (
        type_chart.get(move_type).get(defending_species.first_type) == const.IMMUNE or
        type_chart.get(move_type).get(defending_species.second_type) == const.IMMUNE
    ):
        return None
    elif (
        defending_pkmn.ability == gen_three_const.LEVITATE_ABILITY and
        move_type == const.TYPE_GROUND
    ):
        return None
    elif (
        defending_pkmn.ability == gen_three_const.DAMP_ABILITY and
        (
            move.name == const.SELFDESTRUCT_MOVE_NAME or
            move.name == const.EXPLOSION_MOVE_NAME
        )
    ):
        return None
    elif (
        (
            defending_pkmn.ability == gen_three_const.VOLT_ABOSRB_ABILITY or
            defending_pkmn.ability == gen_three_const.LIGHTNING_ROD_ABILITY
        ) and
        move_type == const.TYPE_ELECTRIC
    ):
        return None
    elif (
        defending_pkmn.ability == gen_three_const.WATER_ABSORB_ABILITY and
        move_type == const.TYPE_WATER
    ):
        return None
    elif (
        defending_pkmn.ability == gen_three_const.FLASH_FIRE_ABILITY and
        move_type == const.TYPE_FIRE
    ):
        return None
    elif defending_pkmn.ability == gen_three_const.WONDER_GUARD_ABILITY:
        first_effectiveness = type_chart.get(move_type).get(defending_species.first_type)
        second_effectiveness = type_chart.get(move_type).get(defending_species.second_type)
        # if either is immune, then shedinja is immune
        # if either is not very effective, then shedinja is net neutral at worst. And thus immune
        if (
            first_effectiveness == const.IMMUNE or first_effectiveness == const.NOT_VERY_EFFECTIVE or
            second_effectiveness == const.IMMUNE or second_effectiveness == const.NOT_VERY_EFFECTIVE
        ):
            return None
        # if neither is super effective, then shedinja is also immune
        elif (
            first_effectiveness != const.SUPER_EFFECTIVE and second_effectiveness != const.SUPER_EFFECTIVE
        ):
            return None
        # we are left with only the cases where at least one is super effective, and the other is either neutral or super effective
    
    # special move interactions
    if const.FLAVOR_FIXED_DAMAGE in move.attack_flavor:
        return damage_calc.DamageRange({base_power: 1})
    elif const.FLAVOR_LEVEL_DAMAGE in move.attack_flavor:
        return damage_calc.DamageRange({attacking_pkmn.level: 1})
    elif const.FLAVOR_PSYWAVE in move.attack_flavor:
        psywave_upper_limit = math.floor(attacking_pkmn.level * 1.5)
        return damage_calc.DamageRange({x:1 for x in range(1, psywave_upper_limit)})

    # TODO: technically inaccurate data if in a doubles battle, and either of the other mons outside the equation have these abilities. Wtv
    # It doesn't actually ever happen in vanilla games, so we're just fully ignoring it
    is_weather_active = False
    if (
        defending_pkmn.ability not in [gen_three_const.AIR_LOCK_ABILITY, gen_three_const.CLOUD_NINE_ABILITY] and
        attacking_pkmn.ability not in [gen_three_const.AIR_LOCK_ABILITY, gen_three_const.CLOUD_NINE_ABILITY]
    ):
        is_weather_active = (weather != const.WEATHER_NONE)

    # TODO: low kick. ughhhhh
    # TODO: present. ughhhhh
    # Handle base_power and move_type override cases first
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
    elif move.name == gen_three_const.ERUPTION_MOVE_NAME:
        try:
            base_power = math.floor(base_power * int(custom_move_data) / 100.0)
        except Exception as e:
            logger.warning(f"Failed to convert return move power to an int: {custom_move_data}")
    elif move.name == gen_three_const.WATER_SPOUT_MOVE_NAME:
        try:
            base_power = math.floor(base_power * int(custom_move_data) / 100.0)
        except Exception as e:
            logger.warning(f"Failed to convert return move power to an int: {custom_move_data}")
    elif move.name == gen_three_const.NATURE_POWER_MOVE_NAME:
        # TODO: nature power emulates 2 moves that have possible bonus damage: earthquake, and surf. We're just fully ignoring those for now
        # TODO: should i just... pull the move info directly, instead of hard-coding it like this? idk
        if custom_move_data == gen_three_const.PLAIN_TERRAIN:
            base_power = 60
            move_type = const.TYPE_NORMAL
        elif custom_move_data == gen_three_const.SAND_TERRAIN:
            base_power = 100
            move_type = const.TYPE_GROUND
        elif custom_move_data == gen_three_const.CAVE_TERRAIN:
            base_power = 80
            move_type = const.TYPE_GHOST
        elif custom_move_data == gen_three_const.ROCK_TERRAIN:
            base_power = 75
            move_type = const.TYPE_ROCK
        elif custom_move_data == gen_three_const.TALL_GRASS_TERRAIN:
            # ugly, but wtv. This turns into stun spore
            return None
        elif custom_move_data == gen_three_const.LONG_GRASS_TERRAIN:
            base_power = 55
            move_type = const.TYPE_GRASS
        elif custom_move_data == gen_three_const.POND_WATER_TERRAIN:
            base_power = 65
            move_type = const.TYPE_WATER
        elif custom_move_data == gen_three_const.SEA_WATER_TERRAIN:
            base_power = 95
            move_type = const.TYPE_WATER
        elif custom_move_data == gen_three_const.UNDERWATER_TERRAIN:
            base_power = 120
            move_type = const.TYPE_WATER
    elif move.name == gen_three_const.WEATHER_BALL_MOVE_NAME and is_weather_active:
        base_power *= 2
        if weather == const.WEATHER_SUN:
            move_type = const.TYPE_FIRE
        elif weather == const.WEATHER_RAIN:
            move_type = const.TYPE_WATER
        elif weather == const.WEATHER_HAIL:
            move_type = const.TYPE_ICE
        elif weather == const.WEATHER_SANDSTORM:
            move_type = const.TYPE_ROCK
    
    if attacking_stage_modifiers is None:
        attacking_stage_modifiers = universal_data_objects.StageModifiers()
    if defending_stage_modifiers is None:
        defending_stage_modifiers = universal_data_objects.StageModifiers()

    # when a crit occurs, always ignore negative modifiers for the attacking pokemon, and always ignore positive modifiers for the defensive pokemon
    if is_crit:
        if move_type in special_types:
            if attacking_stage_modifiers.special_attack_stage < 0:
                attacking_stage_modifiers = universal_data_objects.StageModifiers()
            if defending_stage_modifiers.special_defense_stage > 0:
                defending_stage_modifiers = universal_data_objects.StageModifiers()
        else:
            if attacking_stage_modifiers.attack_stage < 0:
                attacking_stage_modifiers = universal_data_objects.StageModifiers()
            if defending_stage_modifiers.defense_stage > 0:
                defending_stage_modifiers = universal_data_objects.StageModifiers()

    if attacking_battle_stats is None:
        attacking_battle_stats = attacking_pkmn.get_battle_stats(attacking_stage_modifiers)
    if defending_battle_stats is None:
        defending_battle_stats = defending_pkmn.get_battle_stats(defending_stage_modifiers)

    if attacking_pkmn.name == gen_three_const.MAROWAK_NAME and attacking_pkmn.held_item == gen_three_const.THICK_CLUB_NAME:
        attacking_battle_stats.attack *= 2
    elif attacking_pkmn.name == gen_three_const.PIKACHU_NAME and attacking_pkmn.held_item == gen_three_const.LIGHT_BALL_NAME:
        attacking_battle_stats.special_attack *= 2
    elif attacking_pkmn.name == gen_three_const.CLAMPERL_NAME and attacking_pkmn.held_item == gen_three_const.DEEP_SEA_TOOTH_NAME:
        attacking_battle_stats.special_attack *= 2
    elif attacking_pkmn.name == gen_three_const.CLAMPERL_NAME and attacking_pkmn.held_item == gen_three_const.DEEP_SEA_SCALE_NAME:
        attacking_battle_stats.special_defense *= 2
    elif (
        (attacking_pkmn.name == gen_three_const.LATIOS_NAME or attacking_pkmn.name == gen_three_const.LATIAS_NAME) and
        attacking_pkmn.held_item == gen_three_const.DEEP_SEA_SCALE_NAME
    ):
        attacking_battle_stats.special_attack = math.floor(attacking_battle_stats.special_attack * 1.5)
        attacking_battle_stats.special_defense = math.floor(attacking_battle_stats.special_defense * 1.5)

    if (
        (defending_pkmn.name == gen_three_const.LATIOS_NAME or defending_pkmn.name == gen_three_const.LATIAS_NAME) and
        defending_pkmn.held_item == gen_three_const.DEEP_SEA_SCALE_NAME
    ):
        defending_battle_stats.special_attack = math.floor(defending_battle_stats.special_attack * 1.5)
        defending_battle_stats.special_defense = math.floor(defending_battle_stats.special_defense * 1.5)
    elif defending_pkmn.name == gen_three_const.DITTO_NAME and defending_pkmn.held_item == gen_three_const.METAL_POWDER_NAME:
        # this should only apply while transformed... but also like, we don't support transforming in the app rn lmao
        defending_battle_stats.defense *= 2
    
    if attacking_pkmn.ability == gen_three_const.HUSTLE_ABILITY:
        attacking_battle_stats.attack = math.floor(attacking_battle_stats.attack * 1.5)

    if (
        attacking_pkmn.ability == gen_three_const.HUGE_POWER_ABILITY or
        attacking_pkmn.ability == gen_three_const.PURE_POWER_ABILITY
    ):
        attacking_battle_stats.attack = math.floor(attacking_battle_stats.attack * 2)
    
    if attacking_pkmn.held_item == gen_three_const.CHOICE_BAND_NAME:
        attacking_battle_stats.attack = math.floor(attacking_battle_stats.attack * 1.5)
    
    if defending_pkmn.ability == gen_three_const.THICK_FAT_ABILITY and move_type in [const.TYPE_FIRE, const.TYPE_ICE]:
        # oddity: this is technically how the actual code does it, despite it being a bit weird
        # When thick fat is applicable, it debuffs the special attack (technically before applying stages, but wtv)
        attacking_battle_stats.special_attack = math.floor(attacking_battle_stats.special_attack / 2)
        # I'm paranoid, since physical/special types are technically editable in a custom gen
        attacking_battle_stats.attack = math.floor(attacking_battle_stats.attack / 2)
    
    # NOTE: ignoring plus/minus abilities. They would modify special attack here, if ever relevant

    # TODO: bunch of abilities below that have a conditional activation. Need to figure out how to implement them properly
    # until then, they're just fully disabled
    if defending_pkmn.ability == gen_three_const.MARVEL_SCALE_ABILITY and False:
        defending_battle_stats.defense = math.floor(defending_battle_stats.defense * 1.5)
    if attacking_pkmn.ability == gen_three_const.GUTS_ABILITY and False:
        attacking_battle_stats.attack = math.floor(attacking_battle_stats.attack * 1.5)
    if attacking_pkmn.ability == gen_three_const.OVERGROW_ABILITY and move_type == const.TYPE_GRASS and False:
        base_power = math.floor(base_power * 1.5)
    if attacking_pkmn.ability == gen_three_const.BLAZE_ABILITY and move_type == const.TYPE_FIRE and False:
        base_power = math.floor(base_power * 1.5)
    if attacking_pkmn.ability == gen_three_const.TORRENT_ABILITY and move_type == const.TYPE_WATER and False:
        base_power = math.floor(base_power * 1.5)
    if attacking_pkmn.ability == gen_three_const.SWARM_ABILITY and move_type == const.TYPE_BUG and False:
        base_power = math.floor(base_power * 1.5)
    
    if move_type in special_types:
        attacking_stat = attacking_battle_stats.special_attack
        defending_stat = defending_battle_stats.special_defense
        if defender_has_light_screen and not is_crit and move.name != gen_three_const.BRICK_BREAK_MOVE_NAME:
            screen_active = True
        else:
            screen_active = False
    else:
        attacking_stat = attacking_battle_stats.attack
        defending_stat = defending_battle_stats.defense
        if defender_has_reflect and not is_crit and move.name != gen_three_const.BRICK_BREAK_MOVE_NAME:
            screen_active = True
        else:
            screen_active = False
    
    if  move.name == const.EXPLOSION_MOVE_NAME or move.name == const.SELFDESTRUCT_MOVE_NAME:
        defending_stat = max(math.floor(defending_stat / 2), 1)

    is_stab = (attacking_species.first_type == move_type) or (attacking_species.second_type == move_type)
    if move.name == const.FUTURE_SIGHT_MOVE_NAME:
        is_stab = False

    if held_item_boost_table.get(attacking_pkmn.held_item) == move_type:
        attacking_stat = math.floor(attacking_stat * 1.1)

    # begin actual formula
    temp = 2 * attacking_pkmn.level
    temp = math.floor(temp / 5) + 2

    temp *= base_power
    temp *= attacking_stat
    temp = math.floor(temp / defending_stat)

    temp = math.floor(temp / 50)

    # start accounting for multipliers
    if screen_active:
        temp = math.floor(temp / 2)
    
    if is_double_battle and move.targeting == const.TARGETING_BOTH_ENEMIES:
        temp = math.floor(temp / 2)

    weather_boost = False
    weather_penalty = False
    if is_weather_active:
        if weather == const.WEATHER_RAIN:
            weather_boost = (move_type == const.TYPE_WATER)
            weather_penalty = (
                move_type == const.TYPE_FIRE or
                move.name == const.SOLAR_BEAM_MOVE_NAME
            )
        elif weather == const.WEATHER_SUN:
            weather_boost = (move_type == const.TYPE_FIRE)
            weather_penalty = (move_type == const.TYPE_WATER)
        elif weather != const.WEATHER_NONE:
            weather_penalty = (
                move.name == const.SOLAR_BEAM_MOVE_NAME
        )

    if weather_boost:
        temp = math.floor(temp * 1.5)
    elif weather_penalty:
        temp = math.floor(temp * 0.5)
    
    # TODO: when we support flash fire, support goes here
    flash_fire_activated = False
    if flash_fire_activated:
        temp = math.floor(temp * 1.5)

    temp += 2

    if (
        is_crit and 
        move.name not in [const.SPIT_UP_MOVE_NAME, const.DOOM_DESIRE_MOVE_NAME, const.FUTURE_SIGHT_MOVE_NAME] and
        defending_pkmn.ability not in [gen_three_const.BATTLE_ARMOR_ABILITY, gen_three_const.SHELL_ARMOR_ABILITY]
    ):
        temp *= 2
    
    # handle all the special moves that may affect the damage formula in other ways
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
    elif move.name == gen_three_const.SPIT_UP_MOVE_NAME:
        move_modifier = int(custom_move_data)
    
    temp *= move_modifier

    if move.name in [
        gen_three_const.GUST_MOVE_NAME,
        gen_three_const.TWISTER_MOVE_NAME,
        gen_three_const.SURF_MOVE_NAME,
        gen_three_const.WHIRLPOOL_MOVE_NAME,
        gen_three_const.EARTHQUAKE_MOVE_NAME,
        gen_three_const.MAGNITUDE_MOVE_NAME,
        gen_three_const.PURSUIT_MOVE_NAME,
        gen_three_const.STOMP_MOVE_NAME,
        gen_three_const.EXTRASENSORY_MOVE_NAME,
        gen_three_const.ASTONISH_MOVE_NAME,
        gen_three_const.NEEDLE_ARM_MOVE_NAME,
        gen_three_const.FACADE_MOVE_NAME,
        gen_three_const.SMELLING_SALT_MOVE_NAME,
        gen_three_const.REVENGE_MOVE_NAME,
    ]:
        double_damage = custom_move_data and (gen_three_const.NO_BONUS not in custom_move_data)
    else:
        double_damage = False

    if double_damage:
        temp *= 2

    # TODO: pretty much wholly outside the use case ofthis app, but here just in case
    is_helping_hand_active = False
    if is_helping_hand_active:
        temp = math.floor(temp * 1.5)
    
    # TODO: one day we might need to support this
    is_charge_active = False
    if is_charge_active and move.move_type == const.TYPE_ELECTRIC:
        temp *= 2

    if is_stab:
        temp = math.floor(temp * 1.5)

    for test_type in type_chart.get(move_type):
        if test_type == defending_species.first_type or test_type == defending_species.second_type:
            effectiveness = type_chart.get(move_type).get(test_type)
            if effectiveness == const.SUPER_EFFECTIVE:
                temp *= 2
            elif effectiveness == const.NOT_VERY_EFFECTIVE:
                temp = math.floor(temp / 2)
    
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
    if move.name in [const.SPIT_UP_MOVE_NAME]:
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
