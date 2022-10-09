
from typing import List
from utils.constants import const
from pkmn.gen_1 import pkmn_utils
from pkmn import universal_utils
from pkmn import universal_data_objects
import pkmn

    

class BagItem:
    def __init__(self, base_item, num):
        self.base_item = base_item
        self.num = num
    
    def __eq__(self, other):
        if not isinstance(other,BagItem):
            return False
        return (
            self.base_item.name == other.base_item.name and
            self.num == other.num
        )


class Inventory:
    def __init__(self, cur_money=None, cur_items=None):
        if cur_money is None:
            cur_money = 3000
        self.cur_money = cur_money

        if cur_items is None:
            cur_items = []
        self.cur_items = [BagItem(x.base_item, x.num) for x in cur_items]
        self._item_lookup = dict()
        self._reindex_lookup()
    
    def _reindex_lookup(self):
        self._item_lookup = {x.base_item.name: idx for idx, x in enumerate(self.cur_items)}
    
    def _copy(self):
        return Inventory(self.cur_money, self.cur_items)
    
    def defeat_trainer(self, trainer_obj):
        if trainer_obj is None:
            return self
        
        result = self._copy()
        result.cur_money += trainer_obj.money

        fight_reward = const.FIGHT_REWARDS.get(trainer_obj.name)
        if fight_reward is not None:
            # it's ok to fail to add a fight reward to your bag
            try:
                result = result.add_item(pkmn.current_gen_info().item_db().get_item(fight_reward), 1)
            except Exception:
                pass
        return result
    
    def add_item(self, base_item:universal_data_objects.BaseItem, num, is_purchase=False, force=False):
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
        elif len(result.cur_items) >= const.BAG_LIMIT and not force:
            raise ValueError(f"Cannot add more than {const.BAG_LIMIT} items to bag")
        elif len(result.cur_items) < const.BAG_LIMIT:
            # looks kind of weird, but when we're forcing, we don't want to error
            # but we still don't have room in the bag. So we just have to ignore that item...
            result._item_lookup[base_item.name] = len(result.cur_items)
            result.cur_items.append(BagItem(base_item, num))
        
        return result
    
    def remove_item(self, base_item:universal_data_objects.BaseItem, num, is_sale=False, force=False):
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
            species_def:universal_data_objects.PokemonSpecies,
            dvs:universal_data_objects.StatBlock,
            badges:universal_data_objects.BadgeList,
            move_list:list=None,
            cur_xp:int=0,
            realized_stat_xp:universal_data_objects.StatBlock=None,
            unrealized_stat_xp:universal_data_objects.StatBlock=None,
            gained_xp:int=0,
            gained_stat_xp:universal_data_objects.StatBlock=None
    ):
        self.name = name
        self.species_def = species_def
        self.dvs = dvs
        self.badges = badges

        if move_list is None:
            self.move_list = [x for x in species_def.initial_moves]
            while len(self.move_list) < 4:
                self.move_list.append("")
        else:
            self.move_list = move_list

        if cur_xp == 0:
            # if no initial XP is defined, assume creating a new level 5 pkmn
            self.cur_xp = universal_utils.level_lookups[self.species_def.growth_rate].get_xp_for_level(5)
        else:
            self.cur_xp = cur_xp

        if badges is None:
            badges = universal_data_objects.BadgeList()

        level_info = universal_utils.level_lookups[self.species_def.growth_rate].get_level_info(self.cur_xp)
        self.cur_level = level_info[0]
        self.xp_to_next_level = level_info[1]

        if realized_stat_xp is None:
            realized_stat_xp = pkmn.current_gen_info().make_stat_block(0, 0, 0, 0, 0, 0, is_stat_xp=True)
        self.realized_stat_xp = realized_stat_xp

        if unrealized_stat_xp is None:
            unrealized_stat_xp = pkmn.current_gen_info().make_stat_block(0, 0, 0, 0, 0, 0, is_stat_xp=True)
        self.unrealized_stat_xp = unrealized_stat_xp

        if gained_stat_xp is None:
            gained_stat_xp = pkmn.current_gen_info().make_stat_block(0, 0, 0, 0, 0, 0, is_stat_xp=True)
        
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
            self.unrealized_stat_xp = pkmn.current_gen_info().make_stat_block(0, 0, 0, 0, 0, 0, is_stat_xp=True)

            level_info = universal_utils.level_lookups[self.species_def.growth_rate].get_level_info(self.cur_xp)
            self.cur_level = level_info[0]
            self.xp_to_next_level = level_info[1]
            if const.DEBUG_MODE:
                print(f"Now level {self.cur_level}, {self.xp_to_next_level} TNL")
        
        if const.DEBUG_MODE:
            print(f"Realized StatXP {self.realized_stat_xp}")
            print(f"Unrealized StatXP {self.unrealized_stat_xp}")

        last_level_xp = universal_utils.level_lookups[self.species_def.growth_rate].get_xp_for_level(self.cur_level)
        self.percent_xp_to_next_level = f"{int((self.xp_to_next_level / (self.cur_xp + self.xp_to_next_level - last_level_xp)) * 100)} %"
        self.cur_stats = self.species_def.stats.calc_level_stats(self.cur_level, self.dvs, self.realized_stat_xp, badges)
    
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
            self.cur_stats != other.cur_stats
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
            badges = universal_data_objects.BadgeList()

        temp = self.species_def.stats.calc_level_stats(
            self.cur_level,
            self.dvs,
            pkmn.current_gen_info().make_stat_block(0, 0, 0, 0, 0, 0, is_stat_xp=True),
            badges
        )

        return self.cur_stats.subtract(temp)

    def get_pkmn_obj(self, badges, stage_modifiers=None):
        # allow badge boosting, and also normal stat boosting
        if stage_modifiers is None:
            stage_modifiers = universal_data_objects.StageModifiers()
        
        battle_stats = self.species_def.stats.calc_battle_stats(self.cur_level, self.dvs, self.realized_stat_xp, stage_modifiers, badges)

        return universal_data_objects.EnemyPkmn(
            self.name,
            self.cur_level,
            -1,
            self.move_list,
            battle_stats,
            self.species_def.stats,
            self.dvs,
            stat_xp=self.realized_stat_xp,
            badges=badges
        )
    
    def defeat_pkmn(self, enemy_pkmn: universal_data_objects.EnemyPkmn, badges:universal_data_objects.BadgeList):
        # enemy_pkmn is an EnemyPkmn type
        return SoloPokemon(
            self.name,
            self.species_def,
            self.dvs,
            badges,
            move_list=self.move_list,
            cur_xp=self.cur_xp,
            realized_stat_xp=self.realized_stat_xp,
            unrealized_stat_xp=self.unrealized_stat_xp,
            gained_xp=enemy_pkmn.xp,
            gained_stat_xp=enemy_pkmn.base_stats
        )
    
    def rare_candy(self, badges:universal_data_objects.BadgeList):
        return SoloPokemon(
            self.name,
            self.species_def,
            self.dvs,
            badges,
            move_list=self.move_list,
            cur_xp=self.cur_xp,
            realized_stat_xp=self.realized_stat_xp,
            unrealized_stat_xp=self.unrealized_stat_xp,
            gained_xp=self.xp_to_next_level,
        )
    
    def get_move_destination(self, move_name, dest):
        # if one were to attempt to learn a move defined by the params
        # return what would the actual destination would be

        # if we already know the move, ignore dest entirely and just don't learn it
        if move_name in self.move_list:
            return None, False
        
        added = False
        for cur_idx in range(len(self.move_list)):
            # if we're learning the move and we have empty slots, always learn the move
            if self.move_list[cur_idx] == "":
                return cur_idx, False
        
        # if we have 4 moves already, and none of those moves are what we're trying to learn
        # Then, we finally care about the destination passed in
        if dest is None:
            return None, True

        if not added and dest is not None:
            return dest, True

    def learn_move(self, move_name, dest, badges):
        # kinda ugly logic below, since move learning has several possible behaviors
        new_movelist = self.move_list

        actual_dest = self.get_move_destination(move_name, dest)[0]
        if actual_dest is not None:
            new_movelist = [x for x in new_movelist]
            new_movelist[actual_dest] = move_name

        return SoloPokemon(
            self.name,
            self.species_def,
            self.dvs,
            badges,
            move_list=new_movelist,
            cur_xp=self.cur_xp,
            realized_stat_xp=self.realized_stat_xp,
            unrealized_stat_xp=self.unrealized_stat_xp,
        )
    
    def take_vitamin(self, vit_name, badges, force=False):
        # NOTE: some potentially buggy reporting of how much stat xp is actually possible when nearing the stat XP cap
        # this is due to the fact that we are keeping unrealized stat XP separate,
        # so any stat XP over the hard cap won't be properly ignored until it's realized
        # however, this bug is both minor (won't ever be reported in the actual pkmn stats) and rare (only when nearing stat XP cap, which is uncommon in solo playthroughs) 
        # intentionally ignoring for now
        cur_stat_xp_total = self.realized_stat_xp.add(self.unrealized_stat_xp)

        if vit_name == const.HP_UP:
            if cur_stat_xp_total.hp >= pkmn_utils.VIT_CAP and not force:
                raise ValueError(f"Ineffective Vitamin: {vit_name} (Already above vitamin cap)")
            new_unrealized_stat_xp = self.unrealized_stat_xp.add(pkmn.current_gen_info().make_stat_block(pkmn_utils.VIT_AMT, 0, 0, 0, 0, 0, is_stat_xp=True))
        elif vit_name == const.PROTEIN:
            if cur_stat_xp_total.attack >= pkmn_utils.VIT_CAP and not force:
                raise ValueError(f"Ineffective Vitamin: {vit_name} (Already above vitamin cap)")
            new_unrealized_stat_xp = self.unrealized_stat_xp.add(pkmn.current_gen_info().make_stat_block(0, pkmn_utils.VIT_AMT, 0, 0, 0, 0, is_stat_xp=True))
        elif vit_name == const.IRON:
            if cur_stat_xp_total.defense >= pkmn_utils.VIT_CAP and not force:
                raise ValueError(f"Ineffective Vitamin: {vit_name} (Already above vitamin cap)")
            new_unrealized_stat_xp = self.unrealized_stat_xp.add(pkmn.current_gen_info().make_stat_block(0, 0, pkmn_utils.VIT_AMT, 0, 0, 0, is_stat_xp=True))
        elif vit_name == const.CALCIUM:
            if cur_stat_xp_total.special >= pkmn_utils.VIT_CAP and not force:
                raise ValueError(f"Ineffective Vitamin: {vit_name} (Already above vitamin cap)")
            new_unrealized_stat_xp = self.unrealized_stat_xp.add(pkmn.current_gen_info().make_stat_block(0, 0, 0, 0, pkmn_utils.VIT_AMT, pkmn_utils.VIT_AMT, 0, is_stat_xp=True))
        elif vit_name == const.CARBOS:
            if cur_stat_xp_total.speed >= pkmn_utils.VIT_CAP and not force:
                raise ValueError(f"Ineffective Vitamin: {vit_name} (Already above vitamin cap)")
            new_unrealized_stat_xp = self.unrealized_stat_xp.add(pkmn.current_gen_info().make_stat_block(0, 0, 0, 0, 0, pkmn_utils.VIT_AMT, is_stat_xp=True))
        else:
            raise ValueError(f"Unknown vitamin: {vit_name}")

        return SoloPokemon(
            self.name,
            self.species_def,
            self.dvs,
            badges,
            move_list=self.move_list,
            cur_xp=self.cur_xp,
            realized_stat_xp=self.realized_stat_xp.add(new_unrealized_stat_xp),
        )


