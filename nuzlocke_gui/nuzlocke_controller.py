from __future__ import annotations
import os
import logging
from typing import List, Tuple
from pkmn.universal_data_objects import BadgeList
from routing.state_objects import SoloPokemon

from utils.constants import const
from routing.route_events import EventDefinition, EventFolder, EventGroup, EventItem, LearnMoveEventDefinition, TrainerEventDefinition
import routing.router
from pkmn import gen_factory


logger = logging.getLogger(__name__)


def handle_exceptions(controller_fn):
    # must wrap an instance method from the MainController class
    def wrapper(*args, **kwargs):
        try:
            controller_fn(*args, **kwargs)
        except Exception as e:
            logger.error(f"Trying to run function: {controller_fn}, got error: {e}")
            logger.exception(e)
            controller:NuzlockeController = args[0]
            controller._on_exception(f"{type(e)}: {e}")
    
    return wrapper


class NuzlockeController:
    def __init__(self):
        self._cur_version = const.YELLOW_VERSION
        self._badge_list:BadgeList = None
        self._solo_mon_list:List[SoloPokemon] = [None] * 6
        self._enemy_trainer_name = None
        self._exception_info = []
        self._active_mon_idx = 0

        self._version_change_events = []
        self._mon_change_events = []
        self._active_mon_change_events = []
        self._badge_change_events = []
        self._trainer_change_events = []
        self._exception_events = []

    
    def get_next_exception_info(self):
        if not len(self._exception_info):
            return None
        return self._exception_info.pop(0)

    #####
    # Registration methods
    #####

    def register_version_change(self, tk_obj):
        new_event_name = const.EVENT_VERSION_CHANGE.format(len(self._version_change_events))
        self._version_change_events.append((tk_obj, new_event_name))
        return new_event_name

    def register_mon_change(self, tk_obj):
        new_event_name = const.EVENT_MON_CHANGE.format(len(self._mon_change_events))
        self._mon_change_events.append((tk_obj, new_event_name))
        return new_event_name

    def register_active_mon_change(self, tk_obj):
        new_event_name = const.EVENT_ACTIVE_MON_CHANGE.format(len(self._active_mon_change_events))
        self._active_mon_change_events.append((tk_obj, new_event_name))
        return new_event_name

    def register_badge_change(self, tk_obj):
        new_event_name = const.EVENT_BADGE_CHANGE.format(len(self._badge_change_events))
        self._badge_change_events.append((tk_obj, new_event_name))
        return new_event_name

    def register_trainer_change(self, tk_obj):
        new_event_name = const.EVENT_TRAINER_CHANGE.format(len(self._trainer_change_events))
        self._trainer_change_events.append((tk_obj, new_event_name))
        return new_event_name

    def register_exception_callback(self, tk_obj):
        new_event_name = const.EVENT_EXCEPTION.format(len(self._exception_events))
        self._exception_events.append((tk_obj, new_event_name))
        return new_event_name
    
    #####
    # Event callbacks
    #####
    
    def _on_version_change(self):
        for tk_obj, cur_event_name in self._version_change_events:
            tk_obj.event_generate(cur_event_name, when="tail")
    
    def _on_mon_change(self):
        for tk_obj, cur_event_name in self._mon_change_events:
            tk_obj.event_generate(cur_event_name, when="tail")
    
    def _on_active_mon_change(self):
        for tk_obj, cur_event_name in self._active_mon_change_events:
            tk_obj.event_generate(cur_event_name, when="tail")

    def _on_badge_change(self):
        for tk_obj, cur_event_name in self._badge_change_events:
            tk_obj.event_generate(cur_event_name, when="tail")

    def _on_trainer_change(self):
        for tk_obj, cur_event_name in self._trainer_change_events:
            tk_obj.event_generate(cur_event_name, when="tail")

    def _on_exception(self, exception_message):
        self._exception_info.append(exception_message)
        for tk_obj, cur_event_name in self._exception_events:
            tk_obj.event_generate(cur_event_name, when="tail")

    ######
    # Methods that induce a state change
    ######

    @handle_exceptions
    def set_new_solo_mon(self, solo_mon, mon_idx):
        if mon_idx < 0 or mon_idx >= len(self._solo_mon_list):
            raise IndexError(f"Invalid target index {mon_idx} for solo mon {solo_mon}")
        
        self._solo_mon_list[mon_idx] = solo_mon
        self._on_mon_change()

    @handle_exceptions
    def update_active_mon_idx(self, mon_idx):
        if mon_idx < 0 or mon_idx >= len(self._solo_mon_list):
            raise IndexError(f"Invalid target index {mon_idx}")
        
        self._active_mon_idx = mon_idx
        self._on_active_mon_change()

    @handle_exceptions
    def update_badge_list(self, new_badge_list):
        if not isinstance(new_badge_list, BadgeList):
            raise TypeError(f"badge_list must be a BadgeList type, not {type(new_badge_list)}")
        
        self._badge_list = new_badge_list
        self._on_badge_change()
    
    @handle_exceptions
    def set_enemy_trainer(self, trainer_name):
        enemy_trainer = gen_factory.current_gen_info().trainer_db().get_trainer(trainer_name)
        if enemy_trainer is None and trainer_name is not None:
            trainer_name = None
        
        self._enemy_trainer_name = enemy_trainer
        self._on_trainer_change()
    
    @handle_exceptions
    def set_current_version(self, version_name):
        gen_factory.change_version(version_name)
        self._cur_version = version_name
        self._on_version_change()

    @handle_exceptions
    def load_all_custom_versions(self):
        gen_factory._gen_factory.reload_all_custom_gens()
    
    def trigger_exception(self, exception_message):
        self._on_exception(exception_message)

    ######
    # Methods that do not induce a state change
    ######

    def get_player_team(self) -> List[SoloPokemon]:
        return self._solo_mon_list

    def get_active_mon(self) -> SoloPokemon:
        return self._solo_mon_list[self._active_mon_idx]

    def get_enemy_team(self):
        return gen_factory.current_gen_info().trainer_db().get_trainer(self._enemy_trainer_name)

    def get_badge_list(self):
        return self._badge_list
    
    def get_version(self):
        return self._cur_version
