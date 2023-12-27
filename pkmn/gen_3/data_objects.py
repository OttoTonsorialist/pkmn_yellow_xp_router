from __future__ import annotations
import math
import copy
from typing import Dict
import logging
from pkmn.universal_data_objects import Nature, StatBlock

from utils.constants import const
from pkmn.gen_3.gen_three_constants import gen_three_const
from pkmn import universal_data_objects, universal_utils

logger = logging.getLogger(__name__)

VIT_AMT = 10
VIT_CAP = 100
SINGLE_STAT_EV_CAP = 255
TOTAL_EV_CAP = 510

STAT_MIN = 1
STAT_MAX = 999
BASE_STAGE_INDEX = 6
STAGE_MOFIDIERS = [
    (2, 8),
    (2, 7),
    (2, 6),
    (2, 5),
    (2, 4),
    (2, 3),
    (2, 2),
    (3, 2),
    (4, 2),
    (5, 2),
    (6, 2),
    (7, 2),
    (8, 2),
]


class GenThreeBadgeList(universal_data_objects.BadgeList):
    def __init__(
        self, badge_rewards,
        stone=False, knuckle=False, dynamo=False, heat=False, balance=False, feather=False, mind=False, rain=False,
        boulder=False, cascade=False, thunder=False, rainbow=False, soul=False, marsh=False, volcano=False, earth=False
    ):
        self._badge_rewards:Dict[str, str] = badge_rewards

        self.stone = stone
        self.knuckle = knuckle
        self.dynamo = dynamo
        self.heat = heat
        self.balance = balance
        self.feather = feather
        self.mind = mind
        self.rain = rain

        self.boulder = boulder
        self.cascade = cascade
        self.thunder = thunder
        self.rainbow = rainbow
        self.soul = soul
        self.marsh = marsh
        self.volcano = volcano
        self.earth = earth
    
    def award_badge(self, trainer_name) -> GenThreeBadgeList:
        reward = self._badge_rewards.get(trainer_name)
        result = self.copy()
        if reward == gen_three_const.STONE_BADGE:
            result.stone = True
        elif reward == gen_three_const.KNUCKLE_BADGE:
            result.knuckle = True
        elif reward == gen_three_const.DYNAMO_BADGE:
            result.dynamo = True
        elif reward == gen_three_const.HEAT_BADGE:
            result.heat = True
        elif reward == gen_three_const.BALANCE_BADGE:
            result.balance = True
        elif reward == gen_three_const.FEATHER_BADGE:
            result.feather = True
        elif reward == gen_three_const.MIND_BADGE:
            result.mind = True
        elif reward == gen_three_const.RAIN_BADGE:
            result.rain = True

        elif reward == gen_three_const.BOULDER_BADGE:
            result.boulder = True
        elif reward == gen_three_const.CASCADE_BADGE:
            result.cascade = True
        elif reward == gen_three_const.THUNDER_BADGE:
            result.thunder = True
        elif reward == gen_three_const.RAINDBOW_BADGE:
            result.rainbow = True
        elif reward == gen_three_const.SOUL_BADGE:
            result.soul = True
        elif reward == gen_three_const.MARSH_BADGE:
            result.marsh = True
        elif reward == gen_three_const.VOLCANO_BADGE:
            result.volcano = True
        elif reward == gen_three_const.EARTH_BADGE:
            result.earth = True
        else:
            return self
        
        return result
    
    def is_attack_boosted(self):
        return self.stone or self.boulder
    
    def is_defense_boosted(self):
        return self.balance or self.soul
    
    def is_speed_boosted(self):
        return self.dynamo or self.thunder
    
    def is_special_attack_boosted(self):
        return self.mind or self.volcano

    def is_special_defense_boosted(self):
        return self.mind or self.volcano
    
    def copy(self) -> GenThreeBadgeList:
        return GenThreeBadgeList(
            self._badge_rewards,
            stone=self.stone,
            knuckle=self.knuckle,
            dynamo=self.dynamo,
            heat=self.heat,
            balance=self.balance,
            feather=self.feather,
            mind=self.mind,
            rain=self.rain,

            boulder=self.boulder,
            cascade=self.cascade,
            thunder=self.thunder,
            rainbow=self.rainbow,
            soul=self.soul,
            marsh=self.marsh,
            volcano=self.volcano,
            earth=self.earth
        )
    
    def to_string(self, verbose=False):
        if not verbose:
            result = []
            if self.stone:
                result.append("Stone")
            if self.knuckle:
                result.append("Knuckle")
            if self.dynamo:
                result.append("Dynamo")
            if self.heat:
                result.append("Heat")
            if self.balance:
                result.append("Balance")
            if self.feather:
                result.append("Feather")
            if self.mind:
                result.append("Mind")
            if self.rain:
                result.append("Rain")

            if self.boulder:
                result.append("Boulder")
            if self.cascade:
                result.append("Cascade")
            if self.thunder:
                result.append("Thunder")
            if self.rainbow:
                result.append("Rainbow")
            if self.soul:
                result.append("Soul")
            if self.marsh:
                result.append("Marsh")
            if self.volcano:
                result.append("Volcano")
            if self.earth:
                result.append("Earth")

            return "Badges: " + ", ".join(result)
        else:
            result = f"Stone: {self.stone}, Knuckle: {self.knuckle}, Dynamo: {self.dynamo}, Heat: {self.heat}, Balance: {self.balance}, Feather: {self.feather}, Mind: {self.mind}, Rain: {self.rain}, "
            return result + f"Boulder: {self.boulder}, Cascade: {self.cascade}, Thunder: {self.thunder}, Rainbow: {self.rainbow}, Soul: {self.soul}, Marsh: {self.marsh}, Volcano: {self.volcano}, Earth: {self.earth}"
    
    def __repr__(self):
        return self.to_string(verbose=True)
    
    def __eq__(self, other):
        if not isinstance(other, GenThreeBadgeList):
            return False
        
        return (
            self.stone == other.stone and
            self.knuckle == other.knuckle and
            self.dynamo == other.dynamo and
            self.heat == other.heat and
            self.balance == other.balance and
            self.feather == other.feather and
            self.mind == other.mind and
            self.rain == other.rain and

            self.boulder == other.boulder and
            self.cascade == other.cascade and
            self.thunder == other.thunder and
            self.rainbow == other.rainbow and
            self.soul == other.soul and
            self.marsh == other.marsh and
            self.volcano == other.volcano and
            self.earth == other.earth
        )


