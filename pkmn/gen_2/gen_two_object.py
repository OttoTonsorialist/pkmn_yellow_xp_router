from ast import Dict
import json
import copy
import math
import os
import shutil
from typing import List, Tuple
import logging

from pkmn import universal_data_objects
from pkmn.gen_2 import pkmn_damage_calc
from pkmn.damage_calc import DamageRange
from pkmn.gen_2.data_objects import GenTwoBadgeList, GenTwoStatBlock, instantiate_trainer_pokemon, instantiate_wild_pokemon, get_hidden_power_base_power, get_hidden_power_type, VIT_AMT, VIT_CAP
from pkmn.gen_2.gen_two_constants import gen_two_const
from pkmn.pkmn_db import ItemDB, MinBattlesDB, PkmnDB, TrainerDB, MoveDB
from pkmn.pkmn_info import CurrentGen
from route_recording.game_recorders.gen_two.crystal_recorder import CrystalRecorder
from route_recording.recorder import RecorderController, RecorderGameHookClient
from routing import full_route_state
from utils.constants import const
from utils import io_utils

logger = logging.getLogger(__name__)


class GenTwo(CurrentGen):
    def __init__(self, pkmn_db_path, trainer_db_path, item_path, move_path, type_info_path, fight_info_path, min_battles_path, version_name, base_version_name=None):
        self._version_name = version_name
        self._base_version_name = base_version_name

        self._all_flat_files = [
            pkmn_db_path, trainer_db_path, item_path, move_path, type_info_path, fight_info_path
        ]

        try:
            self._pkmn_db = PkmnDB(_load_pkmn_db(pkmn_db_path))
        except Exception as e:
            logger.error(f"Error loading pokemon DB: {pkmn_db_path}")
            logger.exception(e)
            raise ValueError(f"Failed to load pokemon DB: {e}")

        try:
            self._trainer_db = TrainerDB(
                _load_trainer_db(
                    trainer_db_path,
                    self._pkmn_db,
                    extract_trainer_id=(
                        version_name == const.CRYSTAL_VERSION or
                        base_version_name == const.CRYSTAL_VERSION
                    )
                )
            )
        except Exception as e:
            logger.error(f"Error loading trainer DB: {pkmn_db_path}")
            logger.exception(e)
            raise ValueError(f"Failed to load trainer DB: {e}")

        try:
            self._item_db = ItemDB(_load_item_db(item_path))
        except Exception as e:
            logger.error(f"Error loading item DB: {pkmn_db_path}")
            logger.exception(e)
            raise ValueError(f"Failed to load item DB: {e}")
        
        try:
            self._move_db = MoveDB(_load_move_db(move_path))
        except Exception as e:
            logger.error(f"Error loading move DB: {pkmn_db_path}")
            logger.exception(e)
            raise ValueError(f"Failed to load move DB: {e}")

        try:
            self._min_battles_db = MinBattlesDB(min_battles_path)
        except Exception as e:
            logger.error(f"Error loading min battles DB: {pkmn_db_path}")
            logger.exception(e)
            raise ValueError(f"Failed to load min battles DB: {e}")

        try:
            with open(type_info_path, 'r') as f:
                type_info = json.load(f)
            
            self._special_types:List[str] = type_info[const.SPECIAL_TYPES_KEY]
            self._type_chart:Dict[str, Dict[str, str]] = type_info[const.TYPE_CHART_KEY]
            self._held_item_boosts:Dict[str, str] = type_info[const.HELD_ITEM_BOOSTS_KEY]
        except Exception as e:
            logger.error(f"Error loading type info: {pkmn_db_path}")
            logger.exception(e)
            raise ValueError(f"Failed to load type info: {e}")

        try:
            with open(fight_info_path, 'r') as f:
                fight_info = json.load(f)
            
            self._badge_rewards:Dict[str, str] = fight_info[const.BADGE_REWARDS_KEY]
            self._major_fights:List[str] = fight_info[const.MAJOR_FIGHTS_KEY]
            self._fight_rewards:Dict[str, str] = fight_info[const.FIGHT_REWARDS_KEY]

            timing_info = fight_info.get(const.TRAINER_TIMING_INFO_KEY, {})
            self._trainer_timing_info = universal_data_objects.TrainerTimingStats(
                timing_info.get(const.INTRO_TIME_KEY, const.DEFAULT_INTRO_TIME),
                timing_info.get(const.OUTRO_TIME_KEY, const.DEFAULT_OUTRO_TIME),
                timing_info.get(const.KO_TIME_KEY, const.DEFAULT_KO_TIME),
                timing_info.get(const.SEND_OUT_TIME_KEY, const.DEFAULT_SEND_OUT_TIME)
            )
        except Exception as e:
            logger.error(f"Error loading fight info: {pkmn_db_path}")
            logger.exception(e)
            raise ValueError(f"Failed to load fight info: {e}")

        supported_types = self._type_chart.keys()
        self._validate_special_types(supported_types)
        self._move_db.validate_move_types(supported_types)
        self._item_db.validate_tms_hms(self._move_db)
        self._validate_fight_rewards()
        self._validate_held_item_boosts(supported_types)
        self._pkmn_db.validate_types(supported_types)
        self._pkmn_db.validate_moves(self._move_db)
        self._trainer_db.validate_trainers(self._pkmn_db, self._move_db)

    def version_name(self) -> str:
        return self._version_name

    def base_version_name(self) -> str:
        return self._base_version_name
    
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

    def get_recorder_client(self, recorder_controller:RecorderController) -> RecorderGameHookClient:
        version_name = self._base_version_name
        if version_name is None:
            version_name = self._version_name

        if version_name == const.CRYSTAL_VERSION:
            return CrystalRecorder(recorder_controller, ["Pokemon Crystal"])

        raise NotImplementedError()

    def create_trainer_pkmn(self, pkmn_name, pkmn_level):
        return instantiate_trainer_pokemon(self._pkmn_db.get_pkmn(pkmn_name), pkmn_level)
    
    def create_wild_pkmn(self, pkmn_name, pkmn_level):
        return instantiate_wild_pokemon(self._pkmn_db.get_pkmn(pkmn_name), pkmn_level)
    
    def get_crit_rate(self, pkmn, move, custom_move_data):
        return pkmn_damage_calc.get_crit_rate(pkmn, move)
    
    def get_move_accuracy(self, pkmn, move, custom_move_data, defending_pkmn, weather):
        return move.accuracy

    def calculate_damage(self,
        attacking_pkmn:universal_data_objects.EnemyPkmn,
        move:universal_data_objects.Move,
        defending_pkmn:universal_data_objects.EnemyPkmn,
        attacking_stage_modifiers:universal_data_objects.StageModifiers=None,
        defending_stage_modifiers:universal_data_objects.StageModifiers=None,
        is_crit:bool=False,
        custom_move_data:str="",
        weather:str=const.WEATHER_NONE,
        is_double_battle:bool=False,
    ) -> DamageRange:
        return pkmn_damage_calc.calculate_gen_two_damage(
            attacking_pkmn,
            self.pkmn_db().get_pkmn(attacking_pkmn.name),
            move,
            defending_pkmn,
            self.pkmn_db().get_pkmn(defending_pkmn.name),
            self._special_types,
            self._type_chart,
            self._held_item_boosts,
            attacking_stage_modifiers=attacking_stage_modifiers,
            defending_stage_modifiers=defending_stage_modifiers,
            is_crit=is_crit,
            custom_move_data=custom_move_data,
            weather=weather
        )
    
    def make_stat_block(self, hp, attack, defense, special_attack, special_defense, speed, is_stat_xp=False) -> universal_data_objects.StatBlock:
        return GenTwoStatBlock(hp, attack, defense, special_attack, special_defense, speed, is_stat_xp=is_stat_xp)
    
    def make_badge_list(self) -> universal_data_objects.BadgeList:
        return GenTwoBadgeList(self._badge_rewards)
    
    def make_inventory(self) -> full_route_state.Inventory:
        return full_route_state.Inventory()
    
    def get_stat_modifer_moves(self) -> List[str]:
        return sorted([self._move_db.get_move(x).name for x in self._move_db.stat_mod_moves.keys()])
    
    def get_fight_reward(self, trainer_name) -> str:
        return self._fight_rewards.get(trainer_name)
    
    def is_major_fight(self, trainer_name) -> str:
        return trainer_name in self._major_fights
    
    def get_move_custom_data(self, move_name) -> List[str]:
        return gen_two_const.CUSTOM_MOVE_DATA.get(move_name)
    
    def get_hidden_power(self, dvs: universal_data_objects.StatBlock) -> Tuple[str, int]:
        return get_hidden_power_type(dvs), get_hidden_power_base_power(dvs)

    def get_valid_weather(self) -> List[str]:
        return [const.WEATHER_NONE, const.WEATHER_SUN, const.WEATHER_RAIN, const.WEATHER_SANDSTORM]
    
    def get_stats_boosted_by_vitamin(self, vit_name: str) -> List[str]:
        if vit_name == const.HP_UP:
            return [const.HP]
        elif vit_name == const.PROTEIN:
            return [const.ATK]
        elif vit_name == const.IRON:
            return [const.DEF]
        elif vit_name == const.CALCIUM:
            return [const.SPA, const.SPD]
        elif vit_name == const.CARBOS:
            return [const.SPE]

        raise ValueError(f"Unknown vitamin: {vit_name}")

    def get_valid_vitamins(self) -> List[str]:
        return [const.HP_UP, const.CARBOS, const.IRON, const.CALCIUM, const.PROTEIN]
    
    def get_vitamin_amount(self) -> int:
        return VIT_AMT
    
    def get_vitamin_cap(self) -> int:
        return VIT_CAP

    def create_new_custom_gen(self, new_version_name):
        folder_name = io_utils.get_safe_path_no_collision(const.CUSTOM_GENS_DIR, new_version_name)
        os.makedirs(folder_name)

        for cur_file in self._all_flat_files:
            shutil.copy2(cur_file, os.path.join(folder_name, os.path.basename(cur_file)))

        # create metadata json file for custom version
        with open(os.path.join(folder_name, const.CUSTOM_GEN_META_FILE_NAME), 'w') as f:
            json.dump(
                {
                    const.CUSTOM_GEN_NAME_KEY: new_version_name,
                    const.BASE_GEN_NAME_KEY: self._version_name
                },
                f, indent=4
            )
    
    def load_custom_gen(self, custom_version_name, root_path) -> CurrentGen:
        return GenTwo(
            os.path.join(root_path, const.POKEMON_DB_FILE_NAME),
            os.path.join(root_path, const.TRAINERS_DB_FILE_NAME),
            os.path.join(root_path, const.ITEM_DB_FILE_NAME),
            os.path.join(root_path, const.MOVE_DB_FILE_NAME),
            os.path.join(root_path, const.TYPE_INFO_FILE_NAME),
            os.path.join(root_path, const.FIGHTS_INFO_FILE_NAME),
            "",
            custom_version_name,
            base_version_name=self._version_name
        )
    
    def get_trainer_timing_info(self) -> universal_data_objects.TrainerTimingStats:
        return self._trainer_timing_info
    
    def get_stat_xp_yield(self, pkmn_name:str, exp_split:int, held_item:str) -> universal_data_objects.StatBlock:
        stat_xp_yield = self.pkmn_db().get_pkmn(pkmn_name).stat_xp_yield
        return GenTwoStatBlock(
            math.floor(stat_xp_yield.hp / exp_split),
            math.floor(stat_xp_yield.attack / exp_split),
            math.floor(stat_xp_yield.defense / exp_split),
            math.floor(stat_xp_yield.special_attack / exp_split),
            math.floor(stat_xp_yield.special_defense / exp_split),
            math.floor(stat_xp_yield.speed / exp_split),
            is_stat_xp=True
        )
    
    def _validate_special_types(self, supported_types):
        invalid_types = []
        for cur_type in self._special_types:
            if cur_type not in supported_types:
                invalid_types.append(cur_type)
        
        if invalid_types:
            raise ValueError(f"Detected invalid special type(s): {invalid_types}")
    
    def _validate_held_item_boosts(self, supported_types):
        invalid_types = []
        for cur_item, cur_type in self._held_item_boosts.items():
            if cur_type not in supported_types:
                invalid_types.append((cur_item, cur_type))
            elif self._item_db.get_item(cur_item) == None:
                invalid_types.append((cur_item, cur_type))
        
        if invalid_types:
            raise ValueError(f"Detected invalid item boosts: {invalid_types}")
    
    def _validate_fight_rewards(self):
        invalid_rewards = []
        for cur_fight, cur_reward in self._fight_rewards.items():
            if self._item_db.get_item(cur_reward) is None:
                invalid_rewards.append((cur_fight, cur_reward))
        
        if len(invalid_rewards) > 0:
            raise ValueError(f"Invalid Fight Rewards: {invalid_rewards}")


