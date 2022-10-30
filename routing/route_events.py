
from typing import List
from utils.constants import const
from routing import route_state_objects
import pkmn

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


class HoldItemEventDefinition:
    def __init__(self, item_name):
        self.item_name = item_name

    def serialize(self):
        return [self.item_name]

    @staticmethod
    def deserialize(raw_val):
        if not raw_val:
            return None
        return HoldItemEventDefinition(raw_val[0])
    
    def __str__(self):
        return f"Hold {self.item_name}"


class VitaminEventDefinition:
    def __init__(self, vitamin, amount):
        self.vitamin = vitamin
        self.amount = amount

    def serialize(self):
        return [self.vitamin, self.amount]
    
    @staticmethod
    def deserialize(raw_val):
        if not raw_val:
            return None
        # backwards compatibility
        if isinstance(raw_val, str):
            return VitaminEventDefinition(raw_val, 1)
        else:
            return VitaminEventDefinition(raw_val[0], raw_val[1])
    
    def __str__(self):
        return f"Vitamin {self.vitamin}, x{self.amount}"


class RareCandyEventDefinition:
    def __init__(self, amount):
        self.amount = amount

    def serialize(self):
        return self.amount
    
    @staticmethod
    def deserialize(raw_val):
        if not raw_val:
            return None
        # backwards compatibility
        if raw_val is True:
            raw_val = 1
        return RareCandyEventDefinition(raw_val)
    
    def __str__(self):
        return f"Rare Candy, x{self.amount}"


class WildPkmnEventDefinition:
    def __init__(self, name, level, quantity=1, trainer_pkmn=False):
        self.name = name
        self.level = level
        self.quantity = quantity
        self.trainer_pkmn = trainer_pkmn

    def serialize(self):
        return [self.name, self.level, self.quantity, self.trainer_pkmn]
    
    @staticmethod
    def deserialize(raw_val):
        if not raw_val:
            return None
        if len(raw_val) == 2:
            return WildPkmnEventDefinition(raw_val[0], raw_val[1])
        else:
            return WildPkmnEventDefinition(raw_val[0], raw_val[1], quantity=raw_val[2], trainer_pkmn=raw_val[3])
    
    def __str__(self):
        prefix = "TrainerPkmn" if self.trainer_pkmn else "WildPkmn"
        return f"{prefix} {self.name}, LV: {self.level}"


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
        return LearnMoveEventDefinition(raw_val[0], raw_val[1], raw_val[2], level=raw_val[3])
    
    def __str__(self):
        if self.destination is None:
            return f"Ignoring {self.move_to_learn}, from {self.source}"
        return f"Learning {self.move_to_learn} in slot #: {self.destination + 1}, from {self.source}"


class TrainerEventDefinition:
    def __init__(self, trainer_name, verbose_export=False, setup_moves=None, mimic_selection="", custom_move_data=None):
        self.trainer_name = trainer_name
        self.verbose_export = verbose_export
        if setup_moves is None:
            setup_moves = []
        self.setup_moves = setup_moves
        self.mimic_selection = mimic_selection
        self.custom_move_data = custom_move_data

    def serialize(self):
        return {
            const.TRAINER_NAME: self.trainer_name,
            const.VERBOSE_KEY: self.verbose_export,
            const.SETUP_MOVES_KEY: self.setup_moves,
            const.MIMIC_SELECTION: self.mimic_selection,
            const.CUSTOM_MOVE_DATA: self.custom_move_data,
        }
    
    @staticmethod
    def deserialize(raw_val):
        if not raw_val:
            return None
        if isinstance(raw_val, str):
            return TrainerEventDefinition(raw_val)
        
        if isinstance(raw_val, list):
            trainer_name = raw_val[0]
            verbose_export = raw_val[1]
            setup_moves = None
            if len(raw_val) > 2:
                setup_moves = raw_val[2]
            return TrainerEventDefinition(trainer_name, verbose_export=verbose_export, setup_moves=setup_moves)

        return TrainerEventDefinition(
            raw_val[const.TRAINER_NAME],
            verbose_export=raw_val[const.VERBOSE_KEY],
            setup_moves=raw_val[const.SETUP_MOVES_KEY],
            mimic_selection=raw_val[const.MIMIC_SELECTION],
            custom_move_data=raw_val.get(const.CUSTOM_MOVE_DATA),
        )
    
    def __str__(self):
        return f"Trainer {self.trainer_name}"


