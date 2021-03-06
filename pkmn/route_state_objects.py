
from pkmn import data_objects
from utils.constants import const
from pkmn import pkmn_utils
from pkmn import pkmn_db

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
        else:
            # no need to hold on to a copy wastefully if no badge was awarded
            return self
        
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
    

class BagItem:
    def __init__(self, base_item, num):
        self.base_item = base_item
        self.num = num


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
                result = result.add_item(pkmn_db.item_db.data[fight_reward], 1)
            except Exception:
                pass
        return result
    
    def add_item(self, base_item:data_objects.BaseItem, num, is_purchase=False):
        result = self._copy()
        if is_purchase:
            total_cost = num * base_item.purchase_price
            if total_cost > result.cur_money:
                raise ValueError(f"Cannot purchase {num} {base_item.name} for {total_cost} with only {result.cur_money} money")
            result.cur_money -= total_cost

        if base_item.name in result._item_lookup:
            if base_item.is_key_item:
                raise ValueError(f"Cannot have multiple of the same key item: {base_item.name}")

            result.cur_items[result._item_lookup[base_item.name]].num += num
        elif len(result.cur_items) >= const.BAG_LIMIT:
            raise ValueError(f"Cannot add more than {const.BAG_LIMIT} items to bag")
        else:
            result._item_lookup[base_item.name] = len(result.cur_items)
            result.cur_items.append(BagItem(base_item, num))
        
        return result
    
    def remove_item(self, base_item:data_objects.BaseItem, num, is_sale=False):
        result = self._copy()
        if base_item.name not in result._item_lookup:
            raise ValueError(f"Cannot sell/use item that you do not have: {base_item.name}")
        if base_item.is_key_item and is_sale:
            raise ValueError(f"Cannot sell key item: {base_item.name}")
        
        bag_item = result.cur_items[result._item_lookup[base_item.name]]
        if bag_item.num < num:
            raise ValueError(f"Cannot sell/use {num} {base_item.name} when you only have {bag_item.num}")
        
        bag_item.num -= num
        if bag_item.num == 0:
            del result.cur_items[result._item_lookup[base_item.name]]
            result._reindex_lookup()
        
        if is_sale:
            result.cur_money += (base_item.sell_price * num)
        
        return result

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
            badges = BadgeList()
        
        # assume going with perfect DVs if undefined
        if dvs is None:
            self.dvs = data_objects.StatBlock(15, 15, 15, 15, 15)
        else:
            self.dvs = dvs

        level_info = pkmn_utils.level_lookups[self.species_def.growth_rate].get_level_info(self.cur_xp)
        self.cur_level = level_info[0]
        self.xp_to_next_level = level_info[1]

        if realized_stat_xp is None:
            realized_stat_xp = data_objects.StatBlock(0, 0, 0, 0, 0, is_stat_xp=True)
        self.realized_stat_xp = realized_stat_xp

        if unrealized_stat_xp is None:
            unrealized_stat_xp = data_objects.StatBlock(0, 0, 0, 0, 0, is_stat_xp=True)
        self.unrealized_stat_xp = unrealized_stat_xp

        if gained_stat_xp is None:
            gained_stat_xp = data_objects.StatBlock(0, 0, 0, 0, 0, is_stat_xp=True)
        
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
            self.unrealized_stat_xp = data_objects.StatBlock(0, 0, 0, 0, 0, is_stat_xp=True)

            level_info = pkmn_utils.level_lookups[self.species_def.growth_rate].get_level_info(self.cur_xp)
            self.cur_level = level_info[0]
            self.xp_to_next_level = level_info[1]
            if const.DEBUG_MODE:
                print(f"Now level {self.cur_level}, {self.xp_to_next_level} TNL")
        
        if const.DEBUG_MODE:
            print(f"Realized StatXP {self.realized_stat_xp}")
            print(f"Unrealized StatXP {self.unrealized_stat_xp}")

        last_level_xp = pkmn_utils.level_lookups[self.species_def.growth_rate].get_xp_for_level(self.cur_level)
        self.percent_xp_to_next_level = f"{int((self.xp_to_next_level / (self.cur_xp + self.xp_to_next_level - last_level_xp)) * 100)} %"
        self.cur_stats = self.species_def.stats.calc_level_stats(self.cur_level, self.dvs, self.realized_stat_xp, badges)
    
    def get_renderable_pkmn(self):
        # pkmn viewer only knows how to show off the EnemyPkmn type
        # So create a view of this pokemon in that type for rendering
        # we're going to cheat a lot here, whatever
        return data_objects.EnemyPkmn(
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
    
    def defeat_pkmn(self, enemy_pkmn: data_objects.EnemyPkmn, badges):
        # enemy_pkmn is an EnemyPkmn type
        return SoloPokemon(
            self.name,
            self.species_def,
            cur_xp=self.cur_xp,
            dvs=self.dvs,
            realized_stat_xp=self.realized_stat_xp,
            unrealized_stat_xp=self.unrealized_stat_xp,
            badges=badges,
            gained_xp=enemy_pkmn.xp,
            gained_stat_xp=enemy_pkmn.base_stat_block
        )
    
    def rare_candy(self, badges):
        return SoloPokemon(
            self.name,
            self.species_def,
            cur_xp=self.cur_xp,
            dvs=self.dvs,
            realized_stat_xp=self.realized_stat_xp,
            unrealized_stat_xp=self.unrealized_stat_xp,
            badges=badges,
            gained_xp=self.xp_to_next_level,
        )
    
    def take_vitamin(self, vit_name, badges):
        # NOTE: some potentially buggy reporting of how much stat xp is actually possible when nearing the stat XP cap
        # this is due to the fact that we are keeping unrealized stat XP separate,
        # so any stat XP over the hard cap won't be properly ignored until it's realized
        # however, this bug is both minor (won't ever be reported in the actual pkmn stats) and rare (only when nearing stat XP cap, which is uncommon in solo playthroughs) 
        # intentionally ignoring for now
        cur_stat_xp_total = self.realized_stat_xp.add(self.unrealized_stat_xp)

        if vit_name == const.HP_UP:
            if cur_stat_xp_total.hp >= pkmn_utils.VIT_CAP:
                raise ValueError(f"Ineffective Vitamin: {self.vitamin} (Already above vitamin cap)")
            new_unrealized_stat_xp = self.unrealized_stat_xp.add(data_objects.StatBlock(pkmn_utils.VIT_AMT, 0, 0, 0, 0, is_stat_xp=True))
        elif vit_name == const.PROTEIN:
            if cur_stat_xp_total.attack >= pkmn_utils.VIT_CAP:
                raise ValueError(f"Ineffective Vitamin: {self.vitamin} (Already above vitamin cap)")
            new_unrealized_stat_xp = self.unrealized_stat_xp.add(data_objects.StatBlock(0, pkmn_utils.VIT_AMT, 0, 0, 0, is_stat_xp=True))
        elif vit_name == const.IRON:
            if cur_stat_xp_total.defense >= pkmn_utils.VIT_CAP:
                raise ValueError(f"Ineffective Vitamin: {self.vitamin} (Already above vitamin cap)")
            new_unrealized_stat_xp = self.unrealized_stat_xp.add(data_objects.StatBlock(0, 0, pkmn_utils.VIT_AMT, 0, 0, is_stat_xp=True))
        elif vit_name == const.CARBOS:
            if cur_stat_xp_total.speed >= pkmn_utils.VIT_CAP:
                raise ValueError(f"Ineffective Vitamin: {self.vitamin} (Already above vitamin cap)")
            new_unrealized_stat_xp = self.unrealized_stat_xp.add(data_objects.StatBlock(0, 0, 0, pkmn_utils.VIT_AMT, 0, is_stat_xp=True))
        elif vit_name == const.CALCIUM:
            if cur_stat_xp_total.special >= pkmn_utils.VIT_CAP:
                raise ValueError(f"Ineffective Vitamin: {self.vitamin} (Already above vitamin cap)")
            new_unrealized_stat_xp = self.unrealized_stat_xp.add(data_objects.StatBlock(0, 0, 0, 0, pkmn_utils.VIT_AMT, is_stat_xp=True))
        else:
            raise ValueError(f"Unknown vitamin: {vit_name}")

        return SoloPokemon(
            self.name,
            self.species_def,
            self.cur_xp,
            dvs=self.dvs,
            realized_stat_xp=self.realized_stat_xp.add(new_unrealized_stat_xp),
            badges=badges,
        )


class RouteState:
    def __init__(self, solo_pkmn:SoloPokemon, badges:BadgeList, inventory:Inventory):
        self.solo_pkmn = solo_pkmn
        self.badges = badges
        self.inventory = inventory
    
    def vitamin(self, vitamin_name):
        try:
            return RouteState(
                self.solo_pkmn.take_vitamin(vitamin_name, self.badges),
                self.badges,
                self.inventory.remove_item(pkmn_db.item_db.data[vitamin_name], 1, False)
            ), ""
        except Exception as e:
            return self, str(e)

    def rare_candy(self):
        try:
            return RouteState(
                self.solo_pkmn.rare_candy(self.badges),
                self.badges,
                self.inventory.remove_item(pkmn_db.item_db.data[const.RARE_CANDY], 1, False)
            ), ""
        except Exception as e:
            return self, str(e)

    def defeat_pkmn(self, enemy_pkmn, trainer_name=None):
        try:
            new_badges = self.badges.award_badge(trainer_name)
            return RouteState(
                self.solo_pkmn.defeat_pkmn(enemy_pkmn, new_badges),
                new_badges,
                self.inventory.defeat_trainer(pkmn_db.trainer_db.data.get(trainer_name))
            ), ""
        except Exception as e:
            return self, str(e)
    
    def add_item(self, item_name, amount, is_purchase):
        try:
            return RouteState(
                self.solo_pkmn,
                self.badges,
                self.inventory.add_item(pkmn_db.item_db.data[item_name], amount, is_purchase)
            ), ""
        except Exception as e:
            return self, str(e)

    def remove_item(self, item_name, amount, is_purchase):
        try:
            return RouteState(
                self.solo_pkmn,
                self.badges,
                self.inventory.remove_item(pkmn_db.item_db.data[item_name], amount, is_purchase)
            ), ""
        except Exception as e:
            return self, str(e)
