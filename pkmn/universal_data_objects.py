import copy
from typing import Tuple

from utils.constants import const
import pkmn.pkmn_utils as pkmn_utils


class BadgeList:
    def award_badge(self, trainer_name):
        raise NotImplementedError()
    
    def to_string(self, verbose=False) -> str:
        raise NotImplementedError()
    
class StageModifiers:
    def __init__(self,
        attack=0, defense=0, speed=0, special=0, accuracy=0, evasion=0,
        attack_bb=0, defense_bb=0, speed_bb=0, special_bb=0
    ):
        self.attack_stage = max(min(attack, 6), -6)
        self.defense_stage = max(min(defense, 6), -6)
        self.speed_stage = max(min(speed, 6), -6)
        self.special_stage = max(min(special, 6), -6)
        self.accuracy_stage = max(min(accuracy, 6), -6)
        self.evasion_stage = max(min(evasion, 6), -6)
        # keep track of which badge boosts are applicable to which stats
        # NOTE: this data structure does not care about which badges the player has
        # this tracks "theoretical" badge boosts, which should only apply if the corresponding badge has been earned
        self.attack_badge_boosts = attack_bb
        self.defense_badge_boosts = defense_bb
        self.speed_badge_boosts = speed_bb
        self.special_badge_boosts = special_bb
    
    def _copy_constructor(self):
        return StageModifiers(
            attack=self.attack_stage, defense=self.defense_stage, speed=self.speed_stage,
            special=self.special_stage, accuracy=self.accuracy_stage, evasion=self.evasion_stage,

            attack_bb=self.attack_badge_boosts, defense_bb=self.defense_badge_boosts,
            speed_bb=self.speed_badge_boosts, special_bb=self.special_badge_boosts,
        )
    
    def clear_badge_boosts(self):
        result = self._copy_constructor()

        result.attack_badge_boosts = 0
        result.defense_badge_boosts = 0
        result.speed_badge_boosts = 0
        result.special_badge_boosts = 0

        return result
    
    def _get_stat_mod(self, move_name) -> Tuple[str, int]:
        raise NotImplementedError()
    
    def after_move(self, move_name):
        stat_mod = self._get_stat_mod(move_name)
        if stat_mod is None:
            return self
        
        result = self._copy_constructor()
        result.attack_badge_boosts += 1
        result.defense_badge_boosts += 1
        result.speed_badge_boosts += 1
        result.special_badge_boosts += 1

        # NOTE: a litle bit of implementation jank: attempt to apply boost as defined,
        # NOTE: but if the boost would have no effect, then revert to returning self
        if stat_mod[0] == const.ATK:
            result.attack_stage = max(min(self.attack_stage + stat_mod[1], 6), -6)
            if result.attack_stage == self.attack_stage:
                return self
            result.attack_badge_boosts = 0
        elif stat_mod[0] == const.DEF:
            result.defense_stage = max(min(self.defense_stage + stat_mod[1], 6), -6)
            if result.defense_stage == self.defense_stage:
                return self
            result.defense_badge_boosts = 0
        elif stat_mod[0] == const.SPE:
            result.speed_stage = max(min(self.speed_stage + stat_mod[1], 6), -6)
            if result.speed_stage == self.speed_stage:
                return self
            result.speed_badge_boosts = 0
        elif stat_mod[0] == const.SPC:
            result.special_stage = max(min(self.special_stage + stat_mod[1], 6), -6)
            if result.special_stage == self.special_stage:
                return self
            result.special_badge_boosts = 0
        elif stat_mod[0] == const.ACC:
            result.accuracy_stage = max(min(self.accuracy_stage + stat_mod[1], 6), -6)
            if result.accuracy_stage == self.accuracy_stage:
                return self
        elif stat_mod[0] == const.EV:
            result.evasion_stage = max(min(self.evasion_stage + stat_mod[1], 6), -6)
            if result.evasion_stage == self.evasion_stage:
                return self

        return result

    def __eq__(self, other):
        if not isinstance(other, StageModifiers):
            return False
        
        return (
            self.attack_stage == other.attack_stage and self.attack_badge_boosts == other.attack_badge_boosts and
            self.defense_stage == other.defense_stage and self.defense_badge_boosts == other.defense_badge_boosts and
            self.speed_stage == other.speed_stage and self.speed_badge_boosts == other.speed_badge_boosts and
            self.special_stage == other.special_stage and self.special_badge_boosts == other.special_badge_boosts and
            self.accuracy_stage == other.accuracy_stage and
            self.evasion_stage == other.evasion_stage
        )
    
    def __repr__(self):
        return f"""
            Atk: ({self.attack_stage}, {self.attack_badge_boosts}), 
            Def: ({self.defense_stage}, {self.defense_badge_boosts}), 
            Spd: ({self.speed_stage}, {self.speed_badge_boosts}), 
            Spc: ({self.special_stage}, {self.special_badge_boosts}), 
            Acc: ({self.accuracy_stage}, 0), 
            Evn: ({self.evasion_stage}, 0)
        """


