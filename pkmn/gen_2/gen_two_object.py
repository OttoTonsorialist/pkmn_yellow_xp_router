import json
import copy
from typing import List

from pkmn import universal_data_objects
from pkmn.gen_2 import pkmn_damage_calc, pkmn_utils
from pkmn.damage_calc import DamageRange
from pkmn.gen_2.data_objects import GenTwoBadgeList, GenTwoStatBlock
from pkmn.gen_2.gen_two_constants import gen_two_const
from pkmn.pkmn_db import ItemDB, MinBattlesDB, PkmnDB, TrainerDB, MoveDB
from pkmn.pkmn_info import CurrentGen
from routing import route_state_objects
from utils.constants import const


class GenTwo(CurrentGen):
    def __init__(self, pkmn_db_path, trainer_db_path, min_battles_path, version_name):
        self._version_name = version_name
        self._pkmn_db = PkmnDB(_load_pkmn_db(pkmn_db_path))
        self._trainer_db = TrainerDB(_load_trainer_db(trainer_db_path, self._pkmn_db))
        self._item_db = ItemDB(_load_item_db(gen_two_const.ITEM_DB_PATH))

        all_stat_modifying_moves = {}
        for name, val in gen_two_const.STAT_INCREASE_MOVES.items():
            all_stat_modifying_moves[name] = val
        for name, val in gen_two_const.STAT_DECREASE_MOVES.items():
            all_stat_modifying_moves[name] = val
        self._move_db = MoveDB(_load_move_db(gen_two_const.MOVE_DB_PATH), all_stat_modifying_moves)

        self._min_battles_db = MinBattlesDB(min_battles_path)

        self._pkmn_db.validate_moves(self._move_db)
        self._trainer_db.validate_trainers(self._pkmn_db, self._move_db)
        self._item_db.validate_tms_hms(self._move_db)

    def version_name(self) -> str:
        return self._version_name
    
    def get_generation(self) -> int:
        return 2

    def pkmn_db(self) -> PkmnDB:
        return self._pkmn_db
    
    def item_db(self) -> ItemDB:
        return self._item_db
    
    def trainer_db(self) -> TrainerDB:
        return self._trainer_db
    
    def move_db(self) -> MoveDB:
        return self._move_db
    
    def min_battles_db(self) -> MinBattlesDB:
        return self._min_battles_db

    def create_trainer_pkmn(self, pkmn_name, pkmn_level):
        return pkmn_utils.instantiate_trainer_pokemon(self._pkmn_db.get_pkmn(pkmn_name), pkmn_level)
    
    def create_wild_pkmn(self, pkmn_name, pkmn_level):
        return pkmn_utils.instantiate_wild_pokemon(self._pkmn_db.get_pkmn(pkmn_name), pkmn_level)
    
    def get_crit_rate(self, pkmn, move):
        return pkmn_damage_calc.get_crit_rate(pkmn, move)

    def calculate_damage(self,
        attacking_pkmn:universal_data_objects.EnemyPkmn,
        move:universal_data_objects.Move,
        defending_pkmn:universal_data_objects.EnemyPkmn,
        attacking_stage_modifiers:universal_data_objects.StageModifiers=None,
        defending_stage_modifiers:universal_data_objects.StageModifiers=None,
        is_crit:bool=False
    ) -> DamageRange:
        return pkmn_damage_calc.calculate_damage(
            attacking_pkmn,
            move,
            defending_pkmn,
            attacking_stage_modifiers=attacking_stage_modifiers,
            defending_stage_modifiers=defending_stage_modifiers,
            is_crit=is_crit
        )
    
    def make_stat_block(self, hp, attack, defense, special_attack, special_defense, speed, is_stat_xp=False) -> universal_data_objects.StatBlock:
        return GenTwoStatBlock(hp, attack, defense, special_attack, special_defense, speed, is_stat_xp=is_stat_xp)
    
    def make_badge_list(self) -> universal_data_objects.BadgeList:
        return GenTwoBadgeList()
    
    def make_inventory(self) -> route_state_objects.Inventory:
        return route_state_objects.Inventory(bag_limit=gen_two_const.BAG_LIMIT)
    
    def get_stat_modifer_moves(self) -> List[str]:
        return (
            list(gen_two_const.STAT_INCREASE_MOVES.keys()) +
            list(gen_two_const.STAT_DECREASE_MOVES.keys())
        )
    
    def get_fight_reward(self, trainer_name) -> str:
        return gen_two_const.FIGHT_REWARDS.get(trainer_name)
    
    def is_minor_fight(self, trainer_name) -> str:
        return trainer_name in gen_two_const.MINOR_FIGHTS
    
    def is_major_fight(self, trainer_name) -> str:
        return trainer_name in gen_two_const.MAJOR_FIGHTS

