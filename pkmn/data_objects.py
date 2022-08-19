import copy

from utils.constants import const
import pkmn.pkmn_utils as pkmn_utils


class BadgeList:
    def __init__(self, boulder=False, cascade=False, thunder=False, rainbow=False, soul=False, marsh=False, volcano=False, earth=False):
        self.boulder = boulder
        self.cascade = cascade
        self.thunder = thunder
        self.rainbow = rainbow
        self.soul = soul
        self.marsh = marsh
        self.volcano = volcano
        self.earth = earth
    
    def award_badge(self, trainer_name):
        reward = const.BADGE_REWARDS.get(trainer_name)
        result = self.copy(self)
        if reward == const.BOULDER_BADGE:
            result.boulder = True
        elif reward == const.CASCADE_BADGE:
            result.cascade = True
        elif reward == const.THUNDER_BADGE:
            result.thunder = True
        elif reward == const.RAINDBOW_BADGE:
            result.rainbow = True
        elif reward == const.SOUL_BADGE:
            result.soul = True
        elif reward == const.MARSH_BADGE:
            result.marsh = True
        elif reward == const.VOLCANO_BADGE:
            result.volcano = True
        elif reward == const.EARTH_BADGE:
            result.earth = True
        else:
            # no need to hold on to a copy wastefully if no badge was awarded
            return self
        
        return result
    
    @staticmethod
    def copy(bl):
        if not isinstance(bl, BadgeList):
            raise ValueError(f"Can only copy BadgeList from BadgeList, not {type(bl)}")
        return BadgeList(
            boulder=bl.boulder,
            cascade=bl.cascade,
            thunder=bl.thunder,
            rainbow=bl.rainbow,
            soul=bl.soul,
            marsh=bl.marsh,
            volcano=bl.volcano,
            earth=bl.earth
        )
    
    def to_string(self, verbose=False):
        if not verbose:
            result = []
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
            return f"Boulder: {self.boulder}, Cascade: {self.cascade}, Thunder: {self.thunder}, Rainbow: {self.rainbow}, Soul: {self.soul}, Marsh: {self.marsh}, Volcano: {self.volcano}, Earth: {self.earth}"
    
    def __repr__(self):
        return self.to_string(verbose=True)


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
    
    def after_move(self, move_name):
        # NOTE: assumes move always successfully modifies the stat in question
        stat_mod = const.STAT_INCREASE_MOVES.get(move_name)
        if stat_mod is None:
            stat_mod = const.STAT_DECREASE_MOVES.get(move_name)
        
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
        elif stat_mod[0] == const.SPD:
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
    def __init__(self, hp, attack, defense, speed, special, is_stat_xp=False):
        self._is_stat_xp = is_stat_xp

        if not is_stat_xp:
            self.hp = hp
            self.attack = attack
            self.defense = defense
            self.speed = speed
            self.special = special
        else:
            self.hp = min(hp, pkmn_utils.STAT_XP_CAP)
            self.attack = min(attack, pkmn_utils.STAT_XP_CAP)
            self.defense = min(defense, pkmn_utils.STAT_XP_CAP)
            self.speed = min(speed, pkmn_utils.STAT_XP_CAP)
            self.special = min(special, pkmn_utils.STAT_XP_CAP)
    
    def add(self, other):
        if not isinstance(other, StatBlock):
            raise ValueError(f"Cannot add type: {type(other)} to StatBlock")
        return StatBlock(
            self.hp + other.hp,
            self.attack + other.attack,
            self.defense + other.defense,
            self.speed + other.speed,
            self.special + other.special,
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
            self.special - other.special,
            is_stat_xp=self._is_stat_xp
        )
    
    def __repr__(self):
        return f"hp: {self.hp}, atk: {self.attack}, def: {self.defense}, spd: {self.speed}, spc: {self.special}"
    
    def calc_level_stats(self, level, stat_dv, stat_xp, badges:BadgeList):
        # assume self is base stats, level is target level, stat_xp is StatBlock of stat_xp vals, badges is a BadgeList
        return StatBlock(
            pkmn_utils.calc_stat(self.hp, level, stat_dv.hp, stat_xp.hp, is_hp=True),
            pkmn_utils.calc_stat(self.attack, level, stat_dv.attack, stat_xp.attack, is_badge_bosted=badges.boulder),
            pkmn_utils.calc_stat(self.defense, level, stat_dv.defense, stat_xp.defense, is_badge_bosted=badges.thunder),
            pkmn_utils.calc_stat(self.speed, level, stat_dv.speed, stat_xp.speed, is_badge_bosted=badges.soul),
            pkmn_utils.calc_stat(self.special, level, stat_dv.special, stat_xp.special, is_badge_bosted=badges.volcano),
        )
    
    def calc_battle_stats(self, level, stat_dv, stat_xp, stage_modifiers:StageModifiers, badges:BadgeList):
        # TODO: this does not properly replicate any of the jank regarding para/burn/full heal/etc.
        # TODO: need to add support for those stat modifiers (both intended any glitched) in the future

        # create a result object, to populate
        result = StatBlock(
            pkmn_utils.calc_stat(self.hp, level, stat_dv.hp, stat_xp.hp, is_hp=True),
            0, 0, 0, 0
        )

        # note, important to apply stage modifier *first*, then any badge boosts
        # Badge boost counts are properly reset upon stage modification, so any listed are from other stats being boosted after the stage modifier
        result.attack = pkmn_utils.calc_battle_stat(self.attack, level, stat_dv.attack, stat_xp.attack, stage_modifiers.attack_stage, is_badge_boosted=badges.boulder)
        if badges.boulder and stage_modifiers.attack_badge_boosts != 0:
            for _ in range(stage_modifiers.attack_badge_boosts):
                result.attack = pkmn_utils.badge_boost_single_stat(result.attack)

        result.defense = pkmn_utils.calc_battle_stat(self.defense, level, stat_dv.defense, stat_xp.defense, stage_modifiers.defense_stage, is_badge_boosted=badges.thunder)
        if badges.thunder and stage_modifiers.defense_badge_boosts != 0:
            for _ in range(stage_modifiers.defense_badge_boosts):
                result.defense = pkmn_utils.badge_boost_single_stat(result.defense)

        result.speed = pkmn_utils.calc_battle_stat(self.speed, level, stat_dv.speed, stat_xp.speed, stage_modifiers.speed_stage, is_badge_boosted=badges.soul)
        if badges.soul and stage_modifiers.speed_badge_boosts != 0:
            for _ in range(stage_modifiers.speed_badge_boosts):
                result.speed = pkmn_utils.badge_boost_single_stat(result.speed)

        result.special = pkmn_utils.calc_battle_stat(self.special, level, stat_dv.special, stat_xp.special, stage_modifiers.special_stage, is_badge_boosted=badges.volcano)
        if badges.volcano and stage_modifiers.special_badge_boosts != 0:
            for _ in range(stage_modifiers.special_badge_boosts):
                result.special = pkmn_utils.badge_boost_single_stat(result.special)

        return result


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
            raw_dict[const.BASE_SPD_KEY],
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
            const.BASE_SPD_KEY: self.stats.speed,
            const.BASE_SPC_KEY: self.stats.special,
            const.BASE_XP_KEY: self.base_xp,
            const.INITIAL_MOVESET_KEY: self.initial_moves,
            const.LEARNED_MOVESET_KEY: self.levelup_moves,
        }


class EnemyPkmn:
    def __init__(self, pkmn_dict, base_stat_block):
        self.name = pkmn_dict[const.NAME_KEY]
        self.level = pkmn_dict[const.LEVEL]
        self.hp = pkmn_dict[const.HP]
        self.attack = pkmn_dict[const.ATK]
        self.defense = pkmn_dict[const.DEF]
        self.speed = pkmn_dict[const.SPD]
        self.special = pkmn_dict[const.SPC]
        self.xp = pkmn_dict[const.XP]
        self.move_list = copy.copy(pkmn_dict[const.MOVES])

        # pkmn_db should be a dict of names->BaseStats objects
        # just grab the StatBlock from there
        self.base_stat_block = base_stat_block
    
    def __repr__(self):
        return f"Lv {self.level}: {self.name}"


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