class EventDefinition:
    def __init__(self, enabled=True, rare_candy=None, vitamin=None, trainer_def=None, wild_pkmn_info=None, item_event_def=None, learn_move=None, hold_item=None, notes=""):
        self.enabled = enabled
        self.rare_candy = rare_candy
        self.vitamin = vitamin
        self.trainer_def = trainer_def
        self._trainer_obj = None
        self.wild_pkmn_info = wild_pkmn_info
        self._wild_pkmn = None
        self.item_event_def = item_event_def
        self.learn_move = learn_move
        self.hold_item = hold_item
        self.notes = notes

    def get_trainer_obj(self):
        if self._trainer_obj is None and self.trainer_def is not None:
            self._trainer_obj = pkmn.current_gen_info().trainer_db().get_trainer(self.trainer_def.trainer_name)
            if self._trainer_obj is None:
                raise ValueError(f"Could not find trainer object for trainer named: '{self.trainer_def.trainer_name}', from trainer_db for version: {pkmn.current_gen_info().version_name()}")
        return self._trainer_obj
    
    def get_wild_pkmn(self):
        if self._wild_pkmn is None and self.wild_pkmn_info is not None:
            if self.wild_pkmn_info.trainer_pkmn:
                self._wild_pkmn = pkmn.current_gen_info().create_trainer_pkmn(self.wild_pkmn_info.name, self.wild_pkmn_info.level)
            else:
                self._wild_pkmn = pkmn.current_gen_info().create_wild_pkmn(self.wild_pkmn_info.name, self.wild_pkmn_info.level)
        return self._wild_pkmn
    
    def get_pokemon_list(self):
        wild_pkmn = self.get_wild_pkmn()
        if wild_pkmn is not None:
            # NOTE: technically bad, it's just multiple references to the same object
            # but since these objects are treated as immutable, it's not actually a problem
            return [wild_pkmn for _ in range(self.wild_pkmn_info.quantity)]
        
        trainer = self.get_trainer_obj()
        if trainer is not None:
            return trainer.pkmn
        
        return []
    
    def get_event_type(self):
        if self.rare_candy is not None:
            return const.TASK_RARE_CANDY
        elif self.vitamin is not None:
            return const.TASK_VITAMIN
        elif self.wild_pkmn_info is not None:
            return const.TASK_FIGHT_WILD_PKMN
        elif self.trainer_def is not None:
            return const.TASK_TRAINER_BATTLE
        elif self.item_event_def is not None:
            if self.item_event_def.is_acquire and self.item_event_def.with_money:
                return const.TASK_PURCHASE_ITEM
            elif self.item_event_def.is_acquire and not self.item_event_def.with_money:
                return const.TASK_GET_FREE_ITEM
            elif self.item_event_def.with_money:
                return const.TASK_SELL_ITEM
            else:
                return const.TASK_USE_ITEM
        elif self.learn_move is not None:
            if self.learn_move.source == const.MOVE_SOURCE_LEVELUP:
                return const.TASK_LEARN_MOVE_LEVELUP
            return const.TASK_LEARN_MOVE_TM
        elif self.hold_item is not None:
            return const.TASK_HOLD_ITEM
        
        return const.TASK_NOTES_ONLY

    def get_item_label(self):
        if self.rare_candy is not None:
            return "Rare Candy x1"
        elif self.vitamin is not None:
            return f"Vitamin: {self.vitamin.vitamin} x1"
        elif self.wild_pkmn_info is not None:
            return str(self.wild_pkmn_info)
        elif self.trainer_def is not None:
            trainer = self.get_trainer_obj()
            return f"Trainer: {trainer.name} ({trainer.location})"
        elif self.item_event_def is not None:
            return str(self.item_event_def)
        elif self.learn_move is not None:
            return str(self.learn_move)
        elif self.hold_item is not None:
            return str(self.hold_item)
        
        return f"Notes: {self.notes}"
    
    def get_label(self):
        if self.rare_candy is not None:
            return str(self.rare_candy)
        elif self.vitamin is not None:
            return str(self.vitamin)
        elif self.wild_pkmn_info is not None:
            return str(self.wild_pkmn_info)
        elif self.trainer_def is not None:
            trainer = self.get_trainer_obj()
            return f"Trainer: {trainer.name} ({trainer.location})"
        elif self.item_event_def is not None:
            return str(self.item_event_def)
        elif self.learn_move is not None:
            return str(self.learn_move)
        elif self.hold_item is not None:
            return str(self.hold_item)
        
        return f"Notes: {self.notes}"
    
    def __str__(self):
        return self.get_label()

    
    def serialize(self):
        result = {const.ENABLED_KEY: self.enabled}
        if self.notes:
            result[const.TASK_NOTES_ONLY] = self.notes

        if self.rare_candy is not None:
            result.update({const.TASK_RARE_CANDY: self.rare_candy.serialize()})
        elif self.vitamin is not None:
            result.update({const.TASK_VITAMIN: self.vitamin.serialize()})
        elif self.trainer_def is not None:
            result.update({const.TASK_TRAINER_BATTLE: self.trainer_def.serialize()})
        elif self.wild_pkmn_info is not None:
            result.update({const.TASK_FIGHT_WILD_PKMN: self.wild_pkmn_info.serialize()})
        elif self.item_event_def is not None:
            result.update({const.INVENTORY_EVENT_DEFINITON: self.item_event_def.serialize()})
        elif self.learn_move is not None:
            result.update({const.LEARN_MOVE_KEY: self.learn_move.serialize()})
        elif self.hold_item is not None:
            result.update({const.TASK_HOLD_ITEM: self.hold_item.serialize()})
        
        return result    

    @staticmethod
    def deserialize(raw_val):
        result = EventDefinition(
            enabled=raw_val.get(const.ENABLED_KEY, True),
            notes=raw_val.get(const.TASK_NOTES_ONLY, ""),
            rare_candy=RareCandyEventDefinition.deserialize(raw_val.get(const.TASK_RARE_CANDY)),
            vitamin=VitaminEventDefinition.deserialize(raw_val.get(const.TASK_VITAMIN)),
            trainer_def=TrainerEventDefinition.deserialize(raw_val.get(const.TASK_TRAINER_BATTLE)),
            wild_pkmn_info=WildPkmnEventDefinition.deserialize(raw_val.get(const.TASK_FIGHT_WILD_PKMN)),
            item_event_def=InventoryEventDefinition.deserialize(raw_val.get(const.INVENTORY_EVENT_DEFINITON)),
            learn_move=LearnMoveEventDefinition.deserialize(raw_val.get(const.LEARN_MOVE_KEY)),
            hold_item=HoldItemEventDefinition.deserialize(raw_val.get(const.TASK_HOLD_ITEM)),
        )
        if result.wild_pkmn_info is not None:
            result.trainer_def = None
        return result


