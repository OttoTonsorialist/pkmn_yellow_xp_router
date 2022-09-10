import math
from typing import Dict, Tuple

from pkmn.data_objects import BadgeList, EnemyPkmn, Move, PokemonSpecies, StageModifiers, StatBlock
from pkmn import pkmn_db
from utils.constants import const

MIN_RANGE = 217
MAX_RANGE = 255
NUM_ROLLS = MAX_RANGE - MIN_RANGE + 1

class DamageRange:
    def __init__(self, damage_vals:dict, num_attacks=1):
        self.damage_vals = {}
        self.min_damage = None
        self.max_damage = None
        self.size = 0

        for cur_damage in damage_vals:
            if cur_damage not in self.damage_vals:
                self.damage_vals[cur_damage] = 0
            
            self.damage_vals[cur_damage] += damage_vals[cur_damage]
            self.size += damage_vals[cur_damage]

            if self.min_damage is None or cur_damage < self.min_damage:
                self.min_damage = cur_damage
            if self.max_damage is None or cur_damage > self.max_damage:
                self.max_damage = cur_damage
        
        if self.max_damage is None or self.min_damage is None:
            raise Exception

        self.num_attacks = num_attacks
    
    def add(self, other):
        if not isinstance(other, DamageRange):
            raise ValueError("Can only add DamageRange to other DamageRanges")

        result_damage_vals = {}

        for my_cur_damage, my_count in self.damage_vals.items():
            for your_cur_damage, your_count in other.damage_vals.items():
                cur_total_damage = my_cur_damage + your_cur_damage
                if cur_total_damage not in result_damage_vals:
                    result_damage_vals[cur_total_damage] = 0

                result_damage_vals[cur_total_damage] += my_count + your_count
        
        return DamageRange(result_damage_vals, num_attacks=(self.num_attacks + other.num_attacks))

    def split_kills(self, hp_threshold):
        if hp_threshold > self.max_damage:
            return None, self
        elif hp_threshold <= self.min_damage:
            return self, None
        
        kill_damage_vals = {}
        non_kill_damage_vals = {}

        for cur_damage, cur_count in self.damage_vals.items():
            if cur_damage >= hp_threshold:
                kill_damage_vals[cur_damage] = cur_count
            else:
                non_kill_damage_vals[cur_damage] = cur_count

        return DamageRange(kill_damage_vals, num_attacks=self.num_attacks), DamageRange(non_kill_damage_vals, num_attacks=self.num_attacks)

    def __len__(self):
        return self.size
    
    def to_string(self, max_num=5, percent_of=None):
        result = []

        for cur_dam in sorted(self.damage_vals.keys()):
            if percent_of is not None:
                cur_percent = (cur_dam / percent_of) * 100
                result.append(f"{cur_percent:.1f} x{self.damage_vals[cur_dam]}")
            else:
                result.append(f"{cur_dam} x{self.damage_vals[cur_dam]}")
        
        if max_num is not None and max_num > 1 and len(result) > max_num:
            parts = max_num // 2
            result = result[:parts] + ['...'] + result[-parts:]
        
        return ", ".join(result)
    
    def __repr__(self):
        return self.to_string()
    
    def __add__(self, other):
        return self.add(other)


def percent_rolls_kill(
    num_non_crits:int,
    damage_range:DamageRange,
    num_crits:int,
    crit_damage_range:DamageRange,
    target_hp:int,
    memoization:Dict[Tuple[int, int, int], int]
):
    num_kill_rolls = _percent_rolls_kill_recursive(
        num_non_crits,
        damage_range,
        num_crits,
        crit_damage_range,
        target_hp,
        1,
        0,
        memoization
    )

    return 100.0 * (num_kill_rolls) / math.pow(len(damage_range), num_non_crits + num_crits)

def _percent_rolls_kill_recursive(
    num_non_crits:int,
    damage_range:DamageRange,
    num_crits:int,
    crit_damage_range:DamageRange,
    target_hp:int,
    num_roll_multiplier:int,
    total_damage:int,
    memoization:Dict[Tuple[int, int, int], int]
):

    cur_key = (num_non_crits, num_crits, num_roll_multiplier, total_damage)
    if cur_key in memoization:
        return memoization[cur_key]

    min_damage_left = num_non_crits * damage_range.min_damage
    min_damage_left += num_crits * crit_damage_range.min_damage

    max_damage_left = num_non_crits * damage_range.max_damage
    max_damage_left += num_crits * crit_damage_range.max_damage

    if total_damage + min_damage_left >= target_hp:
        # if kill is guaranteed, add all rolls for this and future attacks
        # NOTE: use the number of rolls in the provided damage_range, so that special moves like psywave still work properly
        result = num_roll_multiplier * math.pow(len(damage_range), num_non_crits + num_crits)
        memoization[cur_key] = result
        return result
    elif num_crits == 0 and num_non_crits == 0:
        # ran out of attacks without a kill being found, no kill rolls found
        memoization[cur_key] = 0
        return 0
    elif total_damage + max_damage_left < target_hp:
        # kill is impossible even with future rolls, just quit and don't bother calculating
        memoization[cur_key] = 0
        return 0

    # recursive case - a kill is still possible, but not found yet
    result = 0
    if num_crits > 0:
        next_damage_range = crit_damage_range
        num_crits -= 1
    else:
        next_damage_range = damage_range
        num_non_crits -= 1
    
    # find all possible kills from this point forward
    for next_damage in next_damage_range.damage_vals:
        result += _percent_rolls_kill_recursive(
            num_non_crits,
            damage_range,
            num_crits,
            crit_damage_range,
            target_hp,
            next_damage_range.damage_vals[next_damage],
            total_damage + next_damage,
            memoization
        )
    
    result *= num_roll_multiplier
    memoization[cur_key] = result
    return result


