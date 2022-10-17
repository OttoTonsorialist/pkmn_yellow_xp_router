from __future__ import annotations
from utils.constants import const
import pkmn.gen_1.pkmn_utils as pkmn_utils
from pkmn.gen_1.gen_one_constants import gen_one_const
from pkmn import universal_data_objects


class GenOneBadgeList(universal_data_objects.BadgeList):
    def __init__(self, boulder=False, cascade=False, thunder=False, rainbow=False, soul=False, marsh=False, volcano=False, earth=False):
        self.boulder = boulder
        self.cascade = cascade
        self.thunder = thunder
        self.rainbow = rainbow
        self.soul = soul
        self.marsh = marsh
        self.volcano = volcano
        self.earth = earth
    
    def award_badge(self, trainer_name) -> GenOneBadgeList:
        reward = gen_one_const.BADGE_REWARDS.get(trainer_name)
        result = self.copy()
        if reward == gen_one_const.BOULDER_BADGE:
            result.boulder = True
        elif reward == gen_one_const.CASCADE_BADGE:
            result.cascade = True
        elif reward == gen_one_const.THUNDER_BADGE:
            result.thunder = True
        elif reward == gen_one_const.RAINDBOW_BADGE:
            result.rainbow = True
        elif reward == gen_one_const.SOUL_BADGE:
            result.soul = True
        elif reward == gen_one_const.MARSH_BADGE:
            result.marsh = True
        elif reward == gen_one_const.VOLCANO_BADGE:
            result.volcano = True
        elif reward == gen_one_const.EARTH_BADGE:
            result.earth = True
        else:
            # no need to hold on to a copy wastefully if no badge was awarded
            return self
        
        return result
    
    def is_attack_boosted(self):
        return self.boulder
    
    def is_defense_boosted(self):
        return self.thunder
    
    def is_speed_boosted(self):
        return self.soul
    
    def is_special_attack_boosted(self):
        return self.volcano

    def is_special_defense_boosted(self):
        return self.volcano
    
    def copy(self) -> GenOneBadgeList:
        return GenOneBadgeList(
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
    
    def __eq__(self, other):
        if not isinstance(other, GenOneBadgeList):
            return False
        
        return (
            self.boulder == other.boulder and
            self.cascade == other.cascade and
            self.thunder == other.thunder and
            self.rainbow == other.rainbow and
            self.soul == other.soul and
            self.marsh == other.marsh and
            self.volcano == other.volcano and
            self.earth == other.earth
        )


class GenOneStatBlock(universal_data_objects.StatBlock):
    def __init__(self, hp, attack, defense, special_attack, special_defense, speed, is_stat_xp=False):
        super().__init__(hp, attack, defense, special_attack, special_defense, speed, is_stat_xp=False)

        # NOTE: as a general strategy, as GenOne only has one special stat in actuality, this object
        # will use special attack for all "special" calculations. Special defense will still be populated with
        # the same value though. This is done for better compatibility with other generations

        # hard cap STAT XP vals
        if is_stat_xp:
            self.hp = min(hp, pkmn_utils.STAT_XP_CAP)
            self.attack = min(attack, pkmn_utils.STAT_XP_CAP)
            self.defense = min(defense, pkmn_utils.STAT_XP_CAP)
            self.speed = min(speed, pkmn_utils.STAT_XP_CAP)
            self.special_attack = min(special_attack, pkmn_utils.STAT_XP_CAP)
            self.special_defense = min(special_defense, pkmn_utils.STAT_XP_CAP)
    
    def calc_level_stats(
        self,
        level:int,
        stat_dv:GenOneStatBlock,
        stat_xp:GenOneStatBlock,
        badges:GenOneBadgeList
    ) -> GenOneStatBlock:
        # assume self is base stats, level is target level, stat_xp is StatBlock of stat_xp vals, badges is a BadgeList
        special = pkmn_utils.calc_stat(self.special_attack, level, stat_dv.special_attack, stat_xp.special_attack, is_badge_bosted=badges.volcano)
        return GenOneStatBlock(
            pkmn_utils.calc_stat(self.hp, level, stat_dv.hp, stat_xp.hp, is_hp=True),
            pkmn_utils.calc_stat(self.attack, level, stat_dv.attack, stat_xp.attack, is_badge_bosted=badges.boulder),
            pkmn_utils.calc_stat(self.defense, level, stat_dv.defense, stat_xp.defense, is_badge_bosted=badges.thunder),
            special,
            special,
            pkmn_utils.calc_stat(self.speed, level, stat_dv.speed, stat_xp.speed, is_badge_bosted=badges.soul),
        )
    
    def calc_battle_stats(
        self,
        level:int,
        stat_dv:GenOneStatBlock,
        stat_xp:GenOneStatBlock,
        stage_modifiers:universal_data_objects.StageModifiers,
        badges:GenOneBadgeList,
        is_crit=False
    ) -> GenOneStatBlock:
        # TODO: this does not properly replicate any of the jank regarding para/burn/full heal/etc.
        # TODO: need to add support for those stat modifiers (both intended any glitched) in the future

        if is_crit:
            # prevent all badge-boosts and stage modifiers whenever a crit occurs
            # by just pretending you don't have any of either
            badges = GenOneBadgeList()
            stage_modifiers = universal_data_objects.StageModifiers(
                accuracy=stage_modifiers.accuracy_stage,
                evasion=stage_modifiers.evasion_stage
            )

        # create a result object, to populate
        result = GenOneStatBlock(
            pkmn_utils.calc_stat(self.hp, level, stat_dv.hp, stat_xp.hp, is_hp=True),
            0, 0, 0, 0, 0
        )

        # note, important to apply stage modifier *first*, then any badge boosts
        # Badge boost counts are properly reset upon stage modification, so any listed are from other stats being boosted after the stage modifier
        result.attack = pkmn_utils.calc_battle_stat(
            self.attack,
            level,
            stat_dv.attack,
            stat_xp.attack,
            stage_modifiers.attack_stage,
            is_badge_boosted=(badges is not None and badges.is_attack_boosted())
        )
        if badges is not None and badges.boulder and stage_modifiers.attack_badge_boosts != 0:
            for _ in range(stage_modifiers.attack_badge_boosts):
                result.attack = pkmn_utils.badge_boost_single_stat(result.attack)

        result.defense = pkmn_utils.calc_battle_stat(
            self.defense,
            level,
            stat_dv.defense,
            stat_xp.defense,
            stage_modifiers.defense_stage,
            is_badge_boosted=(badges is not None and badges.is_defense_boosted())
        )
        if badges is not None and badges.thunder and stage_modifiers.defense_badge_boosts != 0:
            for _ in range(stage_modifiers.defense_badge_boosts):
                result.defense = pkmn_utils.badge_boost_single_stat(result.defense)

        result.speed = pkmn_utils.calc_battle_stat(
            self.speed,
            level,
            stat_dv.speed,
            stat_xp.speed,
            stage_modifiers.speed_stage,
            is_badge_boosted=(badges is not None and badges.is_speed_boosted())
        )
        if badges is not None and badges.soul and stage_modifiers.speed_badge_boosts != 0:
            for _ in range(stage_modifiers.speed_badge_boosts):
                result.speed = pkmn_utils.badge_boost_single_stat(result.speed)

        result.special_attack = pkmn_utils.calc_battle_stat(
            self.special_attack,
            level,
            stat_dv.special_attack,
            stat_xp.special_attack,
            stage_modifiers.special_attack_stage,
            is_badge_boosted=(badges is not None and badges.is_special_attack_boosted())
        )
        if badges is not None and badges.volcano and stage_modifiers.special_badge_boosts != 0:
            for _ in range(stage_modifiers.special_badge_boosts):
                result.special_attack = pkmn_utils.badge_boost_single_stat(result.special_attack)
        result.special_defense = result.special_attack

        return result
