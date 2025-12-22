import math
import logging
import copy
from typing import Dict, List

from pkmn import universal_data_objects, damage_calc
from pkmn.gen_4.data_objects import get_hidden_power_type, get_hidden_power_base_power, modify_stat_by_stage
from utils.constants import const
from pkmn.gen_4.gen_four_constants import gen_four_const


logger = logging.getLogger(__name__)


MIN_RANGE = 85
MAX_RANGE = 100
NUM_ROLLS = MAX_RANGE - MIN_RANGE + 1


def get_crit_rate(cur_mon:universal_data_objects.EnemyPkmn, move:universal_data_objects.Move, custom_move_data:str):
    stage = 0
    if const.FLAVOR_HIGH_CRIT in move.attack_flavor:
        stage += 1
    if move.name == gen_four_const.NATURE_POWER_MOVE_NAME and custom_move_data == gen_four_const.LONG_GRASS_TERRAIN:
        stage += 1
    if cur_mon.ability == gen_four_const.SUPER_LUCK_ABILITY:
        stage += 1

    if stage == 0:
        return (1/16)
    elif stage == 1:
        return (1/8)
    elif stage == 2:
        return (1/4)
    elif stage == 3:
        return (1/3)
    # stages 4+
    return (1/2)


def get_move_accuracy(
    pkmn:universal_data_objects.EnemyPkmn,
    move:universal_data_objects.Move,
    custom_move_data:str,
    defending_pkmn:universal_data_objects.EnemyPkmn,
    weather:str,
):
    if pkmn.ability == gen_four_const.NO_GUARD_ABILITY or defending_pkmn.ability == gen_four_const.NO_GUARD_ABILITY:
        return None

    if move.name == gen_four_const.NATURE_POWER_MOVE_NAME:
        if custom_move_data == gen_four_const.TALL_GRASS_TERRAIN:
            result = 75
        elif custom_move_data == gen_four_const.LONG_GRASS_TERRAIN:
            result = 95
        elif custom_move_data == gen_four_const.UNDERWATER_TERRAIN:
            result = 80
        elif custom_move_data == gen_four_const.PLAIN_TERRAIN:
            result = None
        result = 100
    else:
        result = move.accuracy
    
    if result is None:
        return None
    
    if pkmn.ability == gen_four_const.COMPOUND_EYES_ABILITY:
        result = min(
            math.floor(result * 1.3),
            100
        )
    elif pkmn.ability == gen_four_const.HUSTLE_ABILITY:
        is_physical = move.category == const.CATEGORY_PHYSICAL
        if move.name == gen_four_const.NATURE_POWER_MOVE_NAME:
            is_physical = custom_move_data in [gen_four_const.SAND_TERRAIN, gen_four_const.CAVE_TERRAIN, gen_four_const.TALL_GRASS_TERRAIN]
        if is_physical:
            result = math.floor(result * 3277 / 4096)
    
    if defending_pkmn.ability == gen_four_const.SAND_VEIL_ABILITY and weather == const.WEATHER_SANDSTORM:
        result = math.floor(result * 3277 / 4096)

    if defending_pkmn.ability == gen_four_const.SNOW_CLOAK_ABILITY and weather == const.WEATHER_SANDSTORM:
        result = math.floor(result * 3277 / 4096)

    return result


