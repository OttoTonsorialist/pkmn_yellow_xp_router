
from cgitb import reset
from utils.constants import const
from pkmn import data_objects
from pkmn import route_state_objects
from pkmn import pkmn_db

event_id_counter = 0

class InventoryEventDefinition:
    def __init__(self, item_name, item_amount, is_acquire, with_money):
        self.item_name = item_name
        self.item_amount = item_amount
        self.is_acquire = is_acquire
        self.with_money = with_money
    
    def serialize(self):
        return [self.item_name, self.item_amount, self.is_acquire, self.with_money]
    
    @staticmethod
    def deserialize(raw_val):
        if not raw_val:
            return None
        return InventoryEventDefinition(raw_val[0], raw_val[1], raw_val[2], raw_val[3])
    
    def __str__(self):
        if self.is_acquire and self.with_money:
            action = "Purchase"
        elif self.is_acquire and not self.with_money:
            action = "Find"
        elif self.with_money:
            action = "Sell"
        else:
            action = "Use/Drop"
        
        return f"{action} {self.item_name} x{self.item_amount}"


class WildPkmnEventDefinition:
    def __init__(self, name, level):
        self.name = name
        self.level = level

    def serialize(self):
        return [self.name, self.level]
    
    @staticmethod
    def deserialize(raw_val):
        if not raw_val:
            return None
        return WildPkmnEventDefinition(raw_val[0], raw_val[1])
    
    def __str__(self):
        return f"{self.name}, LV: {self.level}"


class EventDefinition:
    def __init__(self, is_rare_candy=False, vitamin=None, trainer_name=None, wild_pkmn_info=None, item_event_def=None):
        self.is_rare_candy = is_rare_candy
        self.vitamin = vitamin
        self.trainer_name = trainer_name
        self._trainer_obj = None
        self.wild_pkmn_info = wild_pkmn_info
        self._wild_pkmn = None
        self.item_event_def = item_event_def

    def get_trainer_obj(self):
        if self._trainer_obj is None and self.trainer_name is not None:
            self._trainer_obj = pkmn_db.trainer_db.data.get(self.trainer_name)
        return self._trainer_obj
    
    def get_wild_pkmn(self):
        if self._wild_pkmn is None and self.wild_pkmn_info is not None:
            self._wild_pkmn = pkmn_db.pkmn_db.create_wild_pkmn(self.wild_pkmn_info.name, self.wild_pkmn_info.level)
        return self._wild_pkmn
    
    def get_pokemon_list(self):
        wild_pkmn = self.get_wild_pkmn()
        if wild_pkmn is not None:
            return [wild_pkmn]
        
        trainer = self.get_trainer_obj()
        if trainer is not None:
            return trainer.pkmn
        
        return []
    
    def get_label(self):
        if self.is_rare_candy:
            return const.RARE_CANDY
        elif self.vitamin is not None:
            return f"Vitamin: {self.vitamin}"
        elif self.wild_pkmn_info is not None:
            return f"Wild Pkmn: {self.wild_pkmn_info}"
        elif self.trainer_name is not None:
            trainer = self.get_trainer_obj()
            return f"Trainer: {trainer.name} ({trainer.location})"
        elif self.item_event_def is not None:
            return str(self.item_event_def)
        
        return "Invalid Event!"
    
    def __str__(self):
        return self.get_label()

    
    def serialize(self):
        if self.is_rare_candy:
            return {const.TASK_RARE_CANDY: self.is_rare_candy}
        elif self.vitamin is not None:
            return {const.TASK_VITAMIN: self.vitamin}
        elif self.trainer_name is not None:
            return {const.TASK_TRAINER_BATTLE: self.trainer_name}
        elif self.wild_pkmn_info is not None:
            return {const.TASK_FIGHT_WILD_PKMN: self.wild_pkmn_info.serialize()}
        else:
            return {const.INVENTORY_EVENT_DEFINITON: self.item_event_def.serialize()}
    
    @staticmethod
    def deserialize(raw_val):
        result = EventDefinition(
            is_rare_candy=raw_val.get(const.TASK_RARE_CANDY),
            vitamin=raw_val.get(const.TASK_VITAMIN),
            trainer_name=raw_val.get(const.TASK_TRAINER_BATTLE),
            wild_pkmn_info=WildPkmnEventDefinition.deserialize(raw_val.get(const.TASK_FIGHT_WILD_PKMN)),
            item_event_def=InventoryEventDefinition.deserialize(raw_val.get(const.INVENTORY_EVENT_DEFINITON)),
        )
        if result.wild_pkmn_info is not None:
            result.trainer_name = None
        return result


