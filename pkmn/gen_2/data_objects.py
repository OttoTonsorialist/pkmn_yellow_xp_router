from __future__ import annotations
import math
import copy

from utils.constants import const
from pkmn.gen_2.gen_two_constants import gen_two_const
from pkmn import universal_data_objects, universal_utils


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


class GenTwoBadgeList(universal_data_objects.BadgeList):
    def __init__(
        self,
        zephyr=False, hive=False, plain=False, fog=False, storm=False, mineral=False, glacier=False, rising=False,
        efour_will=False, efour_koga=False, efour_bruno=False, efour_karen=False, efour_lance=False,
        boulder=False, cascade=False, thunder=False, rainbow=False, soul=False, marsh=False, volcano=False, earth=False
    ):
        self.zephyr = zephyr
        self.hive = hive
        self.plain = plain
        self.fog = fog
        self.storm = storm
        self.mineral = mineral
        self.glacier = glacier
        self.rising = rising

        self.efour_will = efour_will
        self.efour_koga = efour_koga
        self.efour_bruno = efour_bruno
        self.efour_karen = efour_karen
        self.efour_lance = efour_lance

        self.boulder = boulder
        self.cascade = cascade
        self.thunder = thunder
        self.rainbow = rainbow
        self.soul = soul
        self.marsh = marsh
        self.volcano = volcano
        self.earth = earth
    
    def award_badge(self, trainer_name) -> GenTwoBadgeList:
        reward = gen_two_const.BADGE_REWARDS.get(trainer_name)
        result = self.copy()
        if reward == gen_two_const.ZEPHYR_BADGE:
            result.zephyr = True
        elif reward == gen_two_const.HIVE_BADGE:
            result.hive = True
        elif reward == gen_two_const.PLAIN_BADGE:
            result.plain = True
        elif reward == gen_two_const.FOG_BADGE:
            result.fog = True
        elif reward == gen_two_const.STORM_BADGE:
            result.storm = True
        elif reward == gen_two_const.MINERAL_BADGE:
            result.mineral = True
        elif reward == gen_two_const.GLACIER_BADGE:
            result.glacier = True
        elif reward == gen_two_const.RISING_BADGE:
            result.rising = True

        elif reward == gen_two_const.EFOUR_WILL_BOOST:
            result.efour_will = True
        elif reward == gen_two_const.EFOUR_KOGA_BOOST:
            result.efour_koga = True
        elif reward == gen_two_const.EFOUR_BRUNO_BOOST:
            result.efour_bruno = True
        elif reward == gen_two_const.EFOUR_KAREN_BOOST:
            result.efour_karen = True
        elif reward == gen_two_const.EFOUR_LANCE_BOOST:
            result.efour_lance = True

        elif reward == gen_two_const.BOULDER_BADGE:
            result.boulder = True
        elif reward == gen_two_const.CASCADE_BADGE:
            result.cascade = True
        elif reward == gen_two_const.THUNDER_BADGE:
            result.thunder = True
        elif reward == gen_two_const.RAINDBOW_BADGE:
            result.rainbow = True
        elif reward == gen_two_const.SOUL_BADGE:
            result.soul = True
        elif reward == gen_two_const.MARSH_BADGE:
            result.marsh = True
        elif reward == gen_two_const.VOLCANO_BADGE:
            result.volcano = True
        elif reward == gen_two_const.EARTH_BADGE:
            result.earth = True
        else:
            # no need to hold on to a copy wastefully if no badge was awarded
            return self
        
        return result
    
    def is_attack_boosted(self):
        return self.zephyr
    
    def is_defense_boosted(self):
        return self.mineral
    
    def is_speed_boosted(self):
        return self.plain
    
    def is_special_attack_boosted(self):
        return self.glacier

    def is_special_defense_boosted(self):
        return self.glacier
    
    def copy(self) -> GenTwoBadgeList:
        return GenTwoBadgeList(
            zephyr=self.zephyr,
            hive=self.hive,
            plain=self.plain,
            fog=self.fog,
            storm=self.storm,
            mineral=self.mineral,
            glacier=self.glacier,
            rising=self.rising,

            efour_will=self.efour_will,
            efour_koga=self.efour_koga,
            efour_bruno=self.efour_bruno,
            efour_karen=self.efour_karen,
            efour_lance=self.efour_lance,

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
            result = f"Zephyr: {self.zephyr}, Hive: {self.hive}, Plain: {self.plain}, Fog: {self.fog}, Storm: {self.storm}, Mineral: {self.mineral}, Glacier: {self.glacier}, Rising: {self.rising}, "
            return result + f"Boulder: {self.boulder}, Cascade: {self.cascade}, Thunder: {self.thunder}, Rainbow: {self.rainbow}, Soul: {self.soul}, Marsh: {self.marsh}, Volcano: {self.volcano}, Earth: {self.earth}"
    
    def __repr__(self):
        return self.to_string(verbose=True)
    
    def __eq__(self, other):
        if not isinstance(other, GenTwoBadgeList):
            return False
        
        return (
            self.zephyr == other.zephyr and
            self.hive == other.hive and
            self.plain == other.plain and
            self.fog == other.fog and
            self.storm == other.storm and
            self.mineral == other.mineral and
            self.glacier == other.glacier and
            self.rising == other.rising and

            self.efour_will == other.efour_will and
            self.efour_koga == other.efour_koga and
            self.efour_bruno == other.efour_bruno and
            self.efour_karen == other.efour_karen and
            self.efour_lance == other.efour_lance and

            self.boulder == other.boulder and
            self.cascade == other.cascade and
            self.thunder == other.thunder and
            self.rainbow == other.rainbow and
            self.soul == other.soul and
            self.marsh == other.marsh and
            self.volcano == other.volcano and
            self.earth == other.earth
        )


class GenTwoStatBlock(universal_data_objects.StatBlock):
    def __init__(self, hp, attack, defense, special_attack, special_defense, speed, is_stat_xp=False):
        super().__init__(hp, attack, defense, special_attack, special_defense, speed, is_stat_xp=False)

        # NOTE: Although GenTwo introduces special attack and special defense as separate stats,
        # GenTwo only has one DV/StatXP val for both special stats, using special_attack for both of them

        # hard cap STAT XP vals
        if is_stat_xp:
            self.hp = min(hp, STAT_XP_CAP)
            self.attack = min(attack, STAT_XP_CAP)
            self.defense = min(defense, STAT_XP_CAP)
            self.speed = min(speed, STAT_XP_CAP)
            self.special_attack = min(special_attack, STAT_XP_CAP)
            self.special_defense = min(special_defense, STAT_XP_CAP)
    
    def calc_level_stats(
        self,
        level:int,
        stat_dv:GenTwoStatBlock,
        stat_xp:GenTwoStatBlock,
        badges:GenTwoBadgeList
    ) -> GenTwoStatBlock:
        # assume self is base stats, level is target level, stat_xp is StatBlock of stat_xp vals, badges is a BadgeList
        return GenTwoStatBlock(
            calc_stat(self.hp, level, stat_dv.hp, stat_xp.hp, is_hp=True),
            calc_stat(self.attack, level, stat_dv.attack, stat_xp.attack, is_badge_bosted=badges.zephyr),
            calc_stat(self.defense, level, stat_dv.defense, stat_xp.defense, is_badge_bosted=badges.mineral),
            calc_stat(self.special_attack, level, stat_dv.special_attack, stat_xp.special_attack, is_badge_bosted=badges.glacier),
            calc_stat(self.special_defense, level, stat_dv.special_attack, stat_xp.special_attack, is_badge_bosted=badges.glacier),
            calc_stat(self.speed, level, stat_dv.speed, stat_xp.speed, is_badge_bosted=badges.plain),
        )
    
    def calc_battle_stats(
        self,
        level:int,
        stat_dv:GenTwoStatBlock,
        stat_xp:GenTwoStatBlock,
        stage_modifiers:universal_data_objects.StageModifiers,
        badges:GenTwoBadgeList,
        is_crit=False
    ) -> GenTwoStatBlock:
        if is_crit:
            # NOTE: right now, only the solo mon's stats can be modified, so this approximation works
            # but it's not a "full" solution if we were to support a full battle simulator
            # in that case we would have to restructure more of how this works

            # crits ignore modifiers if the effective stages would make the damage worse
            # since the enemy is always neutral, just correct to 0

            # correct attack/spa up (ignore negative penalties on crit)
            # correct defense/spd down (ignore positive penalties on enemy crit)
            stage_modifiers = universal_data_objects.StageModifiers(
                attack=max(0, stage_modifiers.attack_stage),
                defense=min(0, stage_modifiers.defense_stage),
                speed=stage_modifiers.speed_stage,
                special_attack=max(0, stage_modifiers.special_attack_stage),
                special_defense=min(0, stage_modifiers.special_defense_stage),
                accuracy=stage_modifiers.accuracy_stage,
                evasion=stage_modifiers.evasion_stage
            )

        # create a result object, to populate
        result = GenTwoStatBlock(
            calc_stat(self.hp, level, stat_dv.hp, stat_xp.hp, is_hp=True),
            0, 0, 0, 0, 0
        )

        result.attack = calc_battle_stat(
            self.attack,
            level,
            stat_dv.attack,
            stat_xp.attack,
            stage_modifiers.attack_stage,
            is_badge_boosted=(badges is not None and badges.is_attack_boosted())
        )

        result.defense = calc_battle_stat(
            self.defense,
            level,
            stat_dv.defense,
            stat_xp.defense,
            stage_modifiers.defense_stage,
            is_badge_boosted=(badges is not None and badges.is_defense_boosted())
        )

        result.speed = calc_battle_stat(
            self.speed,
            level,
            stat_dv.speed,
            stat_xp.speed,
            stage_modifiers.speed_stage,
            is_badge_boosted=(badges is not None and badges.is_speed_boosted())
        )

        result.special_attack = calc_battle_stat(
            self.special_attack,
            level,
            stat_dv.special_attack,
            stat_xp.special_attack,
            stage_modifiers.special_attack_stage,
            is_badge_boosted=(badges is not None and badges.is_special_attack_boosted())
        )

        result.special_defense = calc_battle_stat(
            self.special_defense,
            level,
            stat_dv.special_attack,
            stat_xp.special_attack,
            stage_modifiers.special_defense_stage,
            is_badge_boosted=(badges is not None and badges.is_special_defense_boosted())
        )

        return result


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

    NOTE: This is the "Normal" case ONLY!  Assuming immunities, fly/dig invlun status, and guaranteed misses/hits
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
    

def instantiate_trainer_pokemon(pkmn_data:universal_data_objects.PokemonSpecies, target_level, special_moves=None) -> universal_data_objects.EnemyPkmn:
    return universal_data_objects.EnemyPkmn(
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


def instantiate_wild_pokemon(pkmn_data:universal_data_objects.PokemonSpecies, target_level) -> universal_data_objects.EnemyPkmn:
    # NOTE: wild pokemon have random DVs. just setting to max to get highest possible stats for now
    return universal_data_objects.EnemyPkmn(
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
    result_idx = 4
    result_idx *= (dvs.attack % 4)
    result_idx += (dvs.defense % 4)

    return _HIDDEN_POWER_TABLE[result_idx]


def get_hidden_power_base_power(dvs:universal_data_objects.StatBlock) -> int:
    # remember that single dv for special is stored in specal_attack
    result = 5 * (1 if dvs.special_attack > 8 else 0)
    result += (dvs.special_attack % 4)
    result = math.floor(result / 2)

    result += 5 * (1 if dvs.speed > 8 else 0)
    result += 10 * (1 if dvs.defense > 8 else 0)
    result += 20 * (1 if dvs.attack > 8 else 0)
    result += 31

    return result