class EventItem:
    """
    This class effectively functions as the conversion layer between EventDefinitions and the RouteState object.
    """
    def __init__(self, parent, event_definition:EventDefinition, to_defeat_idx=None, cur_state=None):
        global event_id_counter
        self.group_id = event_id_counter
        event_id_counter += 1

        self.enabled = True
        self.parent = parent
        self.name = event_definition.get_item_label()
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
        self.enabled = self.event_definition.enabled
        if not self.enabled:
            self.final_state = cur_state
            self.error_message = ""
            self.name = f"Disabled: {self.event_definition.get_label()}"
            return

        if self.to_defeat_idx is not None:
            enemy_team = self.event_definition.get_pokemon_list()
            if len(enemy_team) <= self.to_defeat_idx:
                self.final_state = cur_state
                self.error_message = f"No Num {self.to_defeat_idx} pkmn from team: {self.event_definition}"
            else:
                # you only "defeat" a trainer after defeating their final pokemon
                if self.event_definition.trainer_def is not None:
                    if self.to_defeat_idx == len(enemy_team) - 1:
                        defeated_trainer_name = self.event_definition.trainer_def.trainer_name
                    else:
                        defeated_trainer_name = None
                    render_trainer_name = self.event_definition.trainer_def.trainer_name
                else:
                    defeated_trainer_name = None
                    render_trainer_name = "TrainerPkmn" if self.event_definition.wild_pkmn_info.trainer_pkmn else "WildPkmn"

                self.name = f"{render_trainer_name}: {enemy_team[self.to_defeat_idx].name}"
                self.final_state, self.error_message = cur_state.defeat_pkmn(enemy_team[self.to_defeat_idx], trainer_name=defeated_trainer_name)
        elif self.event_definition.rare_candy is not None:
            # note: deliberatley ignoring amount here, that's handled at the group level
            # just apply one rare candy at the item level
            self.final_state, self.error_message = cur_state.rare_candy()
        elif self.event_definition.vitamin is not None:
            # note: deliberatley ignoring amount here, that's handled at the group level
            # just apply one vitamin at the item level
            self.final_state, self.error_message = cur_state.vitamin(self.event_definition.vitamin.vitamin)
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
            dest_info = cur_state.solo_pkmn.get_move_destination(
                self.event_definition.learn_move.move_to_learn,
                self.event_definition.learn_move.destination,
            )
            self.event_definition.learn_move.destination = dest_info[0]

            self.name = self.event_definition.get_label()
            self.final_state, self.error_message = cur_state.learn_move(
                self.event_definition.learn_move.move_to_learn,
                self.event_definition.learn_move.destination,
                self.event_definition.learn_move.source,
            )
        elif self.event_definition.hold_item is not None:
            self.final_state, self.error_message = cur_state.hold_item(
                self.event_definition.hold_item.item_name
            )
        else:
            # Notes only, no processing just pass through
            self.final_state = self.init_state
            self.error_message = ""


    def get_pkmn_after_levelups(self):
        return ""

    def pkmn_level(self):
        if not self.enabled:
            return ""
        return self.final_state.solo_pkmn.cur_level
    
    def xp_to_next_level(self):
        if not self.enabled:
            return ""
        return self.final_state.solo_pkmn.xp_to_next_level

    def percent_xp_to_next_level(self):
        if not self.enabled:
            return ""
        return self.final_state.solo_pkmn.percent_xp_to_next_level

    def xp_gain(self):
        if not self.enabled:
            return ""
        return self.final_state.solo_pkmn.cur_xp - self.init_state.solo_pkmn.cur_xp

    def total_xp(self):
        if not self.enabled:
            return ""
        return self.final_state.solo_pkmn.cur_xp

    def has_errors(self):
        return len(self.error_message) != 0

    def is_enabled(self):
        return self.enabled
    
    def is_major_fight(self):
        return False
    
    def get_tags(self):
        if self.has_errors():
            return [const.EVENT_TAG_ERRORS]

        return []