class StatBlock:
    def __init__(self, hp, attack, defense, special_attack, special_defense, speed, is_stat_xp=False):
        self._is_stat_xp = is_stat_xp

        if not is_stat_xp:
            self.hp = hp
            self.attack = attack
            self.defense = defense
            self.speed = speed
            self.special_attack = special_attack
            self.special_defense = special_defense
        else:
            self.hp = min(hp, pkmn_utils.STAT_XP_CAP)
            self.attack = min(attack, pkmn_utils.STAT_XP_CAP)
            self.defense = min(defense, pkmn_utils.STAT_XP_CAP)
            self.speed = min(speed, pkmn_utils.STAT_XP_CAP)
            self.special_attack = min(special_attack, pkmn_utils.STAT_XP_CAP)
            self.special_defense = min(special_defense, pkmn_utils.STAT_XP_CAP)
    
    def add(self, other):
        if not isinstance(other, StatBlock):
            raise ValueError(f"Cannot add type: {type(other)} to StatBlock")
        return StatBlock(
            self.hp + other.hp,
            self.attack + other.attack,
            self.defense + other.defense,
            self.speed + other.speed,
            self.special_attack + other.special_attack,
            self.special_defense + other.special_defense,
            is_stat_xp=self._is_stat_xp
        )
    
    def subtract(self, other):
        if not isinstance(other, StatBlock):
            raise ValueError(f"Cannot subtract type: {type(other)} from StatBlock")
        return StatBlock(
            self.hp - other.hp,
            self.attack - other.attack,
            self.defense - other.defense,
            self.speed - other.speed,
            self.special_attack - other.special_attack,
            self.special_defense - other.special_defense,
            is_stat_xp=self._is_stat_xp
        )
    
    def serialize(self):
        return {
            const.HP: self.hp,
            const.ATK: self.attack,
            const.DEF: self.defense,
            const.SPE: self.speed,
            const.SPA: self.special_attack,
            const.SPD: self.special_defense,
        }
    
    @staticmethod
    def deserialize(raw_dict):
        return StatBlock(
            raw_dict[const.HP],
            raw_dict[const.ATK],
            raw_dict[const.DEF],
            raw_dict[const.SPA],
            raw_dict[const.SPD],
            raw_dict[const.SPE],
        )
    
    def __eq__(self, other):
        if not isinstance(other, StatBlock):
            return False
        
        return (
            self.hp == other.hp and
            self.attack == other.attack and
            self.defense == other.defense and
            self.speed == other.speed and
            self.special_attack == other.special_attack and 
            self.special_defense == other.special_defense
        )
    
    def __repr__(self):
        return f"hp: {self.hp}, atk: {self.attack}, def: {self.defense}, spa: {self.special_attack}, spd: {self.special_defense}, spe: {self.speed}"
    
    def calc_level_stats(self, level, stat_dv, stat_xp, badges:BadgeList):
        raise NotImplementedError()
    
    def calc_battle_stats(self, level, stat_dv, stat_xp, stage_modifiers:StageModifiers, badges:BadgeList, is_crit=False):
        raise NotImplementedError()