def _load_pkmn_db(path):
    result = {}
    with open(path, 'r') as f:
        raw_pkmn_db = json.load(f)

    all_pkmn = raw_pkmn_db.get("pokemon", raw_pkmn_db.values())
    for cur_pkmn in all_pkmn:
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
            cur_pkmn[const.TM_HM_LEARNSET_KEY],
            GenTwoStatBlock(
                cur_pkmn[const.BASE_HP_KEY],
                cur_pkmn[const.BASE_ATK_KEY],
                cur_pkmn[const.BASE_DEF_KEY],
                cur_pkmn[const.BASE_SPA_KEY],
                cur_pkmn[const.BASE_SPD_KEY],
                cur_pkmn[const.OLD_BASE_SPD_KEY],
            ),
            [""]
        )

    return result


def _create_trainer(trainer_dict, pkmn_db:PkmnDB, extract_trainer_id=False) -> universal_data_objects.Trainer:
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
                held_item=cur_mon[const.HELD_ITEM_KEY],
                is_trainer_mon=True
            )
        )
    
    if extract_trainer_id:
        try:
            trainer_id = trainer_dict[const.TRAINER_ID]
        except Exception as e:
            raise KeyError(f"Issue with {trainer_dict[const.TRAINER_NAME]}") from e
    else:
        trainer_id = -1

    return universal_data_objects.Trainer(
        trainer_dict[const.TRAINER_CLASS],
        trainer_dict[const.TRAINER_NAME],
        trainer_dict[const.TRAINER_LOC],
        trainer_dict[const.MONEY],
        enemy_pkmn,
        rematch=("Rematch" in trainer_dict[const.TRAINER_NAME]),
        trainer_id=trainer_id,
        refightable=trainer_dict.get(const.TRAINER_REFIGHTABLE, False)
    )