class EventGroup:
    def __init__(self, parent, event_definition:EventDefinition):
        global event_id_counter
        self.group_id = event_id_counter
        event_id_counter += 1

        self.parent = parent
        self.enabled = True
        self.name = None
        self.init_state = None
        self.final_state = None
        self.event_items:List[EventItem] = []
        self.event_definition = event_definition
        self.pkmn_after_levelups = []
        self.error_messages = []
        self.level_up_learn_event_defs = []
    
    def apply(self, cur_state, level_up_learn_event_defs=None):
        self.name = self.event_definition.get_label()
        self.init_state = cur_state
        self.pkmn_after_levelups = []
        self.event_items = []
        self.enabled = self.event_definition.enabled

        if not self.enabled:
            self.final_state = cur_state
            self.error_messages = []
            self.name = f"Disabled: {self.event_definition.get_label()}"
            return

        if level_up_learn_event_defs is None:
            self.level_up_learn_event_defs = []
        else:
            self.level_up_learn_event_defs = level_up_learn_event_defs

        if self.event_definition.trainer_def is not None or self.event_definition.wild_pkmn_info is not None:
            pkmn_counter = {}
            pkmn_to_fight = self.event_definition.get_pokemon_list()
            for pkmn_idx, cur_pkmn in enumerate(pkmn_to_fight):
                self.event_items.append(EventItem(self, self.event_definition, to_defeat_idx=pkmn_idx, cur_state=cur_state))
                pkmn_counter[cur_pkmn.name] = pkmn_counter.get(cur_pkmn.name, 0) + 1
                
                next_state = self.event_items[-1].final_state
                if next_state is None or cur_state is None:
                    breakpoint()
                # when a level up occurs
                if next_state.solo_pkmn.cur_level != cur_state.solo_pkmn.cur_level:
                    # learn moves, if needed
                    for learn_move in self.level_up_learn_event_defs:
                        if learn_move.level == next_state.solo_pkmn.cur_level:
                            self.event_items.append(EventItem(self, EventDefinition(learn_move=learn_move), cur_state=next_state))
                            next_state = self.event_items[-1].final_state
                    # keep track of pkmn coming out
                    if pkmn_idx + 1 < len(pkmn_to_fight):
                        next_pkmn_name = pkmn_to_fight[pkmn_idx + 1].name
                        next_pkmn_count = pkmn_counter.get(next_pkmn_name, 0) + 1
                        self.pkmn_after_levelups.append(f"#{next_pkmn_count} {next_pkmn_name}")
                    else:
                        self.pkmn_after_levelups.append("after_final_pkmn")
                cur_state = next_state
        
        elif self.event_definition.wild_pkmn_info is not None:
            # assumption: can only have at most one level up per event group of non-trainer battle types
            # This allows us to simplify the level up move learn checks
            self.event_items.append(EventItem(self, self.event_definition, to_defeat_idx=0, cur_state=cur_state))
            if self.level_up_learn_event_defs:
                self.event_items.append(EventItem(self, EventDefinition(learn_move=self.level_up_learn_event_defs[0]), cur_state=self.event_items[0].final_state))
        elif self.event_definition.rare_candy is not None:
            for _ in range(self.event_definition.rare_candy.amount):
                self.event_items.append(EventItem(self, self.event_definition, cur_state=cur_state))
                # TODO: duplicated logic for handling level up moves. How can this be unified?
                next_state = self.event_items[-1].final_state
                if next_state.solo_pkmn.cur_level != cur_state.solo_pkmn.cur_level:
                    for learn_move in self.level_up_learn_event_defs:
                        if learn_move.level == next_state.solo_pkmn.cur_level:
                            self.event_items.append(EventItem(self, EventDefinition(learn_move=learn_move), cur_state=next_state))
                            next_state = self.event_items[-1].final_state
                cur_state = next_state
        elif self.event_definition.vitamin is not None:
            for _ in range(self.event_definition.vitamin.amount):
                self.event_items.append(EventItem(self, self.event_definition, cur_state=cur_state))
                cur_state = self.event_items[-1].final_state
        else:
            # assumption: can only have at most one level up per event group of non-trainer battle types
            # This allows us to simplify the level up move learn checks
            self.event_items.append(EventItem(self, self.event_definition, cur_state=cur_state))
            if self.level_up_learn_event_defs:
                self.event_items.append(EventItem(self, EventDefinition(learn_move=self.level_up_learn_event_defs[0]), cur_state=self.event_items[0].final_state))
            
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
        if not self.enabled:
            return ""
        return self.final_state.solo_pkmn.cur_level
    
    def xp_to_next_level(self):
        if not self.enabled:
            return ""
        return self.final_state.solo_pkmn.xp_to_next_level

    def percent_xp_to_next_level(self):
        if not self.enabled:
            return ""
        return self.final_state.solo_pkmn.percent_xp_to_next_level

    def xp_gain(self):
        if not self.enabled:
            return ""
        return self.final_state.solo_pkmn.cur_xp - self.init_state.solo_pkmn.cur_xp

    def total_xp(self):
        if not self.enabled:
            return ""
        return self.final_state.solo_pkmn.cur_xp

    def serialize(self):
        return self.event_definition.serialize()
    
    def has_errors(self):
        return len(self.error_messages) != 0
    
    def is_enabled(self):
        return self.enabled

    def set_enabled_status(self, is_enabled):
        self.enabled = self.event_definition.enabled = is_enabled

    def is_major_fight(self):
        if self.event_definition.trainer_def is None:
            return False
        if pkmn.current_gen_info() is None:
            return False
        return pkmn.current_gen_info().is_major_fight(self.event_definition.trainer_def.trainer_name)
    
    def get_tags(self):
        if self.has_errors():
            return [const.EVENT_TAG_ERRORS]

        if self.is_major_fight():
            return [const.EVENT_TAG_IMPORTANT]
        
        return []
    
    def __repr__(self):
        return f"EventGroup: {self.event_definition}"