def calculate_gen_four_damage(
    attacking_pkmn:universal_data_objects.EnemyPkmn,
    attacking_species:universal_data_objects.PokemonSpecies,
    move:universal_data_objects.Move,
    defending_pkmn:universal_data_objects.EnemyPkmn,
    defending_species:universal_data_objects.PokemonSpecies,
    type_chart:Dict[str, Dict[str, str]],
    held_item_boost_table:Dict[str, str],
    attacking_stage_modifiers:universal_data_objects.StageModifiers=None,
    defending_stage_modifiers:universal_data_objects.StageModifiers=None,
    attacking_field:universal_data_objects.FieldStatus=None,
    defending_field:universal_data_objects.FieldStatus=None,
    is_crit:bool=False,
    custom_move_data:str="",
    weather:str=const.WEATHER_NONE,
    is_double_battle:bool=False,
    attacking_battle_stats:universal_data_objects.StatBlock=None,
    defending_battle_stats:universal_data_objects.StatBlock=None,
):
    if move.name == const.HIDDEN_POWER_MOVE_NAME:
        move_type = get_hidden_power_type(attacking_pkmn.dvs)
        base_power = get_hidden_power_base_power(attacking_pkmn.dvs)
    else:
        move_type = move.move_type
        base_power = move.base_power
    
    if base_power is None or base_power == 0:
        return None
    
    attacking_mon_first_type = attacking_species.first_type
    attacking_mon_second_type = attacking_species.second_type
    attacking_ability = attacking_pkmn.ability
    defending_ability = defending_pkmn.ability

    if attacking_field.worry_seed:
        attacking_ability = gen_four_const.INSOMNIA_ABILITY
    elif attacking_field.gastro_acid:
        attacking_ability = ""

    if defending_field.worry_seed:
        defending_ability = gen_four_const.INSOMNIA_ABILITY
    elif defending_field.gastro_acid:
        defending_ability = ""

    if attacking_ability == gen_four_const.MULTITYPE_ABILITY:
        new_type = gen_four_const.PLATE_TYPE_LOOKUP.get(attacking_pkmn.held_item)
        if new_type:
            attacking_mon_first_type = new_type
            attacking_mon_second_type = new_type

    # TODO: technically inaccurate data if in a doubles battle, and either of the other mons outside the equation have these abilities. Wtv
    # It doesn't actually ever happen in vanilla games, so we're just fully ignoring it
    is_weather_active = False
    if (
        defending_ability not in [gen_four_const.AIR_LOCK_ABILITY, gen_four_const.CLOUD_NINE_ABILITY] and
        attacking_ability not in [gen_four_const.AIR_LOCK_ABILITY, gen_four_const.CLOUD_NINE_ABILITY]
    ):
        is_weather_active = (weather != const.WEATHER_NONE)

    # Need to resolve any moves/abilities that change move type as early as possible
    if move.name == gen_four_const.NATURE_POWER_MOVE_NAME:
        # TODO: nature power emulates 2 moves that have possible bonus damage: earthquake, and surf. We're just fully ignoring those for now
        # TODO: should i just... pull the move info directly, instead of hard-coding it like this? idk
        if custom_move_data == gen_four_const.PLAIN_TERRAIN:
            base_power = 60
            move_type = const.TYPE_NORMAL
        elif custom_move_data == gen_four_const.SAND_TERRAIN:
            base_power = 100
            move_type = const.TYPE_GROUND
        elif custom_move_data == gen_four_const.CAVE_TERRAIN:
            base_power = 80
            move_type = const.TYPE_GHOST
        elif custom_move_data == gen_four_const.ROCK_TERRAIN:
            base_power = 75
            move_type = const.TYPE_ROCK
        elif custom_move_data == gen_four_const.TALL_GRASS_TERRAIN:
            # ugly, but wtv. This turns into stun spore
            return None
        elif custom_move_data == gen_four_const.LONG_GRASS_TERRAIN:
            base_power = 55
            move_type = const.TYPE_GRASS
        elif custom_move_data == gen_four_const.POND_WATER_TERRAIN:
            base_power = 65
            move_type = const.TYPE_WATER
        elif custom_move_data == gen_four_const.SEA_WATER_TERRAIN:
            base_power = 95
            move_type = const.TYPE_WATER
        elif custom_move_data == gen_four_const.UNDERWATER_TERRAIN:
            base_power = 120
            move_type = const.TYPE_WATER
    elif move.name == gen_four_const.WEATHER_BALL_MOVE_NAME and is_weather_active:
        base_power *= 2
        if weather == const.WEATHER_SUN:
            move_type = const.TYPE_FIRE
        elif weather == const.WEATHER_RAIN:
            move_type = const.TYPE_WATER
        elif weather == const.WEATHER_HAIL:
            move_type = const.TYPE_ICE
        elif weather == const.WEATHER_SANDSTORM:
            move_type = const.TYPE_ROCK

    if (
        attacking_ability == gen_four_const.TECHNICIAN_ABILITY and
        base_power <= 60
    ):
        base_power = math.floor(60 * 1.5)

    if attacking_ability == gen_four_const.NORMALIZE_ABILITY:
        move_type = const.TYPE_NORMAL
    
    if move.name == gen_four_const.JUDGMENT_MOVE_NAME:
        new_type = gen_four_const.PLATE_TYPE_LOOKUP.get(attacking_pkmn.held_item)
        if new_type:
            move_type = new_type
    
    if move.name == gen_four_const.PUNISHMENT_MOVE_NAME:
        num_buffs = 0
        for cur_stage in [
            defending_stage_modifiers.attack_stage,
            defending_stage_modifiers.defense_stage,
            defending_stage_modifiers.special_attack_stage,
            defending_stage_modifiers.special_defense_stage,
            defending_stage_modifiers.speed_stage,
        ]:
            if cur_stage > 0:
                num_buffs += cur_stage
        
        num_buffs = min(num_buffs, 7)
        base_power += (num_buffs * 20)

    is_scrappy_active = (
        (defending_species.first_type == const.TYPE_GHOST or defending_species.second_type == const.TYPE_GHOST) and
        (move.move_type == const.TYPE_NORMAL or move.move_type == const.TYPE_FIGHTING) and
        attacking_ability == gen_four_const.SCRAPPY_ABILITY
    )

    ignore_ground_immunity = (
        (defending_species.first_type == const.TYPE_FLYING or defending_species.second_type == const.TYPE_FLYING) and
        move.move_type == const.TYPE_GROUND and
        (defending_field.gravity or defending_field.roost)
    )

    ignore_dark_immunity = (
        (defending_species.first_type == const.TYPE_DARK or defending_species.second_type == const.TYPE_DARK) and
        move.move_type == const.TYPE_PSYCHIC and
        defending_field.miracle_eye
    )

    
    if (
        (
            type_chart.get(move_type).get(defending_species.first_type) == const.IMMUNE or
            type_chart.get(move_type).get(defending_species.second_type) == const.IMMUNE
        ) and
        (not is_scrappy_active) and
        (not ignore_ground_immunity) and
        (not ignore_dark_immunity)
    ):
        return None
    elif (
        defending_ability == gen_four_const.LEVITATE_ABILITY and
        move_type == const.TYPE_GROUND and
        (not ignore_ground_immunity)
    ):
        return None
    elif (
        defending_ability == gen_four_const.DAMP_ABILITY and
        (
            move.name == const.SELFDESTRUCT_MOVE_NAME or
            move.name == const.EXPLOSION_MOVE_NAME
        )
    ):
        return None
    elif (
        (
            defending_ability == gen_four_const.VOLT_ABOSRB_ABILITY or
            defending_ability == gen_four_const.LIGHTNING_ROD_ABILITY or
            defending_ability == gen_four_const.MOTOR_DRIVE_ABILITY
        ) and
        move_type == const.TYPE_ELECTRIC
    ):
        return None
    elif (
        defending_ability == gen_four_const.WATER_ABSORB_ABILITY and
        move_type == const.TYPE_WATER
    ):
        return None
    elif (
        defending_ability == gen_four_const.FLASH_FIRE_ABILITY and
        move_type == const.TYPE_FIRE
    ):
        return None
    elif (
        defending_ability == gen_four_const.DRY_SKIN_ABILITY and
        move_type == const.TYPE_WATER
    ):
        return None
    elif defending_ability == gen_four_const.WONDER_GUARD_ABILITY:
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
    elif (
        defending_field.magnet_rise and
        move.move_type == const.TYPE_GROUND
    ):
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

    # when a crit occurs, always ignore negative modifiers for the attacking pokemon, and always ignore positive modifiers for the defensive pokemon
    if is_crit:
        if move.category == const.CATEGORY_PHYSICAL:
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
        attacking_battle_stats = attacking_pkmn.get_battle_stats(attacking_stage_modifiers, mon_field=attacking_field)

    if defending_battle_stats is None:
        defending_battle_stats = defending_pkmn.get_battle_stats(defending_stage_modifiers, mon_field=defending_field)

    # TODO: present. ughhhhh
    # Handle base_power and move_type override cases first
    if move.name == gen_four_const.MAGNITUDE_MOVE_NAME:
        if gen_four_const.MAGNITUDE_4 in custom_move_data:
            base_power = 10
        elif gen_four_const.MAGNITUDE_5 in custom_move_data:
            base_power = 30
        elif gen_four_const.MAGNITUDE_6 in custom_move_data:
            base_power = 50
        elif gen_four_const.MAGNITUDE_7 in custom_move_data:
            base_power = 70
        elif gen_four_const.MAGNITUDE_8 in custom_move_data:
            base_power = 90
        elif gen_four_const.MAGNITUDE_9 in custom_move_data:
            base_power = 110
        elif gen_four_const.MAGNITUDE_10 in custom_move_data:
            base_power = 150
    elif move.name in [const.FLAIL_MOVE_NAME, const.REVERSAL_MOVE_NAME]:
        if gen_four_const.FLAIL_FULL_HP in custom_move_data:
            base_power = 20
        elif gen_four_const.FLAIL_HALF_HP in custom_move_data:
            base_power = 40
        elif gen_four_const.FLAIL_QUARTER_HP in custom_move_data:
            base_power = 80
        elif gen_four_const.FLAIL_TEN_PERCENT_HP in custom_move_data:
            base_power = 100
        elif gen_four_const.FLAIL_FIVE_PERCENT_HP in custom_move_data:
            base_power = 150
        elif gen_four_const.FLAIL_MIN_HP in custom_move_data:
            base_power = 200
    elif move.name == gen_four_const.RETURN_MOVE_NAME:
        try:
            base_power = int(custom_move_data)
        except Exception as e:
            logger.warning(f"Failed to convert return move power to an int: {custom_move_data}")
    elif move.name == gen_four_const.ERUPTION_MOVE_NAME:
        try:
            base_power = math.floor(base_power * int(custom_move_data) / 100.0)
        except Exception as e:
            logger.warning(f"Failed to convert return move power to an int: {custom_move_data}")
    elif move.name == gen_four_const.WATER_SPOUT_MOVE_NAME:
        try:
            base_power = math.floor(base_power * int(custom_move_data) / 100.0)
        except Exception as e:
            logger.warning(f"Failed to convert return move power to an int: {custom_move_data}")
    elif (
        move.name == gen_four_const.CRUSH_GRIP_MOVE_NAME or
        move.name == gen_four_const.WRING_OUT_MOVE_NAME
    ):
        try:
            base_power = math.floor(1 + (120 * int(custom_move_data)))
        except Exception as e:
            logger.warning(f"Failed to convert return move power to an int: {custom_move_data}")
    elif move.name == gen_four_const.GYRO_BALL_MOVE_NAME:
        base_power = math.floor(1 + ((25 * attacking_battle_stats.speed) / defending_battle_stats.speed))
        base_power = min(base_power, 150)
    elif move.name == gen_four_const.TRUMP_CARD_MOVE_NAME:
        if custom_move_data == "3":
            base_power = 50
        elif custom_move_data == "2":
            base_power = 60
        elif custom_move_data == "1":
            base_power = 80
        elif custom_move_data == "0":
            base_power = 200
    elif move.name in [gen_four_const.LOW_KICK_MOVE_NAME, gen_four_const.GRASS_KNOW_MOVE_NAME]:
        if defending_species.weight is None:
            base_power = 1
            logger.warning(f"Undefined weight for species: {defending_species.name}")
        elif defending_species.weight < 10:
            base_power = 20
        elif defending_species.weight < 25:
            base_power = 40
        elif defending_species.weight < 50:
            base_power = 60
        elif defending_species.weight < 100:
            base_power = 80
        elif defending_species.weight < 200:
            base_power = 100
        else:
            base_power = 120

    # NOTE: for now, just ignoring the "edge case" of: what if the mon for mon-specific unique items has klutz?
    # it never occurs in normal gameplay, and would require a hack. so, wtv
    if attacking_pkmn.name == gen_four_const.MAROWAK_NAME and attacking_pkmn.held_item == gen_four_const.THICK_CLUB_NAME:
        attacking_battle_stats.attack *= 2
    elif attacking_pkmn.name == gen_four_const.PIKACHU_NAME and attacking_pkmn.held_item == gen_four_const.LIGHT_BALL_NAME:
        attacking_battle_stats.special_attack *= 2
    elif attacking_pkmn.name == gen_four_const.CLAMPERL_NAME and attacking_pkmn.held_item == gen_four_const.DEEP_SEA_TOOTH_NAME:
        attacking_battle_stats.special_attack *= 2
    elif attacking_pkmn.name == gen_four_const.CLAMPERL_NAME and attacking_pkmn.held_item == gen_four_const.DEEP_SEA_SCALE_NAME:
        attacking_battle_stats.special_defense *= 2
    elif (
        (attacking_pkmn.name == gen_four_const.LATIOS_NAME or attacking_pkmn.name == gen_four_const.LATIAS_NAME) and
        attacking_pkmn.held_item == gen_four_const.DEEP_SEA_SCALE_NAME
    ):
        attacking_battle_stats.special_attack = math.floor(attacking_battle_stats.special_attack * 1.5)
        attacking_battle_stats.special_defense = math.floor(attacking_battle_stats.special_defense * 1.5)

    if (
        (defending_pkmn.name == gen_four_const.LATIOS_NAME or defending_pkmn.name == gen_four_const.LATIAS_NAME) and
        defending_pkmn.held_item == gen_four_const.DEEP_SEA_SCALE_NAME
    ):
        defending_battle_stats.special_attack = math.floor(defending_battle_stats.special_attack * 1.5)
        defending_battle_stats.special_defense = math.floor(defending_battle_stats.special_defense * 1.5)
    elif defending_pkmn.name == gen_four_const.DITTO_NAME and defending_pkmn.held_item == gen_four_const.METAL_POWDER_NAME:
        # this should only apply while transformed... but also like, we don't support transforming in the app rn lmao
        defending_battle_stats.defense *= 2
    
    if attacking_ability == gen_four_const.HUSTLE_ABILITY:
        attacking_battle_stats.attack = math.floor(attacking_battle_stats.attack * 1.5)

    if (
        attacking_ability == gen_four_const.HUGE_POWER_ABILITY or
        attacking_ability == gen_four_const.PURE_POWER_ABILITY
    ):
        attacking_battle_stats.attack = math.floor(attacking_battle_stats.attack * 2)
    
    if (
        attacking_pkmn.held_item == gen_four_const.CHOICE_BAND_NAME and
        attacking_ability != gen_four_const.KLUTZ_ABILITY
    ):
        attacking_battle_stats.attack = math.floor(attacking_battle_stats.attack * 1.5)

    if (
        attacking_pkmn.held_item == gen_four_const.CHOICE_SPECS_NAME and
        attacking_ability != gen_four_const.KLUTZ_ABILITY
    ):
        attacking_battle_stats.special_attack = math.floor(attacking_battle_stats.special_attack * 1.5)
    
    if defending_ability == gen_four_const.THICK_FAT_ABILITY and move_type in [const.TYPE_FIRE, const.TYPE_ICE]:
        # oddity: this is technically how the actual code does it, despite it being a bit weird
        # When thick fat is applicable, it debuffs the special attack (technically before applying stages, but wtv)
        attacking_battle_stats.special_attack = math.floor(attacking_battle_stats.special_attack / 2)
        attacking_battle_stats.attack = math.floor(attacking_battle_stats.attack / 2)

    if defending_ability == gen_four_const.HEATPROOF_ABILITY and move_type == const.TYPE_FIRE:
        # seems to reuse the same code as thick-fat (based on bulbapedia's description)
        attacking_battle_stats.special_attack = math.floor(attacking_battle_stats.special_attack / 2)
        attacking_battle_stats.attack = math.floor(attacking_battle_stats.attack / 2)
    
    if (
        defending_ability == gen_four_const.FLOWER_GIFT_ABILITY and
        is_weather_active and
        weather == const.WEATHER_SUN
    ):
        defending_battle_stats.special_attack = math.floor(defending_battle_stats.special_attack * 1.5)
        defending_battle_stats.special_defense = math.floor(defending_battle_stats.special_attack * 1.5)
    elif (
        attacking_ability == gen_four_const.FLOWER_GIFT_ABILITY and
        is_weather_active and
        weather == const.WEATHER_SUN
    ):
        attacking_battle_stats.special_attack = math.floor(attacking_battle_stats.special_attack * 1.5)
        attacking_battle_stats.special_defense = math.floor(attacking_battle_stats.special_attack * 1.5)
    elif (
        attacking_ability == gen_four_const.SOLAR_POWER_ABILITY and
        is_weather_active and
        weather == const.WEATHER_SUN
    ):
        attacking_battle_stats.special_attack = math.floor(attacking_battle_stats.special_attack * 1.5)
    
    # NOTE: ignoring plus/minus abilities. They would modify special attack here, if ever relevant

    # TODO: bunch of abilities below that have a conditional activation. Need to figure out how to implement them properly
    # until then, they're just fully disabled
    if defending_ability == gen_four_const.MARVEL_SCALE_ABILITY and False:
        defending_battle_stats.defense = math.floor(defending_battle_stats.defense * 1.5)
    if attacking_ability == gen_four_const.GUTS_ABILITY and False:
        attacking_battle_stats.attack = math.floor(attacking_battle_stats.attack * 1.5)
    if attacking_ability == gen_four_const.OVERGROW_ABILITY and move_type == const.TYPE_GRASS and False:
        base_power = math.floor(base_power * 1.5)
    if attacking_ability == gen_four_const.BLAZE_ABILITY and move_type == const.TYPE_FIRE and False:
        base_power = math.floor(base_power * 1.5)
    if attacking_ability == gen_four_const.TORRENT_ABILITY and move_type == const.TYPE_WATER and False:
        base_power = math.floor(base_power * 1.5)
    if attacking_ability == gen_four_const.SWARM_ABILITY and move_type == const.TYPE_BUG and False:
        base_power = math.floor(base_power * 1.5)
    
    if move.category == const.CATEGORY_SPECIAL:
        attacking_stat = attacking_battle_stats.special_attack
        defending_stat = defending_battle_stats.special_defense
        if defending_field.light_screen and not is_crit and move.name != gen_four_const.BRICK_BREAK_MOVE_NAME:
            screen_active = True
        else:
            screen_active = False
    else:
        attacking_stat = attacking_battle_stats.attack
        defending_stat = defending_battle_stats.defense
        if defending_field.reflect and not is_crit and move.name != gen_four_const.BRICK_BREAK_MOVE_NAME:
            screen_active = True
        else:
            screen_active = False
    
    if  move.name == const.EXPLOSION_MOVE_NAME or move.name == const.SELFDESTRUCT_MOVE_NAME:
        defending_stat = max(math.floor(defending_stat / 2), 1)

    is_stab = (attacking_mon_first_type == move_type) or (attacking_mon_second_type == move_type)
    if move.name == const.FUTURE_SIGHT_MOVE_NAME:
        is_stab = False

    if (
        held_item_boost_table.get(attacking_pkmn.held_item) == move_type and
        attacking_ability != gen_four_const.KLUTZ_ABILITY
    ):
        attacking_stat = math.floor(attacking_stat * 1.2)
    elif (
        attacking_pkmn.name == gen_four_const.DIALGA_NAME and
        attacking_pkmn.held_item == gen_four_const.ADAMANT_ORB_NAME and
        (move.move_type == const.TYPE_DRAGON or move.move_type == const.TYPE_STEEL)
    ):
        attacking_stat = math.floor(attacking_stat * 1.2)
    elif (
        attacking_pkmn.name == gen_four_const.PALKIA_NAME and
        attacking_pkmn.held_item == gen_four_const.LUSTROUS_ORB_NAME and
        (move.move_type == const.TYPE_DRAGON or move.move_type == const.TYPE_WATER)
    ):
        attacking_stat = math.floor(attacking_stat * 1.2)
    elif (
        attacking_pkmn.name == gen_four_const.GIRATINA_NAME and
        attacking_pkmn.held_item == gen_four_const.GRISEOUS_ORB_NAME and
        (move.move_type == const.TYPE_DRAGON or move.move_type == const.TYPE_GHOST)
    ):
        attacking_stat = math.floor(attacking_stat * 1.2)

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
        defending_ability not in [gen_four_const.BATTLE_ARMOR_ABILITY, gen_four_const.SHELL_ARMOR_ABILITY]
    ):
        if attacking_ability == gen_four_const.SNIPER_ABILITY:
            temp *= 3
        else:
            temp *= 2
    
    # handle all the special moves that may affect the damage formula in other ways
    move_modifier = 1

    if move.name == gen_four_const.ROLLOUT_MOVE_NAME:
        # ugh, dumb hack. String is either just an int, or the special case of last turn + defense curl
        try:
            num_rollout_turns = int(custom_move_data)
        except ValueError:
            num_rollout_turns = 6
        
        move_modifier = math.pow(2, num_rollout_turns)
    elif move.name == gen_four_const.FURY_CUTTER_MOVE_NAME:
        move_modifier = math.pow(2, int(custom_move_data))
    elif move.name == gen_four_const.RAGE_MOVE_NAME:
        move_modifier = int(custom_move_data)
    elif move.name == gen_four_const.TRIPLE_KICK_MOVE_NAME:
        move_modifier = int(custom_move_data)
    elif move.name == gen_four_const.SPIT_UP_MOVE_NAME:
        move_modifier = int(custom_move_data)
    
    temp *= move_modifier

    if move.name in [
        gen_four_const.GUST_MOVE_NAME,
        gen_four_const.TWISTER_MOVE_NAME,
        gen_four_const.SURF_MOVE_NAME,
        gen_four_const.WHIRLPOOL_MOVE_NAME,
        gen_four_const.EARTHQUAKE_MOVE_NAME,
        gen_four_const.MAGNITUDE_MOVE_NAME,
        gen_four_const.PURSUIT_MOVE_NAME,
        gen_four_const.STOMP_MOVE_NAME,
        gen_four_const.EXTRASENSORY_MOVE_NAME,
        gen_four_const.ASTONISH_MOVE_NAME,
        gen_four_const.NEEDLE_ARM_MOVE_NAME,
        gen_four_const.FACADE_MOVE_NAME,
        gen_four_const.SMELLING_SALT_MOVE_NAME,
        gen_four_const.REVENGE_MOVE_NAME,
        gen_four_const.ASSURANCE_MOVE_NAME,
        gen_four_const.AVALANCHE_MOVE_NAME,
        gen_four_const.BRINE_MOVE_NAME,
        gen_four_const.PAYBACK_MOVE_NAME,
        gen_four_const.WAKE_UP_SLAP_MOVE_NAME,
    ]:
        double_damage = custom_move_data and (gen_four_const.NO_BONUS not in custom_move_data)
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
        if attacking_ability == gen_four_const.ADAPTABILITY_ABILITY:
            temp = math.floor(temp * 2)
        else:
            temp = math.floor(temp * 1.5)

    is_tinted_lens_active = False
    for test_type in type_chart.get(move_type):
        if test_type == defending_species.first_type or test_type == defending_species.second_type:
            effectiveness = type_chart.get(move_type).get(test_type)
            if effectiveness == const.SUPER_EFFECTIVE:
                if (
                    defending_ability == gen_four_const.FILTER_ABILITY or
                    defending_ability == gen_four_const.SOLID_ROCK_ABILITY
                ):
                    temp = math.floor(temp * 1.5)
                else:
                    temp *= 2
            elif effectiveness == const.NOT_VERY_EFFECTIVE:
                if attacking_ability == gen_four_const.TINTED_LENS_ABILITY:
                    is_tinted_lens_active = True
                temp = math.floor(temp / 2)
    
    # doing all this so that we guarantee that you only get one tinted lens boost if the move is doubly resisted
    if is_tinted_lens_active:
        temp *= 2

    # NOTE: I don't really know where in the formula gen 4 multipliers go
    # So, just throwing them at the end
    if (
        defending_ability == gen_four_const.DRY_SKIN_ABILITY and
        move.move_type == const.TYPE_FIRE
    ):
        temp = math.floor(temp * 1.3)

    
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
                other_damage = calculate_gen_four_damage(
                    attacking_pkmn,
                    attacking_species,
                    move,
                    defending_pkmn,
                    defending_species,
                    type_chart,
                    held_item_boost_table,
                    attacking_stage_modifiers,
                    defending_stage_modifiers,
                    attacking_field=attacking_field,
                    defending_field=defending_field,
                    weather=weather,
                    is_double_battle=is_double_battle,
                    custom_move_data=""
                )
            else:
                other_damage = result
            
            for _ in range(1, multi_hit_multiplier):
                result = result + other_damage
    
    return result