class GenThreeStatBlock(universal_data_objects.StatBlock):
    def __init__(self, hp, attack, defense, special_attack, special_defense, speed, is_stat_xp=False):
        super().__init__(hp, attack, defense, special_attack, special_defense, speed, is_stat_xp=is_stat_xp)

        # hard cap STAT XP vals
        if is_stat_xp:
            cur_ev_total = 0
            self.hp, cur_ev_total = self._get_actual_addable_evs(0, hp, cur_ev_total)
            self.attack, cur_ev_total= self._get_actual_addable_evs(0, attack, cur_ev_total)
            self.defense, cur_ev_total = self._get_actual_addable_evs(0, defense, cur_ev_total)
            self.speed, cur_ev_total = self._get_actual_addable_evs(0, speed, cur_ev_total)
            self.special_attack, cur_ev_total = self._get_actual_addable_evs(0, special_attack, cur_ev_total)
            self.special_defense, cur_ev_total = self._get_actual_addable_evs(0, special_defense, cur_ev_total)
    
    def calc_level_stats(
        self,
        level:int,
        stat_dv:GenThreeStatBlock,
        stat_xp:GenThreeStatBlock,
        badges:GenThreeBadgeList,
        nature:Nature,
        held_item:str
    ) -> GenThreeStatBlock:
        # assume self is base stats, level is target level, stat_xp is StatBlock of stat_xp vals, badges is a BadgeList
        speed_stat = calc_stat(
            self.speed,
            level,
            stat_dv.speed,
            stat_xp.speed,
            is_badge_boosted=badges.is_speed_boosted(),
            nature_raised=nature.is_stat_raised(const.SPEED),
            nature_lowered=nature.is_stat_lowered(const.SPEED),
        )
        if held_item == const.MACHO_BRACE_ITEM_NAME:
            speed_stat = math.floor(speed_stat / 2)

        return GenThreeStatBlock(
            calc_stat(self.hp, level, stat_dv.hp, stat_xp.hp, is_hp=True),
            calc_stat(
                self.attack,
                level,
                stat_dv.attack,
                stat_xp.attack,
                is_badge_boosted=badges.is_attack_boosted(),
                nature_raised=nature.is_stat_raised(const.ATTACK),
                nature_lowered=nature.is_stat_lowered(const.ATTACK),
            ),
            calc_stat(
                self.defense,
                level,
                stat_dv.defense,
                stat_xp.defense,
                is_badge_boosted=badges.is_defense_boosted(),
                nature_raised=nature.is_stat_raised(const.DEFENSE),
                nature_lowered=nature.is_stat_lowered(const.DEFENSE),
            ),
            calc_stat(
                self.special_attack,
                level,
                stat_dv.special_attack,
                stat_xp.special_attack,
                is_badge_boosted=badges.is_special_attack_boosted(),
                nature_raised=nature.is_stat_raised(const.SPECIAL_ATTACK),
                nature_lowered=nature.is_stat_lowered(const.SPECIAL_ATTACK),
            ),
            calc_stat(
                self.special_defense,
                level,
                stat_dv.special_defense,
                stat_xp.special_defense,
                is_badge_boosted=badges.is_special_defense_boosted(),
                nature_raised=nature.is_stat_raised(const.SPECIAL_DEFENSE),
                nature_lowered=nature.is_stat_lowered(const.SPECIAL_DEFENSE),
            ),
            speed_stat,
        )
    
    def calc_battle_stats(
        self,
        level:int,
        stat_dv:GenThreeStatBlock,
        stat_xp:GenThreeStatBlock,
        stage_modifiers:universal_data_objects.StageModifiers,
        badges:GenThreeBadgeList,
        nature:Nature,
        held_item:str,
        is_crit=False
    ) -> GenThreeStatBlock:
        if is_crit:
            # NOTE: Right now, we are relying on the damage calculator in pkmn_damage_calc to determine
            # whether the stage modifiers should be modified on a crit. Only the damage calculator can
            # do this, because it has the move in question. As such, we are assuming for a crit that
            # the stage_modifiers passed in are always correct. Instead, the is_crit flag will serve
            # to disable the badge boosts 
            # This does mean that sometimes the damage calculator will "lie" to this function when a crit
            # is happening, but we want the badge boosts (which can happen when the stage modifiers favor the attacker)

            # since this is just a badge boost flag now, disable all badge boosts when it's passed in
            if badges is not None:
                badges = GenThreeBadgeList(badges._badge_rewards)

        # create a result object, to populate
        result = GenThreeStatBlock(
            calc_stat(self.hp, level, stat_dv.hp, stat_xp.hp, is_hp=True),
            0, 0, 0, 0, 0
        )

        result.attack = calc_battle_stat(
            self.attack,
            level,
            stat_dv.attack,
            stat_xp.attack,
            stage_modifiers.attack_stage,
            is_badge_boosted=(badges is not None and badges.is_attack_boosted()),
            nature_raised=nature.is_stat_raised(const.ATTACK),
            nature_lowered=nature.is_stat_lowered(const.ATTACK),
        )

        result.defense = calc_battle_stat(
            self.defense,
            level,
            stat_dv.defense,
            stat_xp.defense,
            stage_modifiers.defense_stage,
            is_badge_boosted=(badges is not None and badges.is_defense_boosted()),
            nature_raised=nature.is_stat_raised(const.DEFENSE),
            nature_lowered=nature.is_stat_lowered(const.DEFENSE),
        )

        result.speed = calc_battle_stat(
            self.speed,
            level,
            stat_dv.speed,
            stat_xp.speed,
            stage_modifiers.speed_stage,
            is_badge_boosted=(badges is not None and badges.is_speed_boosted()),
            nature_raised=nature.is_stat_raised(const.SPEED),
            nature_lowered=nature.is_stat_lowered(const.SPEED),
            macho_brace=held_item == const.MACHO_BRACE_ITEM_NAME
        )

        result.special_attack = calc_battle_stat(
            self.special_attack,
            level,
            stat_dv.special_attack,
            stat_xp.special_attack,
            stage_modifiers.special_attack_stage,
            is_badge_boosted=(badges is not None and badges.is_special_attack_boosted()),
            nature_raised=nature.is_stat_raised(const.SPECIAL_ATTACK),
            nature_lowered=nature.is_stat_lowered(const.SPECIAL_ATTACK),
        )

        result.special_defense = calc_battle_stat(
            self.special_defense,
            level,
            stat_dv.special_defense,
            stat_xp.special_defense,
            stage_modifiers.special_defense_stage,
            is_badge_boosted=(badges is not None and badges.is_special_defense_boosted()),
            nature_raised=nature.is_stat_raised(const.SPECIAL_DEFENSE),
            nature_lowered=nature.is_stat_lowered(const.SPECIAL_DEFENSE),
        )

        return result

    def add(self, other: StatBlock) -> StatBlock:
        if not self._is_stat_xp:
            return super().add(other)

        if not isinstance(other, StatBlock):
            raise ValueError(f"Cannot add type: {type(other)} to StatBlock")

        cur_ev_total = self.hp + self.attack + self.defense + self.special_attack + self.special_defense + self.speed
        cur_ev_total = min(cur_ev_total, TOTAL_EV_CAP)

        # Add to each EV in RAM order. If any EV tries to go over the single stat cap, prevent it
        # then add those evs to the current toal. If any EV tries to go over the total EV cap, prevent it
        addable_hp, cur_ev_total = self._get_actual_addable_evs(self.hp, other.hp, cur_ev_total)
        addable_attack, cur_ev_total = self._get_actual_addable_evs(self.attack, other.attack, cur_ev_total)
        addable_defense, cur_ev_total = self._get_actual_addable_evs(self.defense, other.defense, cur_ev_total)
        addable_speed, cur_ev_total = self._get_actual_addable_evs(self.speed, other.speed, cur_ev_total)
        addable_special_attack, cur_ev_total = self._get_actual_addable_evs(self.special_attack, other.special_attack, cur_ev_total)
        addable_special_defense, cur_ev_total = self._get_actual_addable_evs(self.special_defense, other.special_defense, cur_ev_total)

        return GenThreeStatBlock(
            self.hp + addable_hp,
            self.attack + addable_attack,
            self.defense + addable_defense,
            self.special_attack + addable_special_attack,
            self.special_defense + addable_special_defense,
            self.speed + addable_speed,
            is_stat_xp=self._is_stat_xp
        )

    @staticmethod
    def _get_actual_addable_evs(cur_stat_ev, new_stat_ev, cur_total_ev):
        actual_new_ev = min(cur_stat_ev + new_stat_ev, SINGLE_STAT_EV_CAP) - cur_stat_ev
        actual_new_ev = max(actual_new_ev, 0)
        actual_new_ev = min(cur_total_ev + actual_new_ev, TOTAL_EV_CAP) - cur_total_ev
        actual_new_ev = max(actual_new_ev, 0)

        return actual_new_ev, (cur_total_ev + actual_new_ev)