class EventItem:
    """
    This class effectively functions as the conversion layer between EventDefinitions and the RouteState object.
    """
    def __init__(self, cur_state, event_def:EventDefinition, to_defeat_idx=None):

        self.to_defeat_idx = to_defeat_idx
        self.event_def = event_def

        self.post_event_state = None
        self.error_message = ""
        self.apply(cur_state)
    
    def apply(self, cur_state: route_state_objects.RouteState):
        if self.to_defeat_idx is not None:
            enemy_team = self.event_def.get_pokemon_list()
            if len(enemy_team) <= self.to_defeat_idx:
                self.post_event_state = cur_state
                self.error_message = f"No Num {self.to_defeat_idx} pkmn from team: {self.event_def}"
            else:
                # you only "defeat" a trainer after defeating their final pokemon
                trainer_name = self.event_def.trainer_name if self.to_defeat_idx == len(enemy_team) - 1 else None
                self.post_event_state, self.error_message = cur_state.defeat_pkmn(enemy_team[self.to_defeat_idx], trainer_name=trainer_name)
        elif self.event_def.is_rare_candy:
            self.post_event_state, self.error_message = cur_state.rare_candy()
        elif self.event_def.vitamin is not None:
            self.post_event_state, self.error_message = cur_state.vitamin(self.event_def.vitamin)
        elif self.event_def.item_event_def is not None:
            if self.event_def.item_event_def.is_acquire:
                self.post_event_state, self.error_message = cur_state.add_item(
                    self.event_def.item_event_def.item_name,
                    self.event_def.item_event_def.item_amount,
                    self.event_def.item_event_def.with_money,
                )
            else:
                self.post_event_state, self.error_message = cur_state.remove_item(
                    self.event_def.item_event_def.item_name,
                    self.event_def.item_event_def.item_amount,
                    self.event_def.item_event_def.with_money,
                )


class EventGroup:
    def __init__(self, cur_state, event_definition:EventDefinition):
        global event_id_counter
        self.group_id = event_id_counter
        event_id_counter += 1

        self.name = None
        self.final_state = None
        self.event_items = []
        self.init_state = cur_state
        self.event_definition = event_definition
        self.pkmn_after_levelups = []
        self.error_messages = []

        self.apply(cur_state)
    
    def apply(self, cur_state):
        self.name = self.event_definition.get_label()
        self.init_state = cur_state
        self.pkmn_after_levelups = []
        self.event_items = []

        if self.event_definition.trainer_name is not None:
            trainer_obj = self.event_definition.get_trainer_obj()
            pkmn_counter = {}
            for pkmn_idx, trainer_pkmn in enumerate(trainer_obj.pkmn):
                self.event_items.append(EventItem(cur_state, self.event_definition, to_defeat_idx=pkmn_idx))
                pkmn_counter[trainer_pkmn.name] = pkmn_counter.get(trainer_pkmn.name, 0) + 1
                
                next_state = self.event_items[-1].post_event_state
                if next_state.solo_pkmn.cur_level != cur_state.solo_pkmn.cur_level:
                    if pkmn_idx + 1 < len(trainer_obj.pkmn):
                        next_pkmn_name = trainer_obj.pkmn[pkmn_idx + 1].name
                        next_pkmn_count = pkmn_counter.get(next_pkmn_name, 0) + 1
                        self.pkmn_after_levelups.append(f"#{next_pkmn_count} {next_pkmn_name}")
                    else:
                        self.pkmn_after_levelups.append("after_final_pkmn")
                cur_state = next_state
        
        elif self.event_definition.wild_pkmn_info is not None:
            self.event_items.append(EventItem(cur_state, self.event_definition, to_defeat_idx=0))
        else:
            self.event_items.append(EventItem(cur_state, self.event_definition))
            
        if len(self.event_items) == 0:
            raise ValueError(f"Something went wrong generating event group: {self.event_definition}")
        
        self.error_messages = [x.error_message for x in self.event_items if x.error_message]
        if self.error_messages:
            self.name = ", ".join(self.error_messages)
        self.final_state = self.event_items[-1].post_event_state
    
    def get_pkmn_after_levelups(self):
        return ",".join(self.pkmn_after_levelups)

    def pkmn_level(self):
        return self.final_state.solo_pkmn.cur_level
    
    def xp_to_next_level(self):
        return self.final_state.solo_pkmn.xp_to_next_level

    def percent_xp_to_next_level(self):
        return self.final_state.solo_pkmn.percent_xp_to_next_level

    def xp_gain(self):
        return self.final_state.solo_pkmn.cur_xp - self.init_state.solo_pkmn.cur_xp

    def total_xp(self):
        return self.final_state.solo_pkmn.cur_xp

    def to_dict(self):
        return self.event_definition.serialize()
    
    def has_errors(self):
        return len(self.error_messages) != 0
    
    def is_major_fight(self):
        return self.event_definition.trainer_name in const.MAJOR_FIGHTS
    
    def get_tag(self):
        if self.has_errors():
            return const.EVENT_TAG_ERRORS

        if self.is_major_fight():
            return const.EVENT_TAG_IMPORTANT
        
        return None