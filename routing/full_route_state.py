
import math
from utils.constants import const
import pkmn.universal_utils
import pkmn.universal_data_objects
import pkmn.gen_factory
from routing.state_objects import Inventory, SoloPokemon


def _defeat_trainer(inventory:Inventory, trainer_obj:pkmn.universal_data_objects.Trainer):
    if trainer_obj is None:
        return inventory
    
    result = inventory._copy()
    result.cur_money += trainer_obj.money

    fight_reward = pkmn.gen_factory.current_gen_info().get_fight_reward(trainer_obj.name)
    if fight_reward is not None:
        # it's ok to fail to add a fight reward to your bag
        try:
            result = result.add_item(pkmn.gen_factory.current_gen_info().item_db().get_item(fight_reward), 1)
        except Exception:
            pass
    return result


def _defeat_pkmn(cur_pkmn:SoloPokemon, enemy_pkmn: pkmn.universal_data_objects.EnemyPkmn, badges:pkmn.universal_data_objects.BadgeList, exp_split:int):
    # enemy_pkmn is an EnemyPkmn type
    gained_xp = math.floor(enemy_pkmn.xp / exp_split)
    gained_stat_xp = pkmn.universal_data_objects.StatBlock(
        math.floor(enemy_pkmn.base_stats.hp / exp_split),
        math.floor(enemy_pkmn.base_stats.attack / exp_split),
        math.floor(enemy_pkmn.base_stats.defense / exp_split),
        math.floor(enemy_pkmn.base_stats.special_attack / exp_split),
        math.floor(enemy_pkmn.base_stats.special_defense / exp_split),
        math.floor(enemy_pkmn.base_stats.speed / exp_split),
        is_stat_xp=True
    )
    return SoloPokemon(
        cur_pkmn.name,
        cur_pkmn.species_def,
        cur_pkmn.dvs,
        badges,
        cur_pkmn._empty_stat_block,
        move_list=cur_pkmn.move_list,
        cur_xp=cur_pkmn.cur_xp,
        realized_stat_xp=cur_pkmn.realized_stat_xp,
        unrealized_stat_xp=cur_pkmn.unrealized_stat_xp,
        gained_xp=gained_xp,
        gained_stat_xp=gained_stat_xp,
        held_item=cur_pkmn.held_item
    )


def _rare_candy(cur_pkmn:SoloPokemon, badges:pkmn.universal_data_objects.BadgeList):
    return SoloPokemon(
        cur_pkmn.name,
        cur_pkmn.species_def,
        cur_pkmn.dvs,
        badges,
        cur_pkmn._empty_stat_block,
        move_list=cur_pkmn.move_list,
        cur_xp=cur_pkmn.cur_xp,
        realized_stat_xp=cur_pkmn.realized_stat_xp,
        unrealized_stat_xp=cur_pkmn.unrealized_stat_xp,
        gained_xp=cur_pkmn.xp_to_next_level,
        held_item=cur_pkmn.held_item
    )


def _learn_move(cur_pkmn:SoloPokemon, move_name, dest, badges):
    # kinda ugly logic below, since move learning has several possible behaviors
    new_movelist = cur_pkmn.move_list

    actual_dest = cur_pkmn.get_move_destination(move_name, dest)[0]
    if actual_dest is not None:
        new_movelist = [x for x in new_movelist]
        new_movelist[actual_dest] = move_name

    return SoloPokemon(
        cur_pkmn.name,
        cur_pkmn.species_def,
        cur_pkmn.dvs,
        badges,
        cur_pkmn._empty_stat_block,
        move_list=new_movelist,
        cur_xp=cur_pkmn.cur_xp,
        realized_stat_xp=cur_pkmn.realized_stat_xp,
        unrealized_stat_xp=cur_pkmn.unrealized_stat_xp,
        held_item=cur_pkmn.held_item
    )


