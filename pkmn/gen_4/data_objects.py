from __future__ import annotations
import math
import copy
from typing import Dict
import logging
from pkmn.universal_data_objects import Nature, StatBlock

from utils.constants import const
from pkmn.gen_4.gen_four_constants import gen_four_const
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

# special table, relying on bulbapedia for values
# https://bulbapedia.bulbagarden.net/wiki/Prize_money#Core_series_games_2
BLACKOUT_BASE_VALS = {
    0: 8,
    1: 16,
    2: 32,
    3: 36,
    4: 48,
    5: 60,
    6: 80,
    7: 100,
    8: 120,
}


class GenFourBadgeList(universal_data_objects.BadgeList):
    def __init__(
        self, badge_rewards,
        coal=False, forest=False, cobble=False, fen=False, relic=False, mine=False, icicle=False, beacon=False,
        zephyr=False, hive=False, plain=False, fog=False, storm=False, mineral=False, glacier=False, rising=False,
        boulder=False, cascade=False, thunder=False, rainbow=False, soul=False, marsh=False, volcano=False, earth=False,
    ):
        self._badge_rewards:Dict[str, str] = badge_rewards

        self.coal = coal
        self.forest = forest
        self.cobble = cobble
        self.fen = fen
        self.relic = relic
        self.mine = mine
        self.icicle = icicle
        self.beacon = beacon

        self.zephyr = zephyr
        self.hive = hive
        self.plain = plain
        self.fog = fog
        self.storm = storm
        self.mineral = mineral
        self.glacier = glacier
        self.rising = rising

        self.boulder = boulder
        self.cascade = cascade
        self.thunder = thunder
        self.rainbow = rainbow
        self.soul = soul
        self.marsh = marsh
        self.volcano = volcano
        self.earth = earth

    def award_badge(self, trainer_name) -> GenFourBadgeList:
        reward = self._badge_rewards.get(trainer_name)
        result = self.copy()
        if reward == gen_four_const.COAL_BADGE:
            result.zephyr = True
        elif reward == gen_four_const.FOREST_BADGE:
            result.hive = True
        elif reward == gen_four_const.COBBLE_BADGE:
            result.plain = True
        elif reward == gen_four_const.FEN_BADGE:
            result.fog = True
        elif reward == gen_four_const.RELIC_BADGE:
            result.storm = True
        elif reward == gen_four_const.MINE_BADGE:
            result.mineral = True
        elif reward == gen_four_const.ICICLE_BADGE:
            result.glacier = True
        elif reward == gen_four_const.BEACON_BADGE:
            result.rising = True

        elif reward == gen_four_const.ZEPHYR_BADGE:
            result.zephyr = True
        elif reward == gen_four_const.HIVE_BADGE:
            result.hive = True
        elif reward == gen_four_const.PLAIN_BADGE:
            result.plain = True
        elif reward == gen_four_const.FOG_BADGE:
            result.fog = True
        elif reward == gen_four_const.STORM_BADGE:
            result.storm = True
        elif reward == gen_four_const.MINERAL_BADGE:
            result.mineral = True
        elif reward == gen_four_const.GLACIER_BADGE:
            result.glacier = True
        elif reward == gen_four_const.RISING_BADGE:
            result.rising = True

        elif reward == gen_four_const.BOULDER_BADGE:
            result.boulder = True
        elif reward == gen_four_const.CASCADE_BADGE:
            result.cascade = True
        elif reward == gen_four_const.THUNDER_BADGE:
            result.thunder = True
        elif reward == gen_four_const.RAINDBOW_BADGE:
            result.rainbow = True
        elif reward == gen_four_const.SOUL_BADGE:
            result.soul = True
        elif reward == gen_four_const.MARSH_BADGE:
            result.marsh = True
        elif reward == gen_four_const.VOLCANO_BADGE:
            result.volcano = True
        elif reward == gen_four_const.EARTH_BADGE:
            result.earth = True
        else:
            return self

        return result

    def is_attack_boosted(self):
        return False

    def is_defense_boosted(self):
        return False
    
    def is_speed_boosted(self):
        return False
    
    def is_special_attack_boosted(self):
        return False

    def is_special_defense_boosted(self):
        return False
    
    def copy(self) -> GenFourBadgeList:
        return GenFourBadgeList(
            self._badge_rewards,
            coal=self.coal, forest=self.forest, cobble=self.cobble, fen=self.fen, relic=self.relic, mine=self.mine, icicle=self.icicle, beacon=self.beacon,
            zephyr=self.zephyr, hive=self.hive, plain=self.plain, fog=self.fog, storm=self.storm, mineral=self.mineral, glacier=self.glacier, rising=self.rising,
            boulder=self.boulder, cascade=self.cascade, thunder=self.thunder, rainbow=self.rainbow, soul=self.soul, marsh=self.marsh, volcano=self.volcano, earth=self.earth,
        )
    
    def to_string(self, verbose=False):
        if not verbose:
            result = []
            if self.coal:
                result.append("Coal")
            if self.forest:
                result.append("Forest")
            if self.cobble:
                result.append("Cobble")
            if self.fen:
                result.append("Fen")
            if self.relic:
                result.append("Relic")
            if self.mine:
                result.append("Mine")
            if self.icicle:
                result.append("Icicle")
            if self.beacon:
                result.append("Beacon")

            if self.zephyr:
                result.append("Zephr")
            if self.hive:
                result.append("Hive")
            if self.plain:
                result.append("Plain")
            if self.fog:
                result.append("Fog")
            if self.storm:
                result.append("Storm")
            if self.mineral:
                result.append("Mineral")
            if self.glacier:
                result.append("Glacier")
            if self.rising:
                result.append("Rising")

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
            result = f"Coal: {self.coal}, Forest: {self.forest}, Cobble: {self.cobble}, Fen: {self.fen}, Relic: {self.relic}, Mine: {self.mine}, Icicle: {self.icicle}, Beacon: {self.beacon}, "
            result += f"Zephyr: {self.zephyr}, Hive: {self.hive}, Plain: {self.plain}, Fog: {self.fog}, Storm: {self.storm}, Mineral: {self.mineral}, Glacier: {self.glacier}, Rising: {self.rising}, "
            return result + f"Boulder: {self.boulder}, Cascade: {self.cascade}, Thunder: {self.thunder}, Rainbow: {self.rainbow}, Soul: {self.soul}, Marsh: {self.marsh}, Volcano: {self.volcano}, Earth: {self.earth}"
    
    def __repr__(self):
        return self.to_string(verbose=True)
    
    def __eq__(self, other):
        if not isinstance(other, GenFourBadgeList):
            return False
        
        return (
            self.coal == other.coal and
            self.forest == other.forest and
            self.cobble == other.cobble and
            self.fen == other.fen and
            self.relic == other.relic and
            self.mine == other.mine and
            self.icicle == other.icicle and
            self.beacon == other.beacon and

            self.zephyr == other.zephyr and
            self.hive == other.hive and
            self.plain == other.plain and
            self.fog == other.fog and
            self.storm == other.storm and
            self.mineral == other.mineral and
            self.glacier == other.glacier and
            self.rising == other.rising and

            self.boulder == other.boulder and
            self.cascade == other.cascade and
            self.thunder == other.thunder and
            self.rainbow == other.rainbow and
            self.soul == other.soul and
            self.marsh == other.marsh and
            self.volcano == other.volcano and
            self.earth == other.earth
        )

    def num_badges(self):
        result = 0
        for cur_badge in [
            self.coal, self.forest, self.cobble, self.fen, self.relic, self.mine, self.icicle, self.beacon,
            self.zephyr, self.hive, self.plain, self.fog, self.storm, self.mineral, self.glacier, self.rising,
            self.boulder, self.cascade, self.thunder, self.rainbow, self.soul, self.marsh, self.volcano, self.earth,
        ]:
            if cur_badge:
                result += 1

        return result