def calc_battle_stat(base_val, level, dv, stat_xp, stage, is_badge_boosted=False, nature_raised=False, nature_lowered=False, macho_brace=False):
    """
    Fully recalculates a stat that has been modified by a stage modifier. This is the
    primary function that should be used when a pokemon's stat's stage has changed, 
    and needs to be recalculated
    """
    result = calc_unboosted_stat(base_val, level, dv, stat_xp, nature_raised=nature_raised, nature_lowered=nature_lowered)
    if macho_brace:
        result = math.floor(result / 2)

    if is_badge_boosted:
        result = badge_boost_single_stat(result)

    return modify_stat_by_stage(result, stage)


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


def calc_unboosted_stat(base_val, level, iv, ev, is_hp=False, nature_raised=False, nature_lowered=False):
    temp = (2 * base_val) + iv
    temp += math.floor(ev / 4)
    temp = math.floor(temp * level / 100)

    if is_hp:
        return temp + level + 10

    result = temp + 5
    if nature_raised:
        return math.floor(result * 1.1)
    if nature_lowered:
        return math.floor(result * 0.9)

    return result


def calc_stat(base_val, level, dv, stat_xp, is_hp=False, is_badge_boosted=False, nature_raised=False, nature_lowered=False):
    result = calc_unboosted_stat(base_val, level, dv, stat_xp, is_hp=is_hp, nature_raised=nature_raised, nature_lowered=nature_lowered)

    if is_badge_boosted:
        result = badge_boost_single_stat(result)

    return result


