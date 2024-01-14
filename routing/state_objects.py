import logging
from typing import List
from copy import copy

from utils.constants import const
import pkmn.universal_utils
import pkmn.universal_data_objects

logger = logging.getLogger(__name__)


class BagItem:
    def __init__(self, base_item, num):
        self.base_item:pkmn.universal_data_objects.BaseItem = base_item
        self.num = num
    
    def __eq__(self, other):
        if not isinstance(other,BagItem):
            return False
        return (
            self.base_item.name == other.base_item.name and
            self.num == other.num
        )


class Inventory:
    def __init__(self, cur_money=None, cur_items:List[BagItem]=None, bag_limit=None):
        if cur_money is None:
            cur_money = 3000
        self.cur_money = cur_money

        if cur_items is None:
            cur_items = []
        self.cur_items:List[BagItem] = [BagItem(x.base_item, x.num) for x in cur_items]
        self._bag_limit = bag_limit
        self._item_lookup = dict()
        self._reindex_lookup()
    
    def _reindex_lookup(self):
        self._item_lookup = {x.base_item.name: idx for idx, x in enumerate(self.cur_items)}
    
    def _copy(self):
        return Inventory(cur_money=self.cur_money, cur_items=self.cur_items, bag_limit=self._bag_limit)
    
    def add_item(self, base_item:pkmn.universal_data_objects.BaseItem, num, is_purchase=False, force=False):
        result = self._copy()
        if is_purchase:
            total_cost = num * base_item.purchase_price
            if total_cost > result.cur_money and not force:
                raise ValueError(f"Cannot purchase {num} {base_item.name} for {total_cost} with only {result.cur_money} money")
            # when forcing, allow money to go negative, so you can get a sense for the rest of the money management of the route
            result.cur_money -= total_cost

        if base_item.name in result._item_lookup:
            if base_item.is_key_item and not force:
                raise ValueError(f"Cannot have multiple of the same key item: {base_item.name}")

            result.cur_items[result._item_lookup[base_item.name]].num += num
        elif self._bag_limit is not None and len(result.cur_items) >= self._bag_limit and not force:
            raise ValueError(f"Cannot add more than {self._bag_limit} items to bag")
        elif self._bag_limit is not None and len(result.cur_items) < self._bag_limit:
            # looks kind of weird, but when we're forcing, we don't want to error
            # but we still don't have room in the bag. So we just have to ignore that item...
            result._item_lookup[base_item.name] = len(result.cur_items)
            result.cur_items.append(BagItem(base_item, num))
        elif self._bag_limit is None:
            result._item_lookup[base_item.name] = len(result.cur_items)
            result.cur_items.append(BagItem(base_item, num))
        
        return result
    
    def remove_item(self, base_item:pkmn.universal_data_objects.BaseItem, num, is_sale=False, force=False):
        if base_item.name not in self._item_lookup:
            if force:
                if is_sale:
                    result = self._copy()
                    result.cur_money += (base_item.sell_price * num)
                    return result
                else:
                    return self
            raise ValueError(f"Cannot sell/use item that you do not have: {base_item.name}")

        if base_item.is_key_item and is_sale and not force:
            raise ValueError(f"Cannot sell key item: {base_item.name}")
        
        result = self._copy()
        bag_item = result.cur_items[result._item_lookup[base_item.name]]
        if bag_item.num < num and not force:
            raise ValueError(f"Cannot sell/use {num} {base_item.name} when you only have {bag_item.num}")
        
        bag_item.num -= num
        if bag_item.num <= 0:
            del result.cur_items[result._item_lookup[base_item.name]]
            result._reindex_lookup()
        
        if is_sale:
            result.cur_money += (base_item.sell_price * num)
        
        return result
    
    def __eq__(self, other):
        if not isinstance(other, Inventory):
            return False
        
        if self.cur_money != other.cur_money:
            return False

        if len(self.cur_items) != len(other.cur_items):
            return False
        
        for cur_idx in range(len(self.cur_items)):
            if self.cur_items[cur_idx] != other.cur_items[cur_idx]:
                return False
        
        return True