def _take_vitamin(cur_pkmn:SoloPokemon, vit_name, badges, force=False):
    # NOTE: some potentially buggy reporting of how much stat xp is actually possible when nearing the stat XP cap
    # this is due to the fact that we are keeping unrealized stat XP separate,
    # so any stat XP over the hard cap won't be properly ignored until it's realized
    # however, this bug is both minor (won't ever be reported in the actual pkmn stats) and rare (only when nearing stat XP cap, which is uncommon in solo playthroughs) 
    # intentionally ignoring for now
    cur_stat_xp_total = cur_pkmn.realized_stat_xp.add(cur_pkmn.unrealized_stat_xp)

    vit_cap = pkmn.gen_factory.current_gen_info().get_vitamin_cap()
    vit_boost = pkmn.gen_factory.current_gen_info().get_vitamin_amount()

    final_realized_stat_xp = cur_pkmn.unrealized_stat_xp
    for boosted_stat in pkmn.gen_factory.current_gen_info().get_stats_boosted_by_vitamin(vit_name):
        if boosted_stat == const.HP:
            if cur_stat_xp_total.hp >= vit_cap and not force:
                raise ValueError(f"Ineffective Vitamin: {vit_name} (Already above vitamin cap)")
            final_realized_stat_xp = final_realized_stat_xp.add(pkmn.gen_factory.current_gen_info().make_stat_block(vit_boost, 0, 0, 0, 0, 0, is_stat_xp=True))
        elif boosted_stat == const.ATK:
            if cur_stat_xp_total.attack >= vit_cap and not force:
                raise ValueError(f"Ineffective Vitamin: {vit_name} (Already above vitamin cap)")
            final_realized_stat_xp = final_realized_stat_xp.add(pkmn.gen_factory.current_gen_info().make_stat_block(0, vit_boost, 0, 0, 0, 0, is_stat_xp=True))
        elif boosted_stat == const.DEF:
            if cur_stat_xp_total.defense >= vit_cap and not force:
                raise ValueError(f"Ineffective Vitamin: {vit_name} (Already above vitamin cap)")
            final_realized_stat_xp = final_realized_stat_xp.add(pkmn.gen_factory.current_gen_info().make_stat_block(0, 0, vit_boost, 0, 0, 0, is_stat_xp=True))
        elif boosted_stat == const.SPA:
            if cur_stat_xp_total.special_attack >= vit_cap and not force:
                raise ValueError(f"Ineffective Vitamin: {vit_name} (Already above vitamin cap)")
            final_realized_stat_xp = final_realized_stat_xp.add(pkmn.gen_factory.current_gen_info().make_stat_block(0, 0, 0, vit_boost, 0, 0, is_stat_xp=True))
        elif boosted_stat == const.SPD:
            # TODO: how to handle this once we're supporting gen 3?
            # Note: the comparison against special attack is intentional here, since gens 1 and 2 only actually have one stat exp field for field for special
            if cur_stat_xp_total.special_attack >= vit_cap and not force:
                raise ValueError(f"Ineffective Vitamin: {vit_name} (Already above vitamin cap)")
            final_realized_stat_xp = final_realized_stat_xp.add(pkmn.gen_factory.current_gen_info().make_stat_block(0, 0, 0, 0, vit_boost, 0, is_stat_xp=True))
        elif boosted_stat == const.SPE:
            if cur_stat_xp_total.speed >= vit_cap and not force:
                raise ValueError(f"Ineffective Vitamin: {vit_name} (Already above vitamin cap)")
            final_realized_stat_xp = final_realized_stat_xp.add(pkmn.gen_factory.current_gen_info().make_stat_block(0, 0, 0, 0, 0, vit_boost, is_stat_xp=True))
        else:
            raise ValueError(f"Unknown vitamin: {vit_name}")

    return SoloPokemon(
        cur_pkmn.name,
        cur_pkmn.species_def,
        cur_pkmn.dvs,
        badges,
        cur_pkmn._empty_stat_block,
        move_list=cur_pkmn.move_list,
        cur_xp=cur_pkmn.cur_xp,
        realized_stat_xp=cur_pkmn.realized_stat_xp.add(final_realized_stat_xp),
        held_item=cur_pkmn.held_item
    )


def _hold_item(cur_pkmn:SoloPokemon, item_name, badges):
    return SoloPokemon(
        cur_pkmn.name,
        cur_pkmn.species_def,
        cur_pkmn.dvs,
        badges,
        cur_pkmn._empty_stat_block,
        move_list=cur_pkmn.move_list,
        cur_xp=cur_pkmn.cur_xp,
        realized_stat_xp=cur_pkmn.realized_stat_xp,
        unrealized_stat_xp=cur_pkmn.unrealized_stat_xp,
        held_item=item_name
    )


