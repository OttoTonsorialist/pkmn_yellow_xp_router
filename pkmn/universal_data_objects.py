from __future__ import annotations
import copy
from typing import Dict, List, Tuple

from utils.constants import const


class BadgeList:
    def award_badge(self, trainer_name):
        raise NotImplementedError()
    
    def to_string(self, verbose=False) -> str:
        raise NotImplementedError()
    
    def is_attack_boosted(self):
        raise NotImplementedError()
    
    def is_defense_boosted(self):
        raise NotImplementedError()
    
    def is_speed_boosted(self):
        raise NotImplementedError()
    
    def is_special_attack_boosted(self):
        raise NotImplementedError()

    def is_special_defense_boosted(self):
        raise NotImplementedError()
    
    def copy(self):
        raise NotImplementedError()
    
    def to_string(self, verbose=False):
        raise NotImplementedError()

class StageModifiers:
    def __init__(self,
        attack=0, defense=0, speed=0, special_attack=0, special_defense=0, accuracy=0, evasion=0,
        attack_bb=0, defense_bb=0, speed_bb=0, special_bb=0
    ):
        self.attack_stage = max(min(attack, 6), -6)
        self.defense_stage = max(min(defense, 6), -6)
        self.speed_stage = max(min(speed, 6), -6)
        self.special_attack_stage = max(min(special_attack, 6), -6)
        self.special_defense_stage = max(min(special_defense, 6), -6)
        self.accuracy_stage = max(min(accuracy, 6), -6)
        self.evasion_stage = max(min(evasion, 6), -6)

        # keep track of which badge boosts are applicable to which stats
        # NOTE: the badge-boost tracking is married to the GenOne structure because they only
        # occur in gen one. These will just be ignored by all other gens
        # SECOND NOTE: this data structure does not care about which badges the player has.
        # Instead, this tracks "theoretical" badge boosts,
        # which should only apply if the corresponding badge has been earned
        self.attack_badge_boosts = attack_bb
        self.defense_badge_boosts = defense_bb
        self.speed_badge_boosts = speed_bb
        self.special_badge_boosts = special_bb
    
    def _copy_constructor(self) -> StageModifiers:
        return StageModifiers(
            attack=self.attack_stage, defense=self.defense_stage, speed=self.speed_stage,
            special_attack=self.special_attack_stage, special_defense=self.special_defense_stage,
            accuracy=self.accuracy_stage, evasion=self.evasion_stage,

            attack_bb=self.attack_badge_boosts, defense_bb=self.defense_badge_boosts,
            speed_bb=self.speed_badge_boosts, special_bb=self.special_badge_boosts,
        )
    
    def clear_badge_boosts(self) -> StageModifiers:
        result = self._copy_constructor()

        result.attack_badge_boosts = 0
        result.defense_badge_boosts = 0
        result.speed_badge_boosts = 0
        result.special_badge_boosts = 0

        return result
    
    def apply_stat_mod(self, all_stat_mods:List[Tuple[str, int]]) -> StageModifiers:
        if not all_stat_mods:
            return self
        
        result = self._copy_constructor()
        result.attack_badge_boosts += 1
        result.defense_badge_boosts += 1
        result.speed_badge_boosts += 1
        result.special_badge_boosts += 1

        for stat_mod in all_stat_mods:
            # NOTE: a litle bit of implementation jank: attempt to apply boost as defined,
            # but if the boost would have no effect, then revert to returning self
            if stat_mod[0] == const.ATK:
                result.attack_stage = max(min(self.attack_stage + stat_mod[1], 6), -6)
                if result.attack_stage == self.attack_stage:
                    result = self
                    continue
                result.attack_badge_boosts = 0
            elif stat_mod[0] == const.DEF:
                result.defense_stage = max(min(self.defense_stage + stat_mod[1], 6), -6)
                if result.defense_stage == self.defense_stage:
                    result = self
                    continue
                result.defense_badge_boosts = 0
            elif stat_mod[0] == const.SPE:
                result.speed_stage = max(min(self.speed_stage + stat_mod[1], 6), -6)
                if result.speed_stage == self.speed_stage:
                    result = self
                    continue
                result.speed_badge_boosts = 0
            elif stat_mod[0] == const.SPA:
                result.special_attack_stage = max(min(self.special_attack_stage + stat_mod[1], 6), -6)
                if result.special_attack_stage == self.special_attack_stage:
                    result = self
                    continue
                result.special_badge_boosts = 0
            elif stat_mod[0] == const.SPD:
                result.special_defense_stage = max(min(self.special_defense_stage + stat_mod[1], 6), -6)
                if result.special_defense_stage == self.special_defense_stage:
                    result = self
                    continue
                result.special_badge_boosts = 0
            elif stat_mod[0] == const.ACC:
                result.accuracy_stage = max(min(self.accuracy_stage + stat_mod[1], 6), -6)
                if result.accuracy_stage == self.accuracy_stage:
                    result = self
                    continue
            elif stat_mod[0] == const.EV:
                result.evasion_stage = max(min(self.evasion_stage + stat_mod[1], 6), -6)
                if result.evasion_stage == self.evasion_stage:
                    result = self
                    continue

        return result

    def __eq__(self, other):
        if not isinstance(other, StageModifiers):
            return False
        
        return (
            self.attack_stage == other.attack_stage and
            self.attack_badge_boosts == other.attack_badge_boosts and
            self.defense_stage == other.defense_stage and
            self.defense_badge_boosts == other.defense_badge_boosts and
            self.speed_stage == other.speed_stage and
            self.speed_badge_boosts == other.speed_badge_boosts and
            self.special_attack_stage == other.special_attack_stage and
            self.special_defense_stage == other.special_defense_stage and
            self.special_badge_boosts == other.special_badge_boosts and
            self.accuracy_stage == other.accuracy_stage and
            self.evasion_stage == other.evasion_stage
        )
    
    def __repr__(self):
        return f"""
            Atk: ({self.attack_stage}, {self.attack_badge_boosts}), 
            Def: ({self.defense_stage}, {self.defense_badge_boosts}), 
            Spa: ({self.special_attack_stage}, {self.special_badge_boosts}), 
            Spd: ({self.special_defense_stage}, {self.special_badge_boosts}), 
            Spe: ({self.speed_stage}, {self.speed_badge_boosts}), 
            Acc: ({self.accuracy_stage}, 0), 
            Evn: ({self.evasion_stage}, 0)
        """