def _load_pkmn_db(path):
    result = {}
    with open(path, 'r') as f:
        raw_pkmn_db = json.load(f)

    for cur_pkmn in raw_pkmn_db.values():
        result[cur_pkmn[const.NAME_KEY]] = universal_data_objects.PokemonSpecies(
            cur_pkmn[const.NAME_KEY],
            cur_pkmn[const.GROWTH_RATE_KEY],
            cur_pkmn[const.BASE_XP_KEY],
            cur_pkmn[const.FIRST_TYPE_KEY],
            cur_pkmn[const.SECOND_TYPE_KEY],
            GenTwoStatBlock(
                cur_pkmn[const.BASE_HP_KEY],
                cur_pkmn[const.BASE_ATK_KEY],
                cur_pkmn[const.BASE_DEF_KEY],
                cur_pkmn[const.BASE_SPA_KEY],
                cur_pkmn[const.BASE_SPD_KEY],
                cur_pkmn[const.OLD_BASE_SPD_KEY],
            ),
            [],
            cur_pkmn[const.LEARNED_MOVESET_KEY],
            cur_pkmn[const.TM_HM_LEARNSET_KEY]
        )

    return result


def _create_trainer(trainer_dict, pkmn_db:PkmnDB) -> universal_data_objects.Trainer:
    enemy_pkmn = []
    for cur_mon in trainer_dict[const.TRAINER_POKEMON]:
        enemy_pkmn.append(
            universal_data_objects.EnemyPkmn(
                cur_mon[const.NAME_KEY],
                cur_mon[const.LEVEL],
                cur_mon[const.XP],
                copy.copy(cur_mon[const.MOVES]),
                GenTwoStatBlock(
                    cur_mon[const.HP],
                    cur_mon[const.ATK],
                    cur_mon[const.DEF],
                    cur_mon[const.SPA],
                    cur_mon[const.SPD],
                    cur_mon[const.SPE],
                ),
                pkmn_db.get_pkmn(cur_mon[const.NAME_KEY]).stats,
                GenTwoStatBlock(
                    trainer_dict[const.DVS_KEY][const.HP],
                    trainer_dict[const.DVS_KEY][const.ATK],
                    trainer_dict[const.DVS_KEY][const.DEF],
                    trainer_dict[const.DVS_KEY][const.SPA],
                    trainer_dict[const.DVS_KEY][const.SPA],
                    trainer_dict[const.DVS_KEY][const.SPE]
                ),
                GenTwoStatBlock(0, 0, 0, 0, 0, 0),
                None,
            )
        )

    return universal_data_objects.Trainer(
        trainer_dict[const.TRAINER_CLASS],
        trainer_dict[const.TRAINER_NAME],
        trainer_dict[const.TRAINER_LOC],
        trainer_dict[const.MONEY],
        "NotImplementedYet",
        enemy_pkmn,
        rematch=("Rematch" in trainer_dict[const.TRAINER_NAME])
    )


def _load_trainer_db(path, pkmn_db:PkmnDB):
    result = {}
    with open(path, 'r') as f:
        raw_db = json.load(f)

    for raw_trainer in raw_db.values():
        # ignoring all unused trainers
        if raw_trainer[const.TRAINER_LOC] == const.UNUSED_TRAINER_LOC:
            continue
        result[raw_trainer[const.TRAINER_NAME]] = _create_trainer(raw_trainer, pkmn_db)
    
    return result


def _load_item_db(path):
    result = {}

    with open(path, 'r') as f:
        raw_db = json.load(f)

    for raw_item in raw_db.values():
        item_name:str = raw_item[const.NAME_KEY]
        move_name = None
        if item_name.startswith("TM") or item_name.startswith("HM"):
            move_name = item_name.split(" ", 1)[1]

        result[item_name] = universal_data_objects.BaseItem(
            item_name,
            raw_item[const.IS_KEY_ITEM],
            raw_item[const.PURCHASE_PRICE],
            raw_item[const.MARTS],
            move_name,
        )
    
    return result


def _load_move_db(path):
    result = {}
    with open(path, 'r') as f:
        raw_db = json.load(f)

    for raw_move in raw_db.values():
        result[raw_move[const.NAME_KEY]] = universal_data_objects.Move(
            raw_move[const.NAME_KEY],
            raw_move[const.MOVE_ACCURACY],
            raw_move[const.MOVE_PP],
            raw_move[const.BASE_POWER],
            raw_move[const.MOVE_TYPE],
            raw_move[const.MOVE_EFFECTS],
            raw_move[const.MOVE_FLAVOR],
        )
    
    return result


gen_two_crystal = GenTwo(
    gen_two_const.CRYSTAL_POKEMON_PATH,
    gen_two_const.CRYSTAL_TRAINER_DB_PATH,
    gen_two_const.MIN_BATTLES_DIR,
    const.CRYSTAL_VERSION
)


gen_two_gold = GenTwo(
    gen_two_const.GS_POKEMON_PATH,
    gen_two_const.GS_TRAINER_DB_PATH,
    gen_two_const.MIN_BATTLES_DIR,
    const.GOLD_VERSION
)

gen_two_silver = GenTwo(
    gen_two_const.GS_POKEMON_PATH,
    gen_two_const.GS_TRAINER_DB_PATH,
    gen_two_const.MIN_BATTLES_DIR,
    const.SILVER_VERSION
)