class RouteState:
    # note: paradigm of this is kind of clunky
    # basically we ask each aspect of the current state of the run (represented by an object)
    # to update to reflect the new state represented by the event in question
    # if any update fails, we record the error, and then redo it with "force=True"
    # this allows us to collect errors, while still making sure that the effects happen

    def __init__(self, solo_pkmn:SoloPokemon, badges:pkmn.universal_data_objects.BadgeList, inventory:Inventory):
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
            try:
                consume_item = not pkmn.gen_factory.current_gen_info().item_db().get_item(source).is_key_item
            except:
                consume_item = False
                error_message = f"Could not get valid item for move {move_name} source: {source}"

            if consume_item:
                try:
                    inv = self.inventory.remove_item(pkmn.gen_factory.current_gen_info().item_db().get_item(source), 1, False)
                except Exception as e:
                    error_message = str(e)
                    inv = self.inventory.remove_item(pkmn.gen_factory.current_gen_info().item_db().get_item(source), 1, is_sale=False, force=True)
            else:
                inv = self.inventory

        return RouteState(
            _learn_move(self.solo_pkmn, move_name, dest, self.badges),
            self.badges,
            inv
        ), error_message

    def vitamin(self, vitamin_name):
        error_message = []
        try:
            new_mon = _take_vitamin(self.solo_pkmn, vitamin_name, self.badges)
        except Exception as e:
            error_message.append(str(e))
            new_mon = _take_vitamin(self.solo_pkmn, vitamin_name, self.badges, force=True)

        try:
            inv = self.inventory.remove_item(pkmn.gen_factory.current_gen_info().item_db().get_item(vitamin_name), 1, False)
        except Exception as e:
            error_message.append(str(e))
            inv = self.inventory.remove_item(pkmn.gen_factory.current_gen_info().item_db().get_item(vitamin_name), 1, False, force=True)

        return RouteState(new_mon, self.badges, inv), ', '.join(error_message)

    def rare_candy(self):
        error_message = ""

        try:
            inv = self.inventory.remove_item(pkmn.gen_factory.current_gen_info().item_db().get_item(const.RARE_CANDY), 1, False)
        except Exception as e:
            error_message = str(e)
            inv = self.inventory.remove_item(pkmn.gen_factory.current_gen_info().item_db().get_item(const.RARE_CANDY), 1, False, force=True)

        return RouteState(
            _rare_candy(self.solo_pkmn, self.badges),
            self.badges,
            inv
        ), error_message

    def defeat_pkmn(self, enemy_pkmn:pkmn.universal_data_objects.EnemyPkmn, trainer_name=None, exp_split=1):
        new_badges = self.badges.award_badge(trainer_name)
        return RouteState(
            _defeat_pkmn(self.solo_pkmn, enemy_pkmn, new_badges, exp_split),
            new_badges,
            _defeat_trainer(self.inventory, pkmn.gen_factory.current_gen_info().trainer_db().get_trainer(trainer_name))
        ), ""
    
    def add_item(self, item_name, amount, is_purchase):
        error_message = ""

        try:
            inv = self.inventory.add_item(pkmn.gen_factory.current_gen_info().item_db().get_item(item_name), amount, is_purchase)
        except Exception as e:
            error_message = str(e)
            inv = self.inventory.add_item(pkmn.gen_factory.current_gen_info().item_db().get_item(item_name), amount, is_purchase, force=True)

        return RouteState(self.solo_pkmn, self.badges, inv), error_message

    def remove_item(self, item_name, amount, is_purchase):
        error_message = ""

        try:
            inv = self.inventory.remove_item(pkmn.gen_factory.current_gen_info().item_db().get_item(item_name), amount, is_purchase)
        except Exception as e:
            error_message = str(e)
            inv = self.inventory.remove_item(pkmn.gen_factory.current_gen_info().item_db().get_item(item_name), amount, is_purchase, force=True)

        return RouteState(self.solo_pkmn, self.badges, inv), error_message
    
    def hold_item(self, item_name):
        error_message = ""

        inv = self.inventory
        existing_held = self.solo_pkmn.held_item
        if existing_held:
            inv = inv.add_item(pkmn.gen_factory.current_gen_info().item_db().get_item(existing_held), 1)
        
        try:
            inv = inv.remove_item(pkmn.gen_factory.current_gen_info().item_db().get_item(item_name), 1)
        except Exception as e:
            error_message = str(e)
            inv = inv.remove_item(pkmn.gen_factory.current_gen_info().item_db().get_item(item_name), 1, force=True)
        
        return RouteState(
            _hold_item(self.solo_pkmn, item_name, self.badges),
            self.badges,
            inv
        ), error_message

    def blackout(self):
        inv = self.inventory._copy()
        inv.cur_money = self.inventory.cur_money // 2
        # TODO: validate rounding is correct here...
        return RouteState(
            self.solo_pkmn,
            self.badges,
            inv
        ), ""