class StatBlock:
    def __init__(self, hp, attack, defense, special_attack, special_defense, speed, is_stat_xp=False):
        # NOTE: StatBlock subclasses must implement stat_xp/EV caps as necessary
        self._is_stat_xp = is_stat_xp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.special_attack = special_attack
        self.special_defense = special_defense
    
    def add(self, other:StatBlock) -> StatBlock:
        if not isinstance(other, StatBlock):
            raise ValueError(f"Cannot add type: {type(other)} to StatBlock")
        return StatBlock(
            self.hp + other.hp,
            self.attack + other.attack,
            self.defense + other.defense,
            self.special_attack + other.special_attack,
            self.special_defense + other.special_defense,
            self.speed + other.speed,
            is_stat_xp=self._is_stat_xp
        )
    
    def subtract(self, other:StatBlock) -> StatBlock:
        if not isinstance(other, StatBlock):
            raise ValueError(f"Cannot subtract type: {type(other)} from StatBlock")
        return StatBlock(
            self.hp - other.hp,
            self.attack - other.attack,
            self.defense - other.defense,
            self.special_attack - other.special_attack,
            self.special_defense - other.special_defense,
            self.speed - other.speed,
            is_stat_xp=self._is_stat_xp
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
    
    def serialize(self):
        return {
            const.HP: self.hp,
            const.ATK: self.attack,
            const.DEF: self.defense,
            const.SPD: self.speed,
            const.SPC: self.special_attack,
        }
    
    def __repr__(self):
        return f"hp: {self.hp}, atk: {self.attack}, def: {self.defense}, spa: {self.special_attack}, spd: {self.special_defense}, spe: {self.speed}"
    
    def calc_level_stats(self, level:int, dvs:StatBlock, stat_xp:StatBlock, badges:BadgeList) -> StatBlock:
        raise NotImplementedError()
    
    def calc_battle_stats(self, level:int, dvs:StatBlock, stat_xp:StatBlock, stage_modifiers:StageModifiers, badges:BadgeList, is_crit=False) -> StatBlock:
        raise NotImplementedError()


class PokemonSpecies:
    def __init__(
        self,
        name:str,
        growth_rate:str,
        base_xp:int,
        first_type:str,
        second_type:str,
        stats:StatBlock,
        initial_moves:List[str],
        levelup_moves:List[Tuple[int, str]],
        tmhm_moves:List[str]
    ):
        self.name = name
        self.growth_rate = growth_rate
        self.base_xp = base_xp
        self.first_type = first_type
        self.second_type = second_type
        self.stats = stats
        self.initial_moves = initial_moves
        self.levelup_moves = levelup_moves
        self.tmhm_moves = tmhm_moves


class EnemyPkmn:
    def __init__(
        self,
        name:str,
        level:int,
        xp:int,
        move_list:List[str],
        cur_stats:StatBlock,
        base_stats:StatBlock,
        dvs:StatBlock,
        stat_xp:StatBlock,
        badges:BadgeList,
        held_item:str=None,
    ):
        self.name = name
        self.level = level
        self.xp = xp
        self.move_list = copy.copy(move_list)
        self.cur_stats = cur_stats
        self.base_stats = base_stats
        self.dvs = dvs
        self.stat_xp = stat_xp
        self.badges = badges
        self.held_item = held_item

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
            self.badges == other.badges and
            self.held_item == other.held_item
        )
    
    def __repr__(self):
        return self.to_string()

    def to_string(self, verbose=False):
        if verbose:
            return f"Lv {self.level}: {self.name} (Held: {self.held_item}) ({self.cur_stats.hp}, {self.cur_stats.attack}, {self.cur_stats.defense}, {self.cur_stats.special_attack}, {self.cur_stats.special_defense}, {self.cur_stats.speed}), ({self.move_list})"
        return f"Lv {self.level}: {self.name}"

    def get_battle_stats(self, stages:StageModifiers, is_crit:bool=False) -> StatBlock:
        return self.base_stats.calc_battle_stats(
            self.level,
            self.dvs,
            self.stat_xp,
            stages,
            self.badges,
            is_crit
        )


class Trainer:
    def __init__(
        self,
        trainer_class:str,
        name:str,
        location:str,
        money:int,
        pkmn:List[EnemyPkmn],
        rematch:bool=False,
        trainer_id:int=-1,
        refightable=False
    ):
        self.trainer_class = trainer_class
        self.name = name
        self.location = location
        self.money = money
        self.pkmn = pkmn
        self.rematch = rematch
        self.trainer_id = trainer_id
        self.refightable = refightable
    

class BaseItem:
    def __init__(
        self,
        name:str,
        is_key_item:bool,
        purchase_price:int,
        marts:List[str],
        move_name:str=None
    ):
        self.name = name
        self.is_key_item = is_key_item
        self.purchase_price = purchase_price
        self.sell_price = self.purchase_price // 2
        self.marts = marts
        self.move_name = move_name


class Move:
    def __init__(
        self,
        name:str,
        accuracy:int,
        pp:int,
        base_power:int,
        move_type:str,
        effects,
        attack_flavor:List[str]
    ):
        self.name = name
        self.accuracy = accuracy
        self.pp = pp
        self.base_power = base_power
        self.move_type = move_type
        self.effects = effects
        self.attack_flavor = attack_flavor
