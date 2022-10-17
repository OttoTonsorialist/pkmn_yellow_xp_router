from __future__ import annotations
from utils.constants import const
import pkmn.gen_2.pkmn_utils as pkmn_utils
from pkmn.gen_2.gen_two_constants import gen_two_const
from pkmn import universal_data_objects


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
            self.hp = min(hp, pkmn_utils.STAT_XP_CAP)
            self.attack = min(attack, pkmn_utils.STAT_XP_CAP)
            self.defense = min(defense, pkmn_utils.STAT_XP_CAP)
            self.speed = min(speed, pkmn_utils.STAT_XP_CAP)
            self.special_attack = min(special_attack, pkmn_utils.STAT_XP_CAP)
            self.special_defense = min(special_defense, pkmn_utils.STAT_XP_CAP)
    
    def calc_level_stats(
        self,
        level:int,
        stat_dv:GenTwoStatBlock,
        stat_xp:GenTwoStatBlock,
        badges:GenTwoBadgeList
    ) -> GenTwoStatBlock:
        # assume self is base stats, level is target level, stat_xp is StatBlock of stat_xp vals, badges is a BadgeList
        return GenTwoStatBlock(
            pkmn_utils.calc_stat(self.hp, level, stat_dv.hp, stat_xp.hp, is_hp=True),
            pkmn_utils.calc_stat(self.attack, level, stat_dv.attack, stat_xp.attack, is_badge_bosted=badges.zephyr),
            pkmn_utils.calc_stat(self.defense, level, stat_dv.defense, stat_xp.defense, is_badge_bosted=badges.mineral),
            pkmn_utils.calc_stat(self.special_attack, level, stat_dv.special_attack, stat_xp.special_attack, is_badge_bosted=badges.glacier),
            pkmn_utils.calc_stat(self.special_defense, level, stat_dv.special_attack, stat_xp.special_attack, is_badge_bosted=badges.glacier),
            pkmn_utils.calc_stat(self.speed, level, stat_dv.speed, stat_xp.speed, is_badge_bosted=badges.plain),
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
            # TODO: need to validate how crits are different in gen two...
            pass

        # create a result object, to populate
        result = GenTwoStatBlock(
            pkmn_utils.calc_stat(self.hp, level, stat_dv.hp, stat_xp.hp, is_hp=True),
            0, 0, 0, 0, 0
        )

        result.attack = pkmn_utils.calc_battle_stat(
            self.attack,
            level,
            stat_dv.attack,
            stat_xp.attack,
            stage_modifiers.attack_stage,
            is_badge_boosted=(badges is not None and badges.is_attack_boosted())
        )

        result.defense = pkmn_utils.calc_battle_stat(
            self.defense,
            level,
            stat_dv.defense,
            stat_xp.defense,
            stage_modifiers.defense_stage,
            is_badge_boosted=(badges is not None and badges.is_defense_boosted())
        )

        result.speed = pkmn_utils.calc_battle_stat(
            self.speed,
            level,
            stat_dv.speed,
            stat_xp.speed,
            stage_modifiers.speed_stage,
            is_badge_boosted=(badges is not None and badges.is_speed_boosted())
        )

        result.special_attack = pkmn_utils.calc_battle_stat(
            self.special_attack,
            level,
            stat_dv.special_attack,
            stat_xp.special_attack,
            stage_modifiers.special_attack_stage,
            is_badge_boosted=(badges is not None and badges.is_special_attack_boosted())
        )

        result.special_defense = pkmn_utils.calc_battle_stat(
            self.special_defense,
            level,
            stat_dv.special_attack,
            stat_xp.special_attack,
            stage_modifiers.special_attack_stage,
            is_badge_boosted=(badges is not None and badges.is_special_defense_boosted())
        )

        return result
