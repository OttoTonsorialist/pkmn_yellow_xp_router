from __future__ import annotations
import os
import logging
from typing import List

from utils.constants import const
from utils.config_manager import config
from utils import route_one_utils
from routing.route_events import EventDefinition, EventFolder, EventGroup, EventItem, TrainerEventDefinition
import routing.router

logger = logging.getLogger(__name__)


def handle_exceptions(controller_fn):
    # must wrap an instance method from the MainController class
    def wrapper(*args, **kwargs):
        try:
            controller_fn(*args, **kwargs)
        except Exception as e:
            controller:MainController = args[0]
            controller._on_exception(e)
    
    return wrapper


class MainController:
    def __init__(self):
        self._main_window = None
        self._data:routing.router.Router = routing.router.Router()
        self._current_preview_event = None
        self._route_name = ""
        self._selected_ids = []

        self._name_change_callbacks = []
        self._version_change_callbacks = []
        self._route_change_callbacks = []
        self._event_change_callbacks = []
        self._event_selection_callbacks = []
        self._event_preview_callbacks = []
        self._exception_callbacks = []


    #####
    # Registration methods
    #####

    def register_name_change(self, callback_fn):
        self._name_change_callbacks.append(callback_fn)

    def register_version_change(self, callback_fn):
        self._version_change_callbacks.append(callback_fn)

    def register_route_change(self, callback_fn):
        self._route_change_callbacks.append(callback_fn)

    def register_event_update(self, callback_fn):
        self._event_change_callbacks.append(callback_fn)

    def register_event_selection(self, callback_fn):
        self._event_selection_callbacks.append(callback_fn)

    def register_event_preview(self, callback_fn):
        self._event_preview_callbacks.append(callback_fn)

    def register_exception_callback(self, callback_fn):
        self._exception_callbacks.append(callback_fn)
    
    #####
    # Event callbacks
    #####
    
    def _on_name_change(self):
        for cur_callback in self._name_change_callbacks:
            cur_callback()
    
    def _on_version_change(self):
        for cur_callback in self._version_change_callbacks:
            cur_callback()
    
    def _on_route_change(self):
        for cur_callback in self._route_change_callbacks:
            cur_callback()

    def _on_event_change(self):
        for cur_callback in self._event_change_callbacks:
            cur_callback()
        self._on_route_change()

    def _on_event_selection(self):
        for cur_callback in self._event_selection_callbacks:
            cur_callback()

    def _on_event_preview(self):
        for cur_callback in self._event_preview_callbacks:
            cur_callback()

    def _on_exception(self, exception):
        for cur_callback in self._event_preview_callbacks:
            cur_callback(exception)

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
    def trainer_add_preview(self, trainer_name):
        self._current_preview_event = EventDefinition(trainer_def=TrainerEventDefinition(trainer_name))
        self._on_event_preview()

    @handle_exceptions
    def update_existing_event(self, event_group_id, new_event):
        self._data.replace_event_group(event_group_id, new_event)
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
            # load an empty route, just in case. Hardcoded, but wtv, Abra is in ever game
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
        self._on_route_change()
    
    @handle_exceptions
    def transfer_to_folder(self, event_ids, new_folder_name):
        self._data.transfer_events(event_ids, new_folder_name)
        self._on_route_change()

    @handle_exceptions
    def new_event(self, event_def, insert_after=None):
        self._data.add_event_object(event_def=event_def, insert_after=insert_after)
        self._on_route_change()

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

    ######
    # Methods that do not induce a state change
    ######

    def get_raw_route(self) -> routing.router.Router:
        return self._data

    def get_current_route_name(self) -> str:
        return self._route_name

    def get_preview_event_id(self):
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