class RouteState:
    # note: paradigm of this is kind of clunky
    # basically we ask each aspect of the current state of the run (represented by an object)
    # to update to reflect the new state represented by the event in question
    # if any update fails, we record the error, and then redo it with "force=True"
    # this allows us to collect errors, while still making sure that the effects happen

    def __init__(self, solo_pkmn:SoloPokemon, badges:universal_data_objects.BadgeList, inventory:Inventory):
        self.solo_pkmn = solo_pkmn
        self.badges = badges
        self.inventory = inventory
    
    def __eq__(self, other):
        if not isinstance(other, RouteState):
            return False
        
        return (
            self.solo_pkmn == other.solo_pkmn and
            self.badges == other.badges and
            self.inventory == other.inventory
        )
    
    def learn_move(self, move_name, dest, source):
        error_message = ""
        if source == const.MOVE_SOURCE_LEVELUP:
            inv = self.inventory
        else:
            consume_item = True
            try:
                consume_item = not pkmn.current_gen_info().item_db().get_item(source).is_key_item
            except:
                pass

            if consume_item:
                try:
                    inv = self.inventory.remove_item(pkmn.current_gen_info().item_db().get_item(source), 1, False)
                except Exception as e:
                    error_message = str(e)
                    inv = self.inventory.remove_item(pkmn.current_gen_info().item_db().get_item(source), 1, is_sale=False, force=True)
            else:
                inv = self.inventory

        return RouteState(
            self.solo_pkmn.learn_move(move_name, dest, self.badges),
            self.badges,
            inv
        ), error_message

    def vitamin(self, vitamin_name):
        error_message = []
        try:
            new_mon = self.solo_pkmn.take_vitamin(vitamin_name, self.badges)
        except Exception as e:
            error_message.append(str(e))
            new_mon = self.solo_pkmn.take_vitamin(vitamin_name, self.badges, force=True)

        try:
            inv = self.inventory.remove_item(pkmn.current_gen_info().item_db().get_item(vitamin_name), 1, False)
        except Exception as e:
            error_message.append(str(e))
            inv = self.inventory.remove_item(pkmn.current_gen_info().item_db().get_item(vitamin_name), 1, False, force=True)

        return RouteState(new_mon, self.badges, inv), ', '.join(error_message)

    def rare_candy(self):
        error_message = ""

        try:
            inv = self.inventory.remove_item(pkmn.current_gen_info().item_db().get_item(const.RARE_CANDY), 1, False)
        except Exception as e:
            error_message = str(e)
            inv = self.inventory.remove_item(pkmn.current_gen_info().item_db().get_item(const.RARE_CANDY), 1, False, force=True)

        return RouteState(
            self.solo_pkmn.rare_candy(self.badges),
            self.badges,
            inv
        ), error_message

    def defeat_pkmn(self, enemy_pkmn:universal_data_objects.EnemyPkmn, trainer_name=None):
        new_badges = self.badges.award_badge(trainer_name)
        return RouteState(
            self.solo_pkmn.defeat_pkmn(enemy_pkmn, new_badges),
            new_badges,
            self.inventory.defeat_trainer(pkmn.current_gen_info().trainer_db().get_trainer(trainer_name))
        ), ""
    
    def add_item(self, item_name, amount, is_purchase):
        error_message = ""

        try:
            inv = self.inventory.add_item(pkmn.current_gen_info().item_db().get_item(item_name), amount, is_purchase)
        except Exception as e:
            error_message = str(e)
            inv = self.inventory.add_item(pkmn.current_gen_info().item_db().get_item(item_name), amount, is_purchase, force=True)

        return RouteState(self.solo_pkmn, self.badges, inv), error_message

    def remove_item(self, item_name, amount, is_purchase):
        error_message = ""

        try:
            inv = self.inventory.remove_item(pkmn.current_gen_info().item_db().get_item(item_name), amount, is_purchase)
        except Exception as e:
            error_message = str(e)
            inv = self.inventory.remove_item(pkmn.current_gen_info().item_db().get_item(item_name), amount, is_purchase, force=True)

        return RouteState(self.solo_pkmn, self.badges, inv), error_message