def get_crit_rate(pkmn:EnemyPkmn, move:Move):
    crit_numerator = int(pkmn.base_stat_block.speed / 2)
    if move.attack_flavor == const.FLAVOR_HIGH_CRIT:
        crit_numerator *= 8
    
    crit_numerator = min(int(crit_numerator), 255)
    result = crit_numerator / 256
    return result


def find_kill(damage_range:DamageRange, crit_damage_range:DamageRange, crit_chance:float, target_hp:int, attack_depth:int=8, percent_cutoff:float=0.1):
    # NOTE: if attack_depth is too deep, (10+ is where I started to notice the issues), you quickly get overflow issues
    result = []

    min_possible_damage = min(damage_range.min_damage, crit_damage_range.min_damage)
    max_possible_damage = max(damage_range.max_damage, crit_damage_range.max_damage)
    highest_found_kill_pct = 0
    memoization = {}

    # this is a quick and dirty way to ignore calculating psywave, which has vastly more possible rolls, and thus takes much longer to calculate
    if len(damage_range) <= NUM_ROLLS:
        for cur_num_attacks in range(1, attack_depth + 1):
            if (max_possible_damage * cur_num_attacks) < target_hp:
                continue
            elif (min_possible_damage * cur_num_attacks) >= target_hp:
                highest_found_kill_pct = 100
                result.append((cur_num_attacks, 100))
                break

            # a kill is possible, but not guaranteed
            # find the exact kill percent
            cur_total_kill_pct = 0
            for cur_num_crits in range(cur_num_attacks + 1):
                # get the kill percent for this exact combination of crits + non-crits
                kill_percent = percent_rolls_kill(
                    cur_num_attacks - cur_num_crits,
                    damage_range,
                    cur_num_crits,
                    crit_damage_range,
                    target_hp,
                    memoization
                )

                # and multiply that kill percent by the probability of actually getting
                # this combination of crits + non-crits
                cur_total_kill_pct += (
                    kill_percent *
                    math.comb(cur_num_attacks, cur_num_crits) *
                    math.pow(crit_chance, cur_num_crits) *
                    math.pow(1 - crit_chance, cur_num_attacks - cur_num_crits)
                )
            
            highest_found_kill_pct = cur_total_kill_pct
            if cur_total_kill_pct > percent_cutoff:
                result.append((cur_num_attacks, cur_total_kill_pct))
            if cur_total_kill_pct > 99.99:
                break
    
    if highest_found_kill_pct < 99:
        # if we haven't found close enough to a kill, get the guaranteed kill
        result.append((math.ceil(target_hp / damage_range.min_damage), -1))
    
    return result


def calculate_damage(
    attacking_pkmn:EnemyPkmn,
    move:Move,
    defending_pkmn:EnemyPkmn,
    stage_modifiers:StageModifiers=None,
    is_crit:bool=False,
    defender_has_light_screen:bool=False,
    defender_has_reflect:bool=False
):
    if move.base_power is None or move.base_power == 0:
        return None
    
    # special move interactions
    if move.attack_flavor == const.FLAVOR_FIXED_DAMAGE:
        return DamageRange({move.base_power: 1})
    elif move.attack_flavor == const.FLAVOR_LEVEL_DAMAGE:
        return DamageRange({attacking_pkmn.level: 1})
    elif move.attack_flavor == const.FLAVOR_PSYWAVE:
        psywave_upper_limit = math.floor(attacking_pkmn.level * 1.5)
        return DamageRange({x:1 for x in range(1, psywave_upper_limit)})
    
    if stage_modifiers is None:
        stage_modifiers = StageModifiers()

    attacking_battle_stats = attacking_pkmn.get_battle_stats(stage_modifiers, is_crit=is_crit)
    defending_battle_stats = defending_pkmn.get_battle_stats(stage_modifiers, is_crit=is_crit)

    attacking_species = pkmn_db.pkmn_db.get_pkmn(attacking_pkmn.name)
    defending_species = pkmn_db.pkmn_db.get_pkmn(defending_pkmn.name)
    first_type_effectiveness = const.TYPE_CHART.get(move.move_type).get(defending_species.first_type)
    second_type_effectiveness = None
    if defending_species.first_type != defending_species.second_type:
        second_type_effectiveness = const.TYPE_CHART.get(move.move_type).get(defending_species.second_type)
    
    if first_type_effectiveness == const.IMMUNE or second_type_effectiveness == const.IMMUNE:
        return None
    
    if move.move_type in const.SPECIAL_TYPES:
        attacking_stat = attacking_battle_stats.special
        defending_stat = defending_battle_stats.special
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
    
    return DamageRange(damage_vals)