class PokemonSpecies:
    def __init__(self, raw_dict):
        self.name = raw_dict[const.NAME_KEY]
        self.growth_rate = raw_dict[const.GROWTH_RATE_KEY]
        self.base_xp = raw_dict[const.BASE_XP_KEY]
        self.first_type = raw_dict[const.FIRST_TYPE_KEY]
        self.second_type = raw_dict[const.SECOND_TYPE_KEY]

        self.stats = StatBlock(
            raw_dict[const.BASE_HP_KEY],
            raw_dict[const.BASE_ATK_KEY],
            raw_dict[const.BASE_DEF_KEY],
            raw_dict[const.BASE_SPE_KEY],
            raw_dict[const.BASE_SPC_KEY],
        )

        self.initial_moves = copy.copy(raw_dict[const.INITIAL_MOVESET_KEY])
        self.levelup_moves = copy.deepcopy(raw_dict[const.LEARNED_MOVESET_KEY])
        self.tmhm_moves = copy.copy(raw_dict[const.TM_HM_LEARNSET_KEY])

    def to_dict(self):
        return {
            const.NAME_KEY: self.name,
            const.BASE_HP_KEY: self.stats.hp,
            const.BASE_ATK_KEY: self.stats.attack,
            const.BASE_DEF_KEY: self.stats.defense,
            const.BASE_SPE_KEY: self.stats.speed,
            const.BASE_SPA_KEY: self.stats.special_attack,
            const.BASE_SPD_KEY: self.stats.special_defense,
            const.BASE_XP_KEY: self.base_xp,
            const.INITIAL_MOVESET_KEY: self.initial_moves,
            const.LEARNED_MOVESET_KEY: self.levelup_moves,
        }


class EnemyPkmn:
    def __init__(self, pkmn_dict, base_stats:StatBlock, dvs:StatBlock, stat_xp:StatBlock=None, badges:BadgeList=None):
        self.name = pkmn_dict[const.NAME_KEY]
        self.level = pkmn_dict[const.LEVEL]
        self.xp = pkmn_dict[const.XP]
        self.move_list = copy.copy(pkmn_dict[const.MOVES])

        self.dvs = dvs
        self.base_stats = base_stats
        self.cur_stats = StatBlock(
            pkmn_dict[const.HP],
            pkmn_dict[const.ATK],
            pkmn_dict[const.DEF],
            pkmn_dict[const.SPE],
            pkmn_dict[const.SPC]
        )

        if stat_xp is None:
            stat_xp = StatBlock(0, 0, 0, 0, 0, True)
        self.stat_xp = stat_xp

        if badges is None:
            badges = BadgeList()
        self.badges = badges

    def __eq__(self, other):
        if not isinstance(other, EnemyPkmn):
            return False
        
        return (
            self.name == other.name and
            self.level == other.level and
            self.cur_stats == other.cur_stats and
            self.xp == other.xp and
            self.move_list == other.move_list and
            self.base_stats == other.base_stats and
            self.dvs == other.dvs and
            self.stat_xp == other.stat_xp and
            self.badges == other.badges
        )
    
    def __repr__(self):
        return self.to_string()

    def to_string(self, verbose=False):
        if verbose:
            return f"Lv {self.level}: {self.name} ({self.cur_stats.hp}, {self.cur_stats.attack}, {self.cur_stats.defense}, {self.cur_stats.speed}, {self.cur_stats.special}), ({self.move_list})"
        return f"Lv {self.level}: {self.name}"

    def get_battle_stats(self, stages:StageModifiers, is_crit:bool=False):
        return self.base_stats.calc_battle_stats(
            self.level,
            self.dvs,
            self.stat_xp,
            stages,
            self.badges,
            is_crit
        )


class Trainer:
    def __init__(self, trainer_dict, pkmn):
        self.trainer_class = trainer_dict[const.TRAINER_CLASS]
        self.name = trainer_dict[const.TRAINER_NAME]
        self.location = trainer_dict[const.TRAINER_LOC]
        self.money = trainer_dict[const.MONEY]
        self.route_one_offset = trainer_dict[const.ROUTE_ONE_OFFSET]

        self.pkmn = pkmn
    

class BaseItem:
    def __init__(self, raw_dict):
        self.name = raw_dict[const.NAME_KEY]
        self.is_key_item = raw_dict[const.IS_KEY_ITEM]
        self.purchase_price = raw_dict[const.PURCHASE_PRICE]
        self.sell_price = self.purchase_price // 2
        self.marts = raw_dict[const.MARTS]
        self.move_name = None
        if self.name.startswith("TM") or self.name.startswith("HM"):
            self.move_name = self.name.split(" ", 1)[1]


class Move:
    def __init__(self, raw_dict):
        self.name = raw_dict[const.NAME_KEY]
        self.accuracy = raw_dict[const.MOVE_ACCURACY]
        self.pp = raw_dict[const.MOVE_PP]
        self.base_power = raw_dict[const.BASE_POWER]
        self.move_type = raw_dict[const.MOVE_TYPE]
        self.effects = raw_dict[const.MOVE_EFFECTS]
        self.attack_flavor = raw_dict[const.MOVE_FLAVOR]