class SoloPokemon:
    """
    This is not considered a mutable object!!!
    Represents a snapshot of a pokemon at a single moment in time
    All methods to apply changes will return a new object
    """
    def __init__(self,
            name,
            species_def:pkmn.universal_data_objects.PokemonSpecies,
            dvs:pkmn.universal_data_objects.StatBlock,
            badges:pkmn.universal_data_objects.BadgeList,
            empty_stat_block:pkmn.universal_data_objects.StatBlock,
            ability:str,
            nature:pkmn.universal_data_objects.Nature,
            move_list:list=None,
            cur_xp:int=0,
            realized_stat_xp:pkmn.universal_data_objects.StatBlock=None,
            unrealized_stat_xp:pkmn.universal_data_objects.StatBlock=None,
            gained_xp:int=0,
            gained_stat_xp:pkmn.universal_data_objects.StatBlock=None,
            held_item:str=None,
    ):
        self.name = name
        self.species_def = species_def
        self.dvs = dvs
        self.badges = badges
        self.held_item = held_item
        self.ability = ability
        self.nature = nature
        # just need to hold on to a reference for a few places
        self._empty_stat_block = empty_stat_block

        if cur_xp == 0:
            # if no initial XP is defined, assume creating a new level 5 pkmn
            try:
                self.cur_xp = pkmn.universal_utils.level_lookups[self.species_def.growth_rate].get_xp_for_level(5)
            except KeyError as e:
                raise ValueError(f"Invalid growth rate: {self.species_def.growth_rate}") from e
        else:
            self.cur_xp = cur_xp

        if badges is None:
            badges = pkmn.universal_data_objects.BadgeList()

        level_info = pkmn.universal_utils.level_lookups[self.species_def.growth_rate].get_level_info(self.cur_xp)
        self.cur_level = level_info[0]
        self.xp_to_next_level = level_info[1]

        if move_list is None:
            self.move_list = [x for x in species_def.initial_moves]
            for try_learn_move in species_def.levelup_moves:
                if try_learn_move[0] <= self.cur_level and try_learn_move[1] not in self.move_list:
                    self.move_list.append(try_learn_move[1])
                if len(self.move_list) > 4:
                    self.move_list = self.move_list[-4:]

            while len(self.move_list) < 4:
                self.move_list.append(None)
        else:
            self.move_list = move_list

        if realized_stat_xp is None:
            realized_stat_xp = copy(self._empty_stat_block)
            realized_stat_xp._is_stat_xp = True
        self.realized_stat_xp = realized_stat_xp

        if unrealized_stat_xp is None:
            unrealized_stat_xp = copy(self.realized_stat_xp)
        self.unrealized_stat_xp = unrealized_stat_xp

        if gained_stat_xp is None:
            gained_stat_xp = copy(self._empty_stat_block)
        
        if const.DEBUG_MODE:
            logger.info(f"Gaining {gained_xp}, was at {self.cur_xp}, now at {self.cur_xp + gained_xp}. Before gain, needed {self.xp_to_next_level} TNL")
        self.cur_xp += gained_xp

        if gained_xp < self.xp_to_next_level:
            # gained xp did not cause a level up
            # just keep collecting unrealized stat xp, and keep track of new XP
            self.xp_to_next_level -= gained_xp
            self.unrealized_stat_xp = self.unrealized_stat_xp.add(gained_stat_xp)
            if const.DEBUG_MODE:
                logger.info(f"NO level up ocurred, still need {self.xp_to_next_level} TNL")
        else:
            # either gained xp caused a level up
            # or, we're at level 100
            level_info = pkmn.universal_utils.level_lookups[self.species_def.growth_rate].get_level_info(self.cur_xp)
            self.cur_level = level_info[0]

            if self.cur_level == 100:
                # level 100. We aren't technically gaining experience anymore, so just override the xp values
                # keep track of stat xp, but have to rely on vitamins to "realize" them
                self.cur_xp = pkmn.universal_utils.level_lookups[self.species_def.growth_rate].get_xp_for_level(100)
                self.xp_to_next_level = 0
                self.unrealized_stat_xp = self.unrealized_stat_xp.add(gained_stat_xp)
                if const.DEBUG_MODE:
                    logger.info(f"At level 100")
            else:
                # gained xp DID cause a level up
                # realize ALL stat XP into new stats, reset unrealized stat XP, and then update level metadata
                self.unrealized_stat_xp = self.unrealized_stat_xp.add(gained_stat_xp)
                self.realized_stat_xp = copy(self.unrealized_stat_xp)
                self.xp_to_next_level = level_info[1]
                if const.DEBUG_MODE:
                    logger.info(f"Now level {self.cur_level}, {self.xp_to_next_level} TNL")
        
        if const.DEBUG_MODE:
            logger.info(f"Realized StatXP {self.realized_stat_xp}")
            logger.info(f"Unrealized StatXP {self.unrealized_stat_xp}")

        if self.xp_to_next_level <= 0:
            self.percent_xp_to_next_level = f"N/A"
        else:
            last_level_xp = pkmn.universal_utils.level_lookups[self.species_def.growth_rate].get_xp_for_level(self.cur_level)
            self.percent_xp_to_next_level = f"{int((self.xp_to_next_level / (self.cur_xp + self.xp_to_next_level - last_level_xp)) * 100)} %"
        self.cur_stats = self.species_def.stats.calc_level_stats(self.cur_level, self.dvs, self.realized_stat_xp, badges, nature, self.held_item)
    
    def __eq__(self, other):
        if not isinstance(other, SoloPokemon):
            return False
        
        if (
            self.species_def.name != other.species_def.name or
            self.cur_level != other.cur_level or
            self.cur_xp != other.cur_xp or
            self.dvs != other.dvs or
            self.realized_stat_xp != other.realized_stat_xp or
            self.unrealized_stat_xp != other.unrealized_stat_xp or
            self.cur_stats != other.cur_stats or
            self.held_item != other.held_item
        ):
            return False
        
        if len(self.move_list) != len(other.move_list):
            return False
        for move_idx in range(len(self.move_list)):
            if self.move_list[move_idx] != other.move_list[move_idx]:
                return False
        
        return True
    
    def get_net_gain_from_stat_xp(self, badges):
        if badges is None:
            badges = pkmn.universal_data_objects.BadgeList()

        temp = self.species_def.stats.calc_level_stats(
            self.cur_level,
            self.dvs,
            self._empty_stat_block,
            badges,
            self.nature,
            self.held_item
        )

        return self.cur_stats.subtract(temp)

    def get_pkmn_obj(self, badges, stage_modifiers=None):
        # allow badge boosting, and also normal stat boosting
        if stage_modifiers is None:
            stage_modifiers = pkmn.universal_data_objects.StageModifiers()
        
        battle_stats = self.species_def.stats.calc_battle_stats(self.cur_level, self.dvs, self.realized_stat_xp, stage_modifiers, badges, self.nature, self.held_item)

        return pkmn.universal_data_objects.EnemyPkmn(
            self.name,
            self.cur_level,
            -1,
            self.move_list,
            battle_stats,
            self.species_def.stats,
            self.dvs,
            stat_xp=self.realized_stat_xp,
            badges=badges,
            is_trainer_mon=True,
            held_item=self.held_item,
            ability=self.ability,
            nature=self.nature
        )

    def get_move_destination(self, move_name, dest):
        # if one were to attempt to learn a move defined by the params
        # return what would the actual destination would be
        
        # if we are forgetting the move, always respect dest
        if move_name is None:
            return dest, True

        # if we already know the move, ignore dest entirely and just don't learn it
        if move_name in self.move_list:
            return None, False
        
        added = False
        for cur_idx in range(len(self.move_list)):
            # if we're learning the move and we have empty slots, always learn the move
            if self.move_list[cur_idx] is None:
                return cur_idx, False
        
        # if we have 4 moves already, and none of those moves are what we're trying to learn
        # Then, we finally care about the destination passed in
        if dest is None:
            return None, True

        if not added and dest is not None:
            return dest, True