def badge_boost_single_stat(cur_stat_val):
    # very basic function, just giving it a name so it's obvious when using the function
    return math.floor(cur_stat_val * 1.1)


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
    

def instantiate_trainer_pokemon(pkmn_data:universal_data_objects.PokemonSpecies, target_level, special_moves=None, nature:Nature=Nature.HARDY) -> universal_data_objects.EnemyPkmn:
    return universal_data_objects.EnemyPkmn(
        pkmn_data.name,
        target_level,
        universal_utils.calc_xp_yield(pkmn_data.base_xp, target_level, True),
        get_move_list(pkmn_data.initial_moves, pkmn_data.levelup_moves, target_level, special_moves=special_moves),
        GenThreeStatBlock(
            calc_stat(pkmn_data.stats.hp, target_level, 8, 0, is_hp=True),
            calc_stat(pkmn_data.stats.attack, target_level, 9, 0, nature_raised=nature.is_stat_raised(const.ATTACK), nature_lowered=nature.is_stat_lowered(const.ATTACK)),
            calc_stat(pkmn_data.stats.defense, target_level, 8, 0, nature_raised=nature.is_stat_raised(const.DEFENSE), nature_lowered=nature.is_stat_lowered(const.DEFENSE)),
            calc_stat(pkmn_data.stats.special_attack, target_level, 8, 0, nature_raised=nature.is_stat_raised(const.SPECIAL_ATTACK), nature_lowered=nature.is_stat_lowered(const.SPECIAL_ATTACK)),
            calc_stat(pkmn_data.stats.special_defense, target_level, 8, 0, nature_raised=nature.is_stat_raised(const.SPECIAL_DEFENSE), nature_lowered=nature.is_stat_lowered(const.SPECIAL_DEFENSE)),
            calc_stat(pkmn_data.stats.speed, target_level, 8, 0, nature_raised=nature.is_stat_raised(const.SPEED), nature_lowered=nature.is_stat_lowered(const.SPEED)),
        ),
        pkmn_data.stats,
        GenThreeStatBlock(8, 9, 8, 8, 8, 8),
        GenThreeStatBlock(0, 0, 0, 0, 0, 0, is_stat_xp=True),
        None,
        is_trainer_mon=True
    )