class EventFolder:
    def __init__(self, parent, name, event_definition=None, expanded=True):
        global event_id_counter
        self.group_id = event_id_counter
        event_id_counter += 1

        self.parent = parent
        self.name = name
        self.enabled = True
        self.expanded = expanded
        if event_definition is None:
            event_definition = EventDefinition(notes="")
        self.event_definition = event_definition
        self.init_state = None
        self.final_state = None
        self.child_errors = False
        self.children = []
    
    def add_child(self, child_obj, force_recalculation=False):
        self.children.append(child_obj)
        child_obj.parent = self

        if force_recalculation:
            self.apply(self.init_state)
    
    def insert_child_before(self, child_obj, before_obj=None):
        if before_obj is None:
            self.add_child(child_obj=child_obj)
        
        else:
            try:
                insert_idx = self.children.index(before_obj)
                self.children.insert(insert_idx, child_obj)
                child_obj.parent = self
            except Exception as e:
                raise ValueError(f"Could not find object to insert before: {before_obj}")

    def move_child(self, child_obj, move_up_flag):
        try:
            idx = self.children.index(child_obj)
        except Exception as e:
            raise ValueError(f"In folder {self.name}, could not find object: {child_obj}")

        if move_up_flag:
            insert_idx = max(idx - 1, 0)
        else:
            insert_idx = min(idx + 1, len(self.children) - 1)
        
        self.children.remove(child_obj)
        self.children.insert(insert_idx, child_obj)
    
    def remove_child(self, child_obj, force_recalculation=False):
        try:
            self.children.remove(child_obj)
            # technically unnecessary, but just to be safe, unlink it as well
            child_obj.parent = None
        except Exception as e:
            raise ValueError(f"EventFolder {self.name} does not have child object: {child_obj}")

        if force_recalculation:
            self.apply(self.init_state)

    def apply(self, cur_state):
        self.init_state = cur_state
        self.child_errors = False

        if not self.enabled:
            self.final_state = cur_state
            return

        for cur_group in self.children:
            cur_group.apply(cur_state)
            cur_state = cur_group.final_state
            if cur_group.has_errors():
                self.child_errors = True
        
        self.final_state = cur_state
    
    def contains_id(self, id_val):
        if self.group_id == id_val:
            return True
        
        return any([x.contains_id(id_val) for x in self.event_items])

    def get_pkmn_after_levelups(self):
        return ""

    def pkmn_level(self):
        return ""
    
    def xp_to_next_level(self):
        return ""

    def percent_xp_to_next_level(self):
        return ""

    def xp_gain(self):
        return ""

    def total_xp(self):
        return ""

    def serialize(self):
        return {
            const.EVENT_FOLDER_NAME: self.name,
            const.TASK_NOTES_ONLY: self.event_definition.notes,
            const.EVENTS: [x.serialize() for x in self.children],
            const.EXPANDED_KEY: self.expanded
        }

    def is_enabled(self):
        return self.enabled

    def set_enabled_status(self, is_enabled):
        self.enabled = is_enabled
    
    def has_errors(self):
        return self.child_errors
    
    def get_tags(self):
        if self.has_errors():
            return [const.EVENT_TAG_ERRORS]
        
        return []
    
    def __repr__(self):
        return f"EventFolder: {self.name}"