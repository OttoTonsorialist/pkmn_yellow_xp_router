import copy

from utils.constants import const
import pkmn.pkmn_utils as pkmn_utils


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
            self.move_name = self.name.split(" ", 1)[1].lower().replace(" ", "_")

