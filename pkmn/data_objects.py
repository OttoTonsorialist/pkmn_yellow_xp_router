import copy
from multiprocessing.sharedctypes import Value

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
    
    def __repr__(self):
        return f"Boulder: {self.boulder}, Cascade: {self.cascade}, Thunder: {self.thunder}, Rainbow: {self.rainbow}, Soul: {self.soul}, Marsh: {self.marsh}, Volcano: {self.volcano}, Earth: {self.earth}"
    

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
    
    def __repr__(self):
        return f"hp: {self.hp}, atk: {self.attack}, def: {self.defense}, spd: {self.speed}, spc: {self.special}"
    
    def calc_level_stats(self, level, stat_dv, stat_xp, badges):
        # assume self is base stats, level is target level, stat_xp is StatBlock of stat_xp vals, badges is a BadgeList
        return StatBlock(
            pkmn_utils.calc_stat(self.hp, level, stat_dv.hp, stat_xp.hp, is_hp=True),
            pkmn_utils.calc_stat(self.attack, level, stat_dv.attack, stat_xp.attack, is_badge_bosted=badges.boulder),
            pkmn_utils.calc_stat(self.defense, level, stat_dv.defense, stat_xp.defense, is_badge_bosted=badges.thunder),
            pkmn_utils.calc_stat(self.speed, level, stat_dv.speed, stat_xp.speed, is_badge_bosted=badges.soul),
            pkmn_utils.calc_stat(self.special, level, stat_dv.special, stat_xp.special, is_badge_bosted=badges.volcano),
        )


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


class Trainer:
    def __init__(self, trainer_dict, pkmn):
        self.trainer_class = trainer_dict[const.TRAINER_CLASS]
        self.name = trainer_dict[const.TRAINER_NAME]
        self.location = trainer_dict[const.TRAINER_LOC]
        self.money = trainer_dict[const.MONEY]

        self.pkmn = pkmn
    

