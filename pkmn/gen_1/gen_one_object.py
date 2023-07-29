import json
import copy
from typing import Dict, List, Tuple
import os
import shutil
import logging

from pkmn import universal_data_objects
from pkmn.gen_1 import pkmn_damage_calc, pkmn_utils
from pkmn.damage_calc import DamageRange
from pkmn.gen_1.data_objects import GenOneBadgeList, GenOneStatBlock
from pkmn.gen_1.gen_one_constants import gen_one_const
from pkmn.pkmn_db import ItemDB, MinBattlesDB, PkmnDB, TrainerDB, MoveDB
from pkmn.pkmn_info import CurrentGen
from route_recording.game_recorders.gen_one.yellow_recorder import YellowRecorder, RedBlueRecorder
from route_recording.recorder import RecorderController, RecorderGameHookClient
from routing import full_route_state
from utils.constants import const
from utils import io_utils

logger = logging.getLogger(__name__)


class GenOne(CurrentGen):
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
            self._trainer_db = TrainerDB(_load_trainer_db(trainer_db_path, self._pkmn_db))
        except Exception as e:
            logger.error(f"Error loading trainer DB: {pkmn_db_path}")
            logger.exception(e)
            raise ValueError(f"Failed to load trainer DB: {e}")

        try:
            self._item_db = ItemDB(_load_item_db(item_path))
        except Exception as e:
            logger.error(f"Error loading trainer DB: {pkmn_db_path}")
            logger.exception(e)
            raise ValueError(f"Failed to load trainer DB: {e}")

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
        except Exception as e:
            logger.error(f"Error loading fight info: {pkmn_db_path}")
            logger.exception(e)
            raise ValueError(f"Failed to load fight info: {e}")

        supported_types = self._type_chart.keys()
        self._validate_special_types(supported_types)
        self._move_db.validate_move_types(supported_types)
        self._item_db.validate_tms_hms(self._move_db)
        self._validate_fight_rewards()
        self._pkmn_db.validate_types(supported_types)
        self._pkmn_db.validate_moves(self._move_db)
        self._trainer_db.validate_trainers(self._pkmn_db, self._move_db)

    def version_name(self) -> str:
        return self._version_name
    
    def base_version_name(self) -> str:
        return self._base_version_name
    
    def get_generation(self) -> int:
        return 1

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

        if version_name == const.YELLOW_VERSION:
            return YellowRecorder(recorder_controller, ["Pokemon Yellow"])
        return RedBlueRecorder(recorder_controller, ["Pokemon Red and Blue", "Pokemon Red/Blue"])

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
        is_crit:bool=False,
        custom_move_data:str="",
        weather:str=const.WEATHER_NONE,
    ) -> DamageRange:
        return pkmn_damage_calc.calculate_gen_one_damage(
            attacking_pkmn,
            self.pkmn_db().get_pkmn(attacking_pkmn.name),
            move,
            defending_pkmn,
            self.pkmn_db().get_pkmn(defending_pkmn.name),
            self._special_types,
            self._type_chart,
            attacking_stage_modifiers=attacking_stage_modifiers,
            defending_stage_modifiers=defending_stage_modifiers,
            is_crit=is_crit,
            custom_move_data=custom_move_data
        )
    
    def make_stat_block(self, hp, attack, defense, special_attack, special_defense, speed, is_stat_xp=False) -> universal_data_objects.StatBlock:
        return GenOneStatBlock(hp, attack, defense, special_attack, special_defense, speed, is_stat_xp=is_stat_xp)
    
    def make_badge_list(self) -> universal_data_objects.BadgeList:
        return GenOneBadgeList(self._badge_rewards)
    
    def make_inventory(self) -> full_route_state.Inventory:
        return full_route_state.Inventory(bag_limit=gen_one_const.BAG_LIMIT)
    
    def get_stat_modifer_moves(self) -> List[str]:
        return [self._move_db.get_move(x).name for x in self._move_db.stat_mod_moves.keys()]
    
    def get_fight_reward(self, trainer_name) -> str:
        return self._fight_rewards.get(trainer_name)
    
    def is_major_fight(self, trainer_name) -> str:
        return trainer_name in self._major_fights
    
    def get_move_custom_data(self, move_name) -> List[str]:
        # Gen one moves that require custom data are already handled by the rendering engine
        # Mimc, and all multi-hit moves
        # so, no other moves will need custom data
        return None
    
    def get_hidden_power(self, dvs: universal_data_objects.StatBlock) -> Tuple[str, int]:
        return "", 0
    
    def get_valid_weather(self) -> List[str]:
        return [const.WEATHER_NONE]
    
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
    
    def get_vitamin_amount(self) -> int:
        return pkmn_utils.VIT_AMT
    
    def get_vitamin_cap(self) -> int:
        return pkmn_utils.VIT_CAP
    
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
        return GenOne(
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
    
    def _validate_special_types(self, supported_types):
        invalid_types = []
        for cur_type in self._special_types:
            if cur_type not in supported_types:
                invalid_types.append(cur_type)
        
        if invalid_types:
            raise ValueError(f"Detected invalid special type(s): {invalid_types}")
    
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

    for cur_pkmn in raw_pkmn_db.values():
        result[cur_pkmn[const.NAME_KEY]] = universal_data_objects.PokemonSpecies(
            cur_pkmn[const.NAME_KEY],
            cur_pkmn[const.GROWTH_RATE_KEY],
            cur_pkmn[const.BASE_XP_KEY],
            cur_pkmn[const.FIRST_TYPE_KEY],
            cur_pkmn[const.SECOND_TYPE_KEY],
            GenOneStatBlock(
                cur_pkmn[const.BASE_HP_KEY],
                cur_pkmn[const.BASE_ATK_KEY],
                cur_pkmn[const.BASE_DEF_KEY],
                cur_pkmn[const.BASE_SPC_KEY],
                cur_pkmn[const.BASE_SPC_KEY],
                cur_pkmn[const.OLD_BASE_SPD_KEY],
            ),
            cur_pkmn[const.INITIAL_MOVESET_KEY],
            cur_pkmn[const.LEARNED_MOVESET_KEY],
            cur_pkmn[const.TM_HM_LEARNSET_KEY]
        )

    return result


def _create_trainer(trainer_dict, pkmn_db:PkmnDB) -> universal_data_objects.Trainer:
    enemy_pkmn = []
    for cur_mon in trainer_dict[const.TRAINER_POKEMON]:
        if pkmn_db.get_pkmn(cur_mon[const.NAME_KEY]) is None:
            raise ValueError(f"Invalid mon found when creating trainer: {trainer_dict[const.TRAINER_NAME], cur_mon[const.NAME_KEY]}")
        enemy_pkmn.append(
            universal_data_objects.EnemyPkmn(
                cur_mon[const.NAME_KEY],
                cur_mon[const.LEVEL],
                cur_mon[const.XP],
                copy.copy(cur_mon[const.MOVES]),
                GenOneStatBlock(
                    cur_mon[const.HP],
                    cur_mon[const.ATK],
                    cur_mon[const.DEF],
                    cur_mon[const.SPC],
                    cur_mon[const.SPC],
                    cur_mon[const.SPD],
                ),
                pkmn_db.get_pkmn(cur_mon[const.NAME_KEY]).stats,
                GenOneStatBlock(8, 9, 8, 8, 8, 8),
                GenOneStatBlock(0, 0, 0, 0, 0, 0),
                None,
            )
        )

    return universal_data_objects.Trainer(
        trainer_dict[const.TRAINER_CLASS],
        trainer_dict[const.TRAINER_NAME],
        trainer_dict[const.TRAINER_LOC],
        trainer_dict[const.MONEY],
        enemy_pkmn,
        refightable=trainer_dict.get(const.TRAINER_REFIGHTABLE, False)
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
            # TODO: update underlying data to actually store with lists, instead of forcing it here
            [raw_move[const.MOVE_FLAVOR]],
        )
    
    return result


gen_one_yellow = GenOne(
    gen_one_const.YELLOW_POKEMON_DB_PATH,
    gen_one_const.YELLOW_TRAINER_DB_PATH,
    gen_one_const.ITEM_DB_PATH,
    gen_one_const.MOVE_DB_PATH,
    gen_one_const.TYPE_INFO_PATH,
    gen_one_const.FIGHTS_INFO_PATH,
    gen_one_const.YELLOW_MIN_BATTLES_DIR,
    const.YELLOW_VERSION
)


gen_one_blue = GenOne(
    gen_one_const.RB_POKEMON_DB_PATH,
    gen_one_const.RB_TRAINER_DB_PATH,
    gen_one_const.ITEM_DB_PATH,
    gen_one_const.MOVE_DB_PATH,
    gen_one_const.TYPE_INFO_PATH,
    gen_one_const.FIGHTS_INFO_PATH,
    gen_one_const.RB_MIN_BATTLES_DIR,
    const.BLUE_VERSION
)

gen_one_red = GenOne(
    gen_one_const.RB_POKEMON_DB_PATH,
    gen_one_const.RB_TRAINER_DB_PATH,
    gen_one_const.ITEM_DB_PATH,
    gen_one_const.MOVE_DB_PATH,
    gen_one_const.TYPE_INFO_PATH,
    gen_one_const.FIGHTS_INFO_PATH,
    gen_one_const.RB_MIN_BATTLES_DIR,
    const.RED_VERSION
)