def instantiate_wild_pokemon(pkmn_data:universal_data_objects.PokemonSpecies, target_level, nature:Nature=Nature.HARDY) -> universal_data_objects.EnemyPkmn:
    # NOTE: wild pokemon have random DVs. just setting to max to get highest possible stats for now
    return universal_data_objects.EnemyPkmn(
        pkmn_data.name,
        target_level,
        universal_utils.calc_xp_yield(pkmn_data.base_xp, target_level, False),
        get_move_list(pkmn_data.initial_moves, pkmn_data.levelup_moves, target_level),
        GenThreeStatBlock(
            calc_stat(pkmn_data.stats.hp, target_level, 15, 0, is_hp=True),
            calc_stat(pkmn_data.stats.attack, target_level, 15, 0, nature_raised=nature.is_stat_raised(const.ATTACK), nature_lowered=nature.is_stat_lowered(const.ATTACK)),
            calc_stat(pkmn_data.stats.defense, target_level, 15, 0, nature_raised=nature.is_stat_raised(const.DEFENSE), nature_lowered=nature.is_stat_lowered(const.DEFENSE)),
            calc_stat(pkmn_data.stats.special_attack, target_level, 15, 0, nature_raised=nature.is_stat_raised(const.SPECIAL_ATTACK), nature_lowered=nature.is_stat_lowered(const.SPECIAL_ATTACK)),
            calc_stat(pkmn_data.stats.special_defense, target_level, 15, 0, nature_raised=nature.is_stat_raised(const.SPECIAL_DEFENSE), nature_lowered=nature.is_stat_lowered(const.SPECIAL_DEFENSE)),
            calc_stat(pkmn_data.stats.speed, target_level, 15, 0, nature_raised=nature.is_stat_raised(const.SPEED), nature_lowered=nature.is_stat_lowered(const.SPEED)),
        ),
        pkmn_data.stats,
        GenThreeStatBlock(15, 15, 15, 15, 15, 15),
        GenThreeStatBlock(0, 0, 0, 0, 0, 0, is_stat_xp=True),
        None,
        is_trainer_mon=False
    )


