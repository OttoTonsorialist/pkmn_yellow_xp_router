from __future__ import annotations
import os
import logging
from typing import List, Tuple

from utils.constants import const
from utils.config_manager import config
from utils import route_one_utils
from routing.route_events import EventDefinition, EventFolder, EventGroup, EventItem, LearnMoveEventDefinition, TrainerEventDefinition
import routing.router
import pkmn

logger = logging.getLogger(__name__)


def handle_exceptions(controller_fn):
    # must wrap an instance method from the MainController class
    def wrapper(*args, **kwargs):
        try:
            controller_fn(*args, **kwargs)
        except Exception as e:
            controller:MainController = args[0]
            controller._on_exception(f"{type(e)}: {e}")
    
    return wrapper


class MainController:
    def __init__(self):
        self._data:routing.router.Router = routing.router.Router()
        self._current_preview_event = None
        self._route_name = ""
        self._selected_ids = []
        self._is_record_mode_active = False
        self._exception_info = []

        self._name_change_events = []
        self._version_change_events = []
        self._route_change_events = []
        self._event_change_events = []
        self._event_selection_events = []
        self._event_preview_events = []
        self._record_mode_change_events = []
        self._exception_events = []
    
    def get_next_exception_info(self):
        if not len(self._exception_info):
            return None
        return self._exception_info.pop(0)

    #####
    # Registration methods
    #####

    def register_name_change(self, tk_obj):
        new_event_name = const.EVENT_NAME_CHANGE.format(len(self._name_change_events))
        self._name_change_events.append((tk_obj, new_event_name))
        return new_event_name

    def register_version_change(self, tk_obj):
        new_event_name = const.EVENT_VERSION_CHANGE.format(len(self._version_change_events))
        self._version_change_events.append((tk_obj, new_event_name))
        return new_event_name

    def register_route_change(self, tk_obj):
        new_event_name = const.EVENT_ROUTE_CHANGE.format(len(self._route_change_events))
        self._route_change_events.append((tk_obj, new_event_name))
        return new_event_name

    def register_event_update(self, tk_obj):
        new_event_name = const.EVENT_EVENT_CHANGE.format(len(self._event_change_events))
        self._event_change_events.append((tk_obj, new_event_name))
        return new_event_name

    def register_event_selection(self, tk_obj):
        new_event_name = const.EVENT_SELECTION_CHANGE.format(len(self._event_selection_events))
        self._event_selection_events.append((tk_obj, new_event_name))
        return new_event_name

    def register_event_preview(self, tk_obj):
        new_event_name = const.EVENT_PREVIEW_CHANGE.format(len(self._event_preview_events))
        self._event_preview_events.append((tk_obj, new_event_name))
        return new_event_name

    def register_record_mode_change(self, tk_obj):
        new_event_name = const.EVENT_RECORD_MODE_CHANGE.format(len(self._record_mode_change_events))
        self._record_mode_change_events.append((tk_obj, new_event_name))
        return new_event_name

    def register_exception_callback(self, tk_obj):
        new_event_name = const.EVENT_EXCEPTION.format(len(self._exception_events))
        self._exception_events.append((tk_obj, new_event_name))
        return new_event_name
    
    #####
    # Event callbacks
    #####
    
    def _on_name_change(self):
        for tk_obj, cur_event_name in self._name_change_events:
            tk_obj.event_generate(cur_event_name, when="tail")
    
    def _on_version_change(self):
        for tk_obj, cur_event_name in self._version_change_events:
            tk_obj.event_generate(cur_event_name, when="tail")
    
    def _on_route_change(self):
        for tk_obj, cur_event_name in self._route_change_events:
            tk_obj.event_generate(cur_event_name, when="tail")

    def _on_event_change(self):
        for tk_obj, cur_event_name in self._event_change_events:
            tk_obj.event_generate(cur_event_name, when="tail")

        self._on_route_change()

    def _on_event_selection(self):
        for tk_obj, cur_event_name in self._event_selection_events:
            tk_obj.event_generate(cur_event_name, when="tail")

    def _on_event_preview(self):
        for tk_obj, cur_event_name in self._event_preview_events:
            tk_obj.event_generate(cur_event_name, when="tail")

    def _on_record_mode_change(self):
        for tk_obj, cur_event_name in self._record_mode_change_events:
            tk_obj.event_generate(cur_event_name, when="tail")

    def _on_exception(self, exception_message):
        self._exception_info.append(exception_message)
        for tk_obj, cur_event_name in self._exception_events:
            tk_obj.event_generate(cur_event_name, when="tail")

    ######
    # Methods that induce a state change
    # TODO: is it ok that all of the changes (including callbacks) are blocking?
    ######

    @handle_exceptions
    def select_new_events(self, all_event_ids):
        self._selected_ids = all_event_ids
        if len(all_event_ids) != 0:
            self._current_preview_event = None

        # kind of gross to have repeated check, but we want all state fully changed before triggering events
        self._on_event_selection()
        if len(all_event_ids) != 0:
            self._on_event_preview()

    @handle_exceptions
    def set_preview_trainer(self, trainer_name):
        if self._current_preview_event is not None and self._current_preview_event.trainer_def.trainer_name == trainer_name:
            return
        
        if pkmn.current_gen_info().trainer_db().get_trainer(trainer_name) is None:
            self._current_preview_event = None
        else:
            self._current_preview_event = EventDefinition(trainer_def=TrainerEventDefinition(trainer_name))

        self._on_event_preview()

    @handle_exceptions
    def update_existing_event(self, event_group_id, new_event):
        self._data.replace_event_group(event_group_id, new_event)
        self._on_event_change()

    @handle_exceptions
    def update_levelup_move(self, new_learn_move_event):
        self._data.replace_levelup_move_event(new_learn_move_event)
        self._on_event_change()
    
    @handle_exceptions
    def add_area(self, area_name, include_rematches, insert_after_id):
        self._data.add_area(
            area_name=area_name,
            insert_after=insert_after_id,
            include_rematches=include_rematches
        )
        self._on_route_change()

    @handle_exceptions
    def create_new_route(self, solo_mon, base_route_path, pkmn_version, custom_dvs=None):
        if base_route_path == const.EMPTY_ROUTE_NAME:
            base_route_path = None

        self._route_name = ""
        try:
            self._data.new_route(solo_mon, base_route_path, pkmn_version=pkmn_version, custom_dvs=custom_dvs)
        except Exception as e:
            logger.error(f"Exception ocurred trying to copy route: {base_route_path}")
            logger.exception(e)
            # load an empty route, just in case
            self._data.new_route(solo_mon)
            raise e
        finally:
            self._on_name_change()
            self._on_version_change()
            self._on_route_change()
    
    @handle_exceptions
    def load_route(self, full_path_to_route):
        try:
            _, route_name = os.path.split(full_path_to_route)
            route_name = os.path.splitext(route_name)[0]
            self._route_name = route_name

            self._data.load(full_path_to_route)
        except Exception as e:
            logger.error(f"Exception ocurred trying to load route: {full_path_to_route}")
            logger.exception(e)
            self._route_name = ""
            # load an empty route, just in case. Hardcoded, but wtv, Abra is in every game
            self._data.new_route("Abra")
            raise e
        finally:
            self._on_name_change()
            self._on_version_change()
            self._on_route_change()

    @handle_exceptions
    def customize_dvs(self, new_dvs):
        self._data.change_current_dvs(new_dvs)
        self._on_route_change()

    @handle_exceptions
    def move_groups_up(self, event_ids):
        for cur_event in event_ids:
            self._data.move_event_object(cur_event, True)
        self._on_route_change()

    @handle_exceptions
    def move_groups_down(self, event_ids):
        for cur_event in event_ids:
            self._data.move_event_object(cur_event, False)
        self._on_route_change()

    @handle_exceptions
    def delete_events(self, event_ids):
        self._data.batch_remove_events(event_ids)

        selection_changed = False
        for cur_event_id in event_ids:
            if cur_event_id in self._selected_ids:
                self._selected_ids.remove(cur_event_id)
                selection_changed = True

        self._on_route_change()
        if selection_changed:
            self._on_event_selection()

    @handle_exceptions
    def purge_empty_folders(self):
        while True:
            deleted_ids = []
            for cur_folder_name, cur_folder in self._data.folder_lookup.items():
                if cur_folder_name == const.ROOT_FOLDER_NAME:
                    continue
                if len(cur_folder.children) == 0:
                    deleted_ids.append(cur_folder.group_id)
            
            if len(deleted_ids) != 0:
                self.delete_events(deleted_ids)
            else:
                break
    
    @handle_exceptions
    def transfer_to_folder(self, event_ids, new_folder_name):
        self._data.transfer_events(event_ids, new_folder_name)
        self._on_route_change()

    @handle_exceptions
    def new_event(self, event_def, insert_after=None, dest_folder_name=const.ROOT_FOLDER_NAME, auto_select=False):
        result = self._data.add_event_object(event_def=event_def, insert_after=insert_after, dest_folder_name=dest_folder_name)
        self._on_route_change()
        if auto_select:
            self.select_new_events([result])
        return result

    @handle_exceptions
    def finalize_new_folder(self, new_folder_name, prev_folder_name=None, insert_after=None):
        if prev_folder_name is None and insert_after is None:
            self._data.add_event_object(new_folder_name=new_folder_name)
        elif prev_folder_name is None:
            self._data.add_event_object(new_folder_name=new_folder_name, insert_after=insert_after)
        else:
            self._data.rename_event_folder(prev_folder_name, new_folder_name)

        self._on_route_change()

    @handle_exceptions
    def toggle_event_highlight(self, event_ids):
        for cur_event in event_ids:
            self._data.toggle_event_highlight(cur_event)
        
        self._on_route_change()

    @handle_exceptions
    def set_record_mode(self, new_record_mode):
        self._is_record_mode_active = new_record_mode
        self._on_record_mode_change()
    
    def trigger_exception(self, exception_message):
        self._on_exception(exception_message)

    ######
    # Methods that do not induce a state change
    ######

    def get_raw_route(self) -> routing.router.Router:
        return self._data

    def get_current_route_name(self) -> str:
        return self._route_name

    def get_preview_event(self):
        return self._current_preview_event

    def get_event_by_id(self, event_id):
        return self._data.get_event_obj(event_id)
    
    def has_errors(self):
        return self._data.root_folder.has_errors()
    
    def get_version(self):
        return self._data.pkmn_version
    
    def get_state_after(self, previous_event_id=None):
        if previous_event_id:
            return self._data.init_route_state

        prev_event = self.get_event_by_id(previous_event_id)
        if prev_event is None:
            return self._data.init_route_state
        
        return prev_event.init_state
    
    def get_init_state(self):
        return self._data.init_route_state
    
    def get_final_state(self):
        return self._data.get_final_state()
    
    def get_all_folder_names(self):
        return list(self._data.folder_lookup.keys())
    
    def get_invalid_folders(self, event_id):
        return self._data.get_invalid_folder_transfers(event_id)
    
    def get_dvs(self):
        return self._data.init_route_state.solo_pkmn.dvs
    
    def get_defeated_trainers(self):
        return self._data.defeated_trainers
    
    def is_empty(self):
        return len(self._data.root_folder.children) == 0
    
    def get_all_selected_ids(self, allow_event_items=True):
        if allow_event_items:
            return self._selected_ids

        return [x for x in self._selected_ids if not isinstance(self.get_event_by_id(x), EventItem)]
    
    def get_single_selected_event_id(self, allow_event_items=True):
        if len(self._selected_ids) == 0 or len(self._selected_ids) > 1:
            return None
        
        if not allow_event_items:
            event_obj = self.get_event_by_id(self._selected_ids[0])
            if isinstance(event_obj, EventItem):
                return None

        return self._selected_ids[0]
    
    def get_single_selected_event_obj(self, allow_event_items=True):
        return self.get_event_by_id(
            self.get_single_selected_event_id(allow_event_items=allow_event_items)
        )
    
    def can_insert_after_current_selection(self):
        # Can always insert if the route is empty
        if self.is_empty():
            return True
        
        # Can't insert is if the route is non-empty, and nothing is selected
        cur_obj = self.get_single_selected_event_obj()
        if cur_obj is None:
            return False
        
        # Can't insert after EventItems, only other event types
        return not isinstance(cur_obj, EventItem)

    def save_route(self, route_name):
        self._data.save(route_name)
    
    def export_notes(self, route_name):
        self._data.export_notes(route_name)

    def just_export_and_run(self, route_name):
        success = False
        try:
            jar_path = config.get_route_one_path()
            if not jar_path:
                config_path, _, _ = route_one_utils.export_to_route_one(self._data, route_name)
                result = f"Could not run RouteOne, jar path not set. Exported RouteOne files: {config_path}"
            else:
                config_path, _, out_path = route_one_utils.export_to_route_one(self._data, route_name)
                error_code = route_one_utils.run_route_one(jar_path, config_path)
                if not error_code:
                    success = True
                    result = f"Ran RouteOne successfully. Result file: {out_path}"
                else:
                    result = f"RouteOne exited with error code: {error_code}"
        except Exception as e:
            result = f"Exception attempting to export and run RouteOne: {type(e)}: {e}"
            logger.error(e)
            logger.exception(e)
        
        return success, result
    
    def is_record_mode_active(self):
        return self._is_record_mode_active
    
    def get_levelup_move_event(self, move_name, new_level) -> LearnMoveEventDefinition:
        levelup_move = self._data.level_up_move_defs.get(tuple(move_name, new_level))
        if levelup_move is None:
            # NOTE: check for edge case that mon got 2 level ups at once, and got move from first level up
            # this is rare, but theoretically possible. It should also be safe, because there are no cases where
            # the same move is learned 2 levels in a row
            levelup_move = self._data.level_up_move_defs.get(tuple(move_name, new_level))
        
        return levelup_move
    
    def get_move_idx(self, move_name, state=None):
        if state is None:
            state = self.get_final_state()
        
        move_idx = None
        for cur_idx, cur_move in enumerate(state.solo_pkmn.move_list):
            if cur_move == move_name:
                move_idx = cur_idx
                break
        
        return move_idx
    
    def _walk_events_helper(self, cur_folder:EventFolder, cur_event_id:int, cur_event_found:bool, walk_forward=True) -> Tuple[bool, EventGroup]:
        if walk_forward:
            iterable = cur_folder.children
        else:
            iterable = reversed(cur_folder.children)

        for test_obj in iterable:
            if isinstance(test_obj, EventGroup):
                if cur_event_found:
                    return cur_event_found, test_obj
                elif test_obj.group_id == cur_event_id:
                    cur_event_found = True
            elif isinstance(test_obj, EventFolder):
                cur_event_found, prev_result = self._walk_events_helper(test_obj, cur_event_id, cur_event_found, walk_forward=walk_forward)
                if cur_event_found and prev_result is not None:
                    return cur_event_found, prev_result
            else:
                logger.error(f"Encountered unexpected types walking events: {type(test_obj)}")
        
        return cur_event_found, None
            
    def get_next_event(self, cur_event_id=None) -> EventGroup:
        return self._walk_events_helper(
            self._data.root_folder,
            cur_event_id=cur_event_id,
            cur_event_found=(cur_event_id == None)
        )[1]

    def get_previous_event(self, cur_event_id=None) -> EventGroup:
        return self._walk_events_helper(
            self._data.root_folder,
            cur_event_id=cur_event_id,
            cur_event_found=(cur_event_id == None),
            walk_forward=False
        )[1]