
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

class LearnMoveEventDefinition:
    def __init__(self, move_to_learn, destination, source, level=const.LEVEL_ANY):
        self.move_to_learn = move_to_learn
        self.destination = destination
        self.source = source
        self.level = level

    def serialize(self):
        return [self.move_to_learn, self.destination, self.source, self.level]
    
    @staticmethod
    def deserialize(raw_val):
        if not raw_val:
            return None
        return LearnMoveEventDefinition(raw_val[0], raw_val[1], raw_val[2], raw_val[3])
    
    def __str__(self):
        if self.destination is None:
            return f"Ignoring {self.move_to_learn}, from {self.source}"
        return f"Learning move {self.move_to_learn} in slot #: {self.destination + 1}, from {self.source}"


class EventDefinition:
    def __init__(self, original_folder_name=None, is_rare_candy=False, vitamin=None, trainer_name=None, wild_pkmn_info=None, item_event_def=None, learn_move=None):
        # ugly hack, but basically we heavily flatten the event structure when serializing
        # so when we deserialize, each event definition is "where" we know which folder it belongs to
        # store it on this object, for reference when deserializing
        # IT SHOULD NEVER BE USED AFTER FULL DESERIALIZATION, AND CAN BE IGNORED ENTIRELY DURING NORMAL PROCESSING
        self.original_folder_name = original_folder_name

        # the actual data associated with the EventDefinition
        self.is_rare_candy = is_rare_candy
        self.vitamin = vitamin
        self.trainer_name = trainer_name
        self._trainer_obj = None
        self.wild_pkmn_info = wild_pkmn_info
        self._wild_pkmn = None
        self.item_event_def = item_event_def
        self.learn_move = learn_move

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
        elif self.learn_move is not None:
            return str(self.learn_move)
        
        return "Invalid Event!"
    
    def __str__(self):
        return self.get_label()

    
    def serialize(self, folder_name):
        result = {const.EVENT_FOLDER_NAME: folder_name}
        if self.is_rare_candy:
            return result.update({const.TASK_RARE_CANDY: self.is_rare_candy})
        elif self.vitamin is not None:
            return result.update({const.TASK_VITAMIN: self.vitamin})
        elif self.trainer_name is not None:
            return result.update({const.TASK_TRAINER_BATTLE: self.trainer_name})
        elif self.wild_pkmn_info is not None:
            return result.update({const.TASK_FIGHT_WILD_PKMN: self.wild_pkmn_info.serialize()})
        else:
            return result.update({const.INVENTORY_EVENT_DEFINITON: self.item_event_definition.serialize()})
    
    @staticmethod
    def deserialize(raw_val):
        result = EventDefinition(
            original_folder_name=raw_val.get(const.EVENT_FOLDER_NAME, const.DEFAULT_FOLDER_NAME),
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
    def __init__(self, event_definition:EventDefinition, to_defeat_idx=None, cur_state=None):
        global event_id_counter
        self.group_id = event_id_counter
        event_id_counter += 1

        self.name = event_definition.get_label()
        self.to_defeat_idx = to_defeat_idx
        self.event_definition = event_definition

        self.init_state = None
        self.final_state = None
        self.error_message = ""

        if cur_state is not None:
            self.apply(cur_state)
    
    def contains_id(self, id_val):
        return self.group_id == id_val
    
    def apply(self, cur_state: route_state_objects.RouteState):
        self.init_state = cur_state
        if self.to_defeat_idx is not None:
            enemy_team = self.event_definition.get_pokemon_list()
            if len(enemy_team) <= self.to_defeat_idx:
                self.final_state = cur_state
                self.error_message = f"No Num {self.to_defeat_idx} pkmn from team: {self.event_definition}"
            else:
                # you only "defeat" a trainer after defeating their final pokemon
                trainer_name = self.event_definition.trainer_name if self.to_defeat_idx == len(enemy_team) - 1 else None
                self.name = f"{self.event_definition.trainer_name}: {enemy_team[self.to_defeat_idx].name}"
                self.final_state, self.error_message = cur_state.defeat_pkmn(enemy_team[self.to_defeat_idx], trainer_name=trainer_name)
        elif self.event_definition.is_rare_candy:
            self.final_state, self.error_message = cur_state.rare_candy()
        elif self.event_definition.vitamin is not None:
            self.final_state, self.error_message = cur_state.vitamin(self.event_definition.vitamin)
        elif self.event_definition.item_event_def is not None:
            if self.event_definition.item_event_def.is_acquire:
                self.final_state, self.error_message = cur_state.add_item(
                    self.event_definition.item_event_def.item_name,
                    self.event_definition.item_event_def.item_amount,
                    self.event_definition.item_event_def.with_money,
                )
            else:
                self.final_state, self.error_message = cur_state.remove_item(
                    self.event_definition.item_event_def.item_name,
                    self.event_definition.item_event_def.item_amount,
                    self.event_definition.item_event_def.with_money,
                )
        elif self.event_definition.learn_move is not None:
            # little bit of book-keeping. Manually update the definition to accurately reflect what happened to the move
            self.event_definition.learn_move.destination = cur_state.solo_pkmn.get_move_destination(
                self.event_definition.learn_move.move_to_learn,
                self.event_definition.learn_move.destination,
            )
            self.name = self.event_definition.get_label()

            self.final_state, self.error_message = cur_state.learn_move(
                self.event_definition.learn_move.move_to_learn,
                self.event_definition.learn_move.destination,
                self.event_definition.learn_move.source,
            )


    def get_pkmn_after_levelups(self):
        return ""

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

    def has_errors(self):
        return len(self.error_message) != 0
    
    def is_major_fight(self):
        return False
    
    def get_tag(self):
        if self.has_errors():
            return const.EVENT_TAG_ERRORS

        return None


class EventGroup:
    def __init__(self, event_definition:EventDefinition):
        global event_id_counter
        self.group_id = event_id_counter
        event_id_counter += 1

        self.name = None
        self.final_state = None
        self.event_items = []
        self.init_state = None
        self.event_definition = event_definition
        self.pkmn_after_levelups = []
        self.error_messages = []
        self.level_up_learn_event_defs = []
    
    def apply(self, cur_state, level_up_learn_event_defs=None):
        self.name = self.event_definition.get_label()
        self.init_state = cur_state
        self.pkmn_after_levelups = []
        self.event_items = []

        if level_up_learn_event_defs is None:
            self.level_up_learn_event_defs = []
        else:
            self.level_up_learn_event_defs = level_up_learn_event_defs

        if self.event_definition.trainer_name is not None:
            trainer_obj = self.event_definition.get_trainer_obj()
            pkmn_counter = {}
            for pkmn_idx, trainer_pkmn in enumerate(trainer_obj.pkmn):
                self.event_items.append(EventItem(self.event_definition, to_defeat_idx=pkmn_idx, cur_state=cur_state))
                pkmn_counter[trainer_pkmn.name] = pkmn_counter.get(trainer_pkmn.name, 0) + 1
                
                next_state = self.event_items[-1].final_state
                # when a level up occurs
                if next_state.solo_pkmn.cur_level != cur_state.solo_pkmn.cur_level:
                    # learn moves, if needed
                    for learn_move in self.level_up_learn_event_defs:
                        if learn_move.level == next_state.solo_pkmn.cur_level:
                            self.event_items.append(EventItem(EventDefinition(learn_move=learn_move), cur_state=next_state))
                            next_state = self.event_items[-1].final_state
                    # keep track of pkmn coming out
                    if pkmn_idx + 1 < len(trainer_obj.pkmn):
                        next_pkmn_name = trainer_obj.pkmn[pkmn_idx + 1].name
                        next_pkmn_count = pkmn_counter.get(next_pkmn_name, 0) + 1
                        self.pkmn_after_levelups.append(f"#{next_pkmn_count} {next_pkmn_name}")
                    else:
                        self.pkmn_after_levelups.append("after_final_pkmn")
                cur_state = next_state
        
        elif self.event_definition.wild_pkmn_info is not None:
            # assumption: can only have at most one level up per event group of non-trainer battle types
            # This allows us to simplify the level up move learn checks
            self.event_items.append(EventItem(self.event_definition, to_defeat_idx=0, cur_state=cur_state))
            if self.level_up_learn_event_defs:
                self.event_items.append(EventItem(EventDefinition(learn_move=self.level_up_learn_event_defs[0]), cur_state=self.event_items[0].final_state))
        else:
            # assumption: can only have at most one level up per event group of non-trainer battle types
            # This allows us to simplify the level up move learn checks
            self.event_items.append(EventItem(self.event_definition, cur_state=cur_state))
            if self.level_up_learn_event_defs:
                self.event_items.append(EventItem(EventDefinition(learn_move=self.level_up_learn_event_defs[0]), cur_state=self.event_items[0].final_state))
            
        if len(self.event_items) == 0:
            raise ValueError(f"Something went wrong generating event group: {self.event_definition}")
        
        self.error_messages = [x.error_message for x in self.event_items if x.error_message]
        if self.error_messages:
            self.name = ", ".join(self.error_messages)
        self.final_state = self.event_items[-1].final_state
    
    def contains_id(self, id_val):
        if self.group_id == id_val:
            return True
        
        return any([x.contains_id(id_val) for x in self.event_items])
    
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

    def to_dict(self, folder_name=None):
        return self.event_definition.serialize(folder_name)
    
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


class EventFolder:
    def __init__(self, name):
        global event_id_counter
        self.group_id = event_id_counter
        event_id_counter += 1

        self.name = name
        self.init_state = None
        self.final_state = None
        self.child_errors = False
        self.event_groups = []
    
    def add_event_group(self, group:EventGroup, force_recalculation=False):
        self.event_groups.append(group)

        if force_recalculation:
            self.apply(self.init_state)
    
    def remove_event_group(self, group_id, force_recalculation=False):
        result = None
        for idx in range(len(self.event_groups)):
            if self.event_groups[idx].contains_id(group_id):
                result = self.event_groups[idx]
                del self.event_groups[idx]
                break
        
        if result is None:
            raise ValueError(f"EventFolder {self.name} does not have group_id {group_id}")

        if force_recalculation:
            self.apply(self.init_state)
        
        return result

    def apply(self, cur_state):
        self.init_state = cur_state
        self.child_errors = False

        for cur_group in self.event_groups:
            cur_group.apply(cur_state)
            cur_state = cur_group.final_state
            if cur_group.has_errors():
                self.child_errors = True
        
        self.final_state = cur_state
    
    def contains_id(self, id_val):
        if self.group_id == id_val:
            return True
        
        return any([x.contains_id(id_val) for x in self.event_items])

    def pkmn_after_levelups(self):
        return ""

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

    def serialize(self):
        return [x.to_dict(self.name) for x in self.event_groups]
    
    def has_errors(self):
        return self.child_errors
    
    def is_major_fight(self):
        return False
    
    def get_tag(self):
        if self.has_errors():
            return const.EVENT_TAG_ERRORS

        if self.is_major_fight():
            return const.EVENT_TAG_IMPORTANT
        
        return None