_HIDDEN_POWER_TABLE = [
    const.TYPE_FIGHTING,
    const.TYPE_FLYING,
    const.TYPE_POISON,
    const.TYPE_GROUND,
    const.TYPE_ROCK,
    const.TYPE_BUG,
    const.TYPE_GHOST,
    const.TYPE_STEEL,
    const.TYPE_FIRE,
    const.TYPE_WATER,
    const.TYPE_GRASS,
    const.TYPE_ELECTRIC,
    const.TYPE_PSYCHIC,
    const.TYPE_ICE,
    const.TYPE_DRAGON,
    const.TYPE_DARK
]
def get_hidden_power_type(dvs:universal_data_objects.StatBlock) -> str:
    result_idx = dvs.hp % 2
    result_idx += (dvs.attack % 2) * 2
    result_idx += (dvs.defense % 2) * 4
    result_idx += (dvs.speed % 2) * 8
    result_idx += (dvs.special_attack % 2) * 16
    result_idx += (dvs.special_defense % 2) * 32

    result_idx *= 15
    result_idx = math.floor(result_idx / 63)
    return _HIDDEN_POWER_TABLE[result_idx]


def _get_power_bit(stat_val):
    # just extracts the second least significant bit
    # i'm sure there's a faster way to do this, but this is easier lol
    return 1 if ((stat_val % 4) >=2) else 0


def get_hidden_power_base_power(dvs:universal_data_objects.StatBlock) -> int:
    result = _get_power_bit(dvs.hp)
    result += _get_power_bit(dvs.attack) * 2
    result += _get_power_bit(dvs.defense) * 4
    result += _get_power_bit(dvs.speed) * 8
    result += _get_power_bit(dvs.special_attack) * 16
    result += _get_power_bit(dvs.special_defense) * 32

    result *= 40
    result = math.floor(result / 63)
    return result + 30