class GenFourStatBlock(universal_data_objects.StatBlock):
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
        stat_dv:GenFourStatBlock,
        stat_xp:GenFourStatBlock,
        badges:GenFourBadgeList,
        nature:Nature,
        held_item:str
    ) -> GenFourStatBlock:
        # assume self is base stats, level is target level, stat_xp is StatBlock of stat_xp vals, badges is a BadgeList
        speed_stat = calc_stat(
            self.speed,
            level,
            stat_dv.speed,
            stat_xp.speed,
            nature_raised=nature.is_stat_raised(const.SPEED),
            nature_lowered=nature.is_stat_lowered(const.SPEED),
        )
        if held_item == const.MACHO_BRACE_ITEM_NAME:
            speed_stat = math.floor(speed_stat / 2)

        return GenFourStatBlock(
            calc_stat(self.hp, level, stat_dv.hp, stat_xp.hp, is_hp=True),
            calc_stat(
                self.attack,
                level,
                stat_dv.attack,
                stat_xp.attack,
                nature_raised=nature.is_stat_raised(const.ATTACK),
                nature_lowered=nature.is_stat_lowered(const.ATTACK),
            ),
            calc_stat(
                self.defense,
                level,
                stat_dv.defense,
                stat_xp.defense,
                nature_raised=nature.is_stat_raised(const.DEFENSE),
                nature_lowered=nature.is_stat_lowered(const.DEFENSE),
            ),
            calc_stat(
                self.special_attack,
                level,
                stat_dv.special_attack,
                stat_xp.special_attack,
                nature_raised=nature.is_stat_raised(const.SPECIAL_ATTACK),
                nature_lowered=nature.is_stat_lowered(const.SPECIAL_ATTACK),
            ),
            calc_stat(
                self.special_defense,
                level,
                stat_dv.special_defense,
                stat_xp.special_defense,
                nature_raised=nature.is_stat_raised(const.SPECIAL_DEFENSE),
                nature_lowered=nature.is_stat_lowered(const.SPECIAL_DEFENSE),
            ),
            speed_stat,
        )

    def calc_battle_stats(
        self,
        level:int,
        stat_dv:GenFourStatBlock,
        stat_xp:GenFourStatBlock,
        stage_modifiers:universal_data_objects.StageModifiers,
        badges:GenFourBadgeList,
        nature:Nature,
        held_item:str,
        is_crit=False,
        field_status:universal_data_objects.FieldStatus=None,
    ) -> GenFourStatBlock:
        # create a result object, to populate
        result = GenFourStatBlock(
            calc_stat(self.hp, level, stat_dv.hp, stat_xp.hp, is_hp=True),
            0, 0, 0, 0, 0
        )
        if field_status is None:
            field_status = universal_data_objects.FieldStatus()

        result.attack = calc_battle_stat(
            self.attack,
            level,
            stat_dv.attack,
            stat_xp.attack,
            0,
            nature_raised=nature.is_stat_raised(const.ATTACK),
            nature_lowered=nature.is_stat_lowered(const.ATTACK),
        )

        result.defense = calc_battle_stat(
            self.defense,
            level,
            stat_dv.defense,
            stat_xp.defense,
            stage_modifiers.defense_stage,
            nature_raised=nature.is_stat_raised(const.DEFENSE),
            nature_lowered=nature.is_stat_lowered(const.DEFENSE),
        )

        result.speed = calc_battle_stat(
            self.speed,
            level,
            stat_dv.speed,
            stat_xp.speed,
            stage_modifiers.speed_stage,
            nature_raised=nature.is_stat_raised(const.SPEED),
            nature_lowered=nature.is_stat_lowered(const.SPEED),
            slowed_speed=(held_item in const.SPEED_SLOWING_ITEMS),
            choice_scarf=held_item == const.CHOICE_SCARF_ITEM_NAME,
        )

        result.special_attack = calc_battle_stat(
            self.special_attack,
            level,
            stat_dv.special_attack,
            stat_xp.special_attack,
            0,
            nature_raised=nature.is_stat_raised(const.SPECIAL_ATTACK),
            nature_lowered=nature.is_stat_lowered(const.SPECIAL_ATTACK),
        )

        result.special_defense = calc_battle_stat(
            self.special_defense,
            level,
            stat_dv.special_defense,
            stat_xp.special_defense,
            stage_modifiers.special_defense_stage,
            nature_raised=nature.is_stat_raised(const.SPECIAL_DEFENSE),
            nature_lowered=nature.is_stat_lowered(const.SPECIAL_DEFENSE),
        )

        if field_status.power_trick:
            result.attack, result.special_attack = result.special_attack, result.attack

        if field_status.slow_start:
            result.attack = int(result.attack / 2)
            result.special_attack = int(result.special_attack / 2)
            result.speed = int(result.speed / 2)

        result.attack = modify_stat_by_stage(result.attack, stage_modifiers.attack_stage)
        result.special_attack = modify_stat_by_stage(result.special_attack, stage_modifiers.special_attack_stage)

        if field_status.tailwind:
            result.speed *= 2

        if field_status.trick_room:
            result.speed = (10_000 - result.speed) % 8_192

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

        return GenFourStatBlock(
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


def calc_battle_stat(base_val, level, dv, stat_xp, stage, nature_raised=False, nature_lowered=False, slowed_speed=False, choice_scarf=False):
    """
    Fully recalculates a stat that has been modified by a stage modifier. This is the
    primary function that should be used when a pokemon's stat's stage has changed, 
    and needs to be recalculated
    """
    result = calc_unboosted_stat(base_val, level, dv, stat_xp, nature_raised=nature_raised, nature_lowered=nature_lowered)
    if slowed_speed:
        result = math.floor(result / 2)
    if choice_scarf:
        result = math.floor(result * 1.5)

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


def calc_stat(base_val, level, dv, stat_xp, is_hp=False, nature_raised=False, nature_lowered=False):
    result = calc_unboosted_stat(base_val, level, dv, stat_xp, is_hp=is_hp, nature_raised=nature_raised, nature_lowered=nature_lowered)

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


def instantiate_trainer_pokemon(pkmn_data:universal_data_objects.PokemonSpecies, target_level, special_moves=None, nature:Nature=Nature.HARDY) -> universal_data_objects.EnemyPkmn:
    return universal_data_objects.EnemyPkmn(
        pkmn_data.name,
        target_level,
        universal_utils.calc_xp_yield(pkmn_data.base_xp, target_level, True),
        get_move_list(pkmn_data.initial_moves, pkmn_data.levelup_moves, target_level, special_moves=special_moves),
        GenFourStatBlock(
            calc_stat(pkmn_data.stats.hp, target_level, 8, 0, is_hp=True),
            calc_stat(pkmn_data.stats.attack, target_level, 9, 0, nature_raised=nature.is_stat_raised(const.ATTACK), nature_lowered=nature.is_stat_lowered(const.ATTACK)),
            calc_stat(pkmn_data.stats.defense, target_level, 8, 0, nature_raised=nature.is_stat_raised(const.DEFENSE), nature_lowered=nature.is_stat_lowered(const.DEFENSE)),
            calc_stat(pkmn_data.stats.special_attack, target_level, 8, 0, nature_raised=nature.is_stat_raised(const.SPECIAL_ATTACK), nature_lowered=nature.is_stat_lowered(const.SPECIAL_ATTACK)),
            calc_stat(pkmn_data.stats.special_defense, target_level, 8, 0, nature_raised=nature.is_stat_raised(const.SPECIAL_DEFENSE), nature_lowered=nature.is_stat_lowered(const.SPECIAL_DEFENSE)),
            calc_stat(pkmn_data.stats.speed, target_level, 8, 0, nature_raised=nature.is_stat_raised(const.SPEED), nature_lowered=nature.is_stat_lowered(const.SPEED)),
        ),
        pkmn_data.stats,
        GenFourStatBlock(8, 9, 8, 8, 8, 8),
        GenFourStatBlock(0, 0, 0, 0, 0, 0, is_stat_xp=True),
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
        GenFourStatBlock(
            calc_stat(pkmn_data.stats.hp, target_level, 15, 0, is_hp=True),
            calc_stat(pkmn_data.stats.attack, target_level, 15, 0, nature_raised=nature.is_stat_raised(const.ATTACK), nature_lowered=nature.is_stat_lowered(const.ATTACK)),
            calc_stat(pkmn_data.stats.defense, target_level, 15, 0, nature_raised=nature.is_stat_raised(const.DEFENSE), nature_lowered=nature.is_stat_lowered(const.DEFENSE)),
            calc_stat(pkmn_data.stats.special_attack, target_level, 15, 0, nature_raised=nature.is_stat_raised(const.SPECIAL_ATTACK), nature_lowered=nature.is_stat_lowered(const.SPECIAL_ATTACK)),
            calc_stat(pkmn_data.stats.special_defense, target_level, 15, 0, nature_raised=nature.is_stat_raised(const.SPECIAL_DEFENSE), nature_lowered=nature.is_stat_lowered(const.SPECIAL_DEFENSE)),
            calc_stat(pkmn_data.stats.speed, target_level, 15, 0, nature_raised=nature.is_stat_raised(const.SPEED), nature_lowered=nature.is_stat_lowered(const.SPEED)),
        ),
        pkmn_data.stats,
        GenFourStatBlock(15, 15, 15, 15, 15, 15),
        GenFourStatBlock(0, 0, 0, 0, 0, 0, is_stat_xp=True),
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