class SoloPokemon:
    """
    This is not considered a mutable object!!!
    Represents a snapshot of a pokemon at a single moment in time
    All methods to apply changes will return a new object

    Moves are not yet handled, only level/stats/statxp are handled
    """
    def __init__(self, name, species_def, cur_xp=0, dvs=None, realized_stat_xp=None, unrealized_stat_xp=None, badges=None, gained_xp=0, gained_stat_xp=None):
        self.name = name
        self.species_def = species_def

        if cur_xp == 0:
            # if no initial XP is defined, assume creating a new level 5 pkmn
            self.cur_xp = pkmn_utils.level_lookups[self.species_def.growth_rate].get_xp_for_level(5)
        else:
            self.cur_xp = cur_xp

        if badges is None:
            self.badges = BadgeList()
        else:
            self.badges = badges
        
        # assume going with perfect DVs if undefined
        if dvs is None:
            self.dvs = StatBlock(15, 15, 15, 15, 15)
        else:
            self.dvs = dvs

        level_info = pkmn_utils.level_lookups[self.species_def.growth_rate].get_level_info(self.cur_xp)
        self.cur_level = level_info[0]
        self.xp_to_next_level = level_info[1]

        if realized_stat_xp is None:
            realized_stat_xp = StatBlock(0, 0, 0, 0, 0, is_stat_xp=True)
        self.realized_stat_xp = realized_stat_xp

        if unrealized_stat_xp is None:
            unrealized_stat_xp = StatBlock(0, 0, 0, 0, 0, is_stat_xp=True)
        self.unrealized_stat_xp = unrealized_stat_xp

        if gained_stat_xp is None:
            gained_stat_xp = StatBlock(0, 0, 0, 0, 0, is_stat_xp=True)
        
        if const.DEBUG_MODE:
            print(f"Gaining {gained_xp}, was at {self.cur_xp}, now at {self.cur_xp + gained_xp}. Before gain, needed {self.xp_to_next_level} TNL")
        self.cur_xp += gained_xp
        if gained_xp < self.xp_to_next_level:
            # gained xp did not cause a level up
            # just keep collecting unrealized stat xp, and keep track of new XP
            self.xp_to_next_level -= gained_xp
            self.unrealized_stat_xp = self.unrealized_stat_xp.add(gained_stat_xp)
            if const.DEBUG_MODE:
                print(f"NO level up ocurred, still need {self.xp_to_next_level} TNL")
        else:
            # gained xp DID cause a level up
            # realize ALL stat XP into new stats, reset unrealized stat XP, and then update level metadata
            self.realized_stat_xp = self.realized_stat_xp.add(self.unrealized_stat_xp).add(gained_stat_xp)
            self.unrealized_stat_xp = StatBlock(0, 0, 0, 0, 0, is_stat_xp=True)

            level_info = pkmn_utils.level_lookups[self.species_def.growth_rate].get_level_info(self.cur_xp)
            self.cur_level = level_info[0]
            self.xp_to_next_level = level_info[1]
            if const.DEBUG_MODE:
                print(f"Now level {self.cur_level}, {self.xp_to_next_level} TNL")
        
        if const.DEBUG_MODE:
            print(f"Realized StatXP {self.realized_stat_xp}")
            print(f"Unrealized StatXP {self.unrealized_stat_xp}")
        self.cur_stats = self.species_def.stats.calc_level_stats(self.cur_level, self.dvs, self.realized_stat_xp, self.badges)
    
    def get_renderable_pkmn(self):
        # pkmn viewer only knows how to show off the EnemyPkmn type
        # So create a view of this pokemon in that type for rendering
        # we're going to cheat a lot here, whatever
        return EnemyPkmn(
            {
                const.NAME_KEY: self.name,
                const.LEVEL: self.cur_level,
                const.HP: self.cur_stats.hp,
                const.ATK: self.cur_stats.attack,
                const.DEF: self.cur_stats.defense,
                const.SPD: self.cur_stats.speed,
                const.SPC: self.cur_stats.special,
                const.XP: -1,
                const.MOVES: ["N/A"],
            },
            self.cur_stats
        )
    
    def defeat_pkmn(self, enemy_pkmn: EnemyPkmn, trainer_name=None, is_final_pkmn=False):
        # enemy_pkmn is an EnemyPkmn type
        return SoloPokemon(
            self.name,
            self.species_def,
            cur_xp=self.cur_xp,
            dvs=self.dvs,
            realized_stat_xp=self.realized_stat_xp,
            unrealized_stat_xp=self.unrealized_stat_xp,
            badges=self.badges.award_badge(trainer_name) if is_final_pkmn else BadgeList.copy(self.badges),
            gained_xp=enemy_pkmn.xp,
            gained_stat_xp=enemy_pkmn.base_stat_block
        )
    
    def rare_candy(self):
        return SoloPokemon(
            self.name,
            self.species_def,
            cur_xp=self.cur_xp,
            dvs=self.dvs,
            realized_stat_xp=self.realized_stat_xp,
            unrealized_stat_xp=self.unrealized_stat_xp,
            badges=BadgeList.copy(self.badges),
            gained_xp=self.xp_to_next_level,
        )
    
    def take_vitamin(self, vit_name):
        # NOTE: some potentially buggy reporting of how much stat xp is actually possible when nearing the stat XP cap
        # this is due to the fact that we are keeping unrealized stat XP separate,
        # so any stat XP over the hard cap won't be properly ignored until it's realized
        # however, this bug is both minor (won't ever be reported in the actual pkmn stats) and rare (only when nearing stat XP cap, which is uncommon in solo playthroughs) 
        # intentionally ignoring for now
        cur_stat_xp_total = self.realized_stat_xp.add(self.unrealized_stat_xp)

        if vit_name == const.HP_UP:
            if cur_stat_xp_total.hp >= pkmn_utils.VIT_CAP:
                return None
            new_unrealized_stat_xp = self.unrealized_stat_xp.add(StatBlock(pkmn_utils.VIT_AMT, 0, 0, 0, 0, is_stat_xp=True))
        elif vit_name == const.PROTEIN:
            if cur_stat_xp_total.attack >= pkmn_utils.VIT_CAP:
                return None
            new_unrealized_stat_xp = self.unrealized_stat_xp.add(StatBlock(0, pkmn_utils.VIT_AMT, 0, 0, 0, is_stat_xp=True))
        elif vit_name == const.IRON:
            if cur_stat_xp_total.defense >= pkmn_utils.VIT_CAP:
                return None
            new_unrealized_stat_xp = self.unrealized_stat_xp.add(StatBlock(0, 0, pkmn_utils.VIT_AMT, 0, 0, is_stat_xp=True))
        elif vit_name == const.CARBOS:
            if cur_stat_xp_total.speed >= pkmn_utils.VIT_CAP:
                return None
            new_unrealized_stat_xp = self.unrealized_stat_xp.add(StatBlock(0, 0, 0, pkmn_utils.VIT_AMT, 0, is_stat_xp=True))
        elif vit_name == const.CALCIUM:
            if cur_stat_xp_total.special >= pkmn_utils.VIT_CAP:
                return None
            new_unrealized_stat_xp = self.unrealized_stat_xp.add(StatBlock(0, 0, 0, 0, pkmn_utils.VIT_AMT, is_stat_xp=True))
        else:
            raise ValueError(f"Unknown vitamin: {vit_name}")

        return SoloPokemon(
            self.name,
            self.species_def,
            self.cur_xp,
            dvs=self.dvs,
            realized_stat_xp=self.realized_stat_xp,
            unrealized_stat_xp=new_unrealized_stat_xp,
            badges=BadgeList.copy(self.badges),
        )