def _load_trainer_db(path, pkmn_db:PkmnDB, extract_trainer_id=False):
    result = {}
    with open(path, 'r') as f:
        raw_db = json.load(f)

    all_trainers = raw_db.get("trainers", raw_db.values())
    for raw_trainer in all_trainers:
        # ignoring all unused trainers
        if raw_trainer[const.TRAINER_LOC] == const.UNUSED_TRAINER_LOC:
            continue
        result[raw_trainer[const.TRAINER_NAME]] = _create_trainer(raw_trainer, pkmn_db, extract_trainer_id=extract_trainer_id)
    
    return result


def _load_item_db(path):
    result = {}

    with open(path, 'r') as f:
        raw_db = json.load(f)

    all_items = raw_db.get("items", raw_db.values())
    for raw_item in all_items:
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

    all_moves = raw_db.get("moves", raw_db.values())
    for raw_move in all_moves:
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
    gen_two_const.ITEM_DB_PATH,
    gen_two_const.MOVE_DB_PATH,
    gen_two_const.TYPE_INFO_PATH,
    gen_two_const.FIGHTS_INFO_PATH,
    gen_two_const.CRYSTAL_MIN_BATTLES_DIR,
    const.CRYSTAL_VERSION
)


gen_two_gold = GenTwo(
    gen_two_const.GS_POKEMON_PATH,
    gen_two_const.GS_TRAINER_DB_PATH,
    gen_two_const.ITEM_DB_PATH,
    gen_two_const.MOVE_DB_PATH,
    gen_two_const.TYPE_INFO_PATH,
    gen_two_const.FIGHTS_INFO_PATH,
    gen_two_const.GS_MIN_BATTLES_DIR,
    const.GOLD_VERSION
)

gen_two_silver = GenTwo(
    gen_two_const.GS_POKEMON_PATH,
    gen_two_const.GS_TRAINER_DB_PATH,
    gen_two_const.ITEM_DB_PATH,
    gen_two_const.MOVE_DB_PATH,
    gen_two_const.TYPE_INFO_PATH,
    gen_two_const.FIGHTS_INFO_PATH,
    gen_two_const.GS_MIN_BATTLES_DIR,
    const.SILVER_VERSION
)