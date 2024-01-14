from __future__ import annotations
import os
import logging
from typing import List, Tuple
import tkinter
from PIL import ImageGrab

from pkmn.pkmn_db import sanitize_string
from utils.constants import const
from utils import io_utils
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
        self._message_info = []
        self._route_filter_types = []
        self._route_search = ""
        self._unsaved_changes = False

        self._name_change_events = []
        self._version_change_events = []
        self._route_change_events = []
        self._event_change_events = []
        self._event_selection_events = []
        self._event_preview_events = []
        self._record_mode_change_events = []
        self._message_events = []
        self._exception_events = []

        self._pre_save_hooks = []
    
    def get_next_exception_info(self):
        if not len(self._exception_info):
            return None
        return self._exception_info.pop(0)

    def get_next_message_info(self):
        if not len(self._message_info):
            return None
        return self._message_info.pop(0)


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

    def register_message_callback(self, tk_obj):
        new_event_name = const.MESSAGE_EXCEPTION.format(len(self._message_events))
        self._message_events.append((tk_obj, new_event_name))
        return new_event_name

    def register_exception_callback(self, tk_obj):
        new_event_name = const.EVENT_EXCEPTION.format(len(self._exception_events))
        self._exception_events.append((tk_obj, new_event_name))
        return new_event_name

    def register_pre_save_hook(self, fn_obj):
        self._pre_save_hooks.append(fn_obj)
    
    #####
    # Event callbacks
    #####

    def _safely_generate_events(self, event_list):
        to_delete = []
        for cur_idx, (tk_obj, cur_event_name) in enumerate(event_list):
            try:
                tk_obj.event_generate(cur_event_name, when="tail")
            except tkinter.TclError:
                logger.info(f"Removing the following event due to TclError: {cur_event_name}")
                to_delete.append(cur_idx)
        
        for cur_idx in sorted(to_delete, reverse=True):
            del event_list[cur_idx]
    
    def _on_name_change(self):
        self._safely_generate_events(self._name_change_events)
    
    def _on_version_change(self):
        self._safely_generate_events(self._version_change_events)
    
    def _on_route_change(self):
        self._unsaved_changes = True
        self._safely_generate_events(self._route_change_events)

    def _on_event_change(self):
        self._safely_generate_events(self._event_change_events)
        self._on_route_change()

    def _on_event_selection(self):
        self._safely_generate_events(self._event_selection_events)

    def _on_event_preview(self):
        self._safely_generate_events(self._event_preview_events)

    def _on_record_mode_change(self):
        self._safely_generate_events(self._record_mode_change_events)

    def _on_info_message(self, info_message):
        self._message_info.append(info_message)
        self._safely_generate_events(self._message_events)

    def _on_exception(self, exception_message):
        self._exception_info.append(exception_message)
        self._safely_generate_events(self._exception_events)
    
    def _fire_pre_save_hooks(self):
        for cur_hook in self._pre_save_hooks:
            try:
                cur_hook()
            except Exception:
                logger.exception(f"Failed to run pre-save hook: {cur_hook}")

    ######
    # Methods that induce a state change
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
        
        if gen_factory.current_gen_info().trainer_db().get_trainer(trainer_name) is None:
            self._current_preview_event = None
        else:
            self._current_preview_event = EventDefinition(trainer_def=TrainerEventDefinition(trainer_name))

        self._on_event_preview()

    @handle_exceptions
    def update_existing_event(self, event_group_id:int, new_event:EventDefinition):
        if new_event.learn_move is not None and new_event.learn_move.source == const.MOVE_SOURCE_LEVELUP:
            return self.update_levelup_move(new_event.learn_move)
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
    def create_new_route(self, solo_mon, base_route_path, pkmn_version, custom_dvs=None, custom_ability=None, custom_nature=None):
        if base_route_path == const.EMPTY_ROUTE_NAME:
            base_route_path = None

        self._route_name = ""
        self._selected_ids = []
        try:
            self._data.new_route(solo_mon, base_route_path, pkmn_version=pkmn_version, custom_dvs=custom_dvs, custom_ability=custom_ability, custom_nature=custom_nature)
        except Exception as e:
            logger.error(f"Exception ocurred trying to copy route: {base_route_path}")
            logger.exception(e)
            # load an empty route, just in case
            self._data.new_route(solo_mon)
            raise e
        finally:
            self._on_name_change()
            self._on_version_change()
            self._on_event_selection()
            self._on_route_change()
    
    @handle_exceptions
    def load_route(self, full_path_to_route):
        try:
            _, route_name = os.path.split(full_path_to_route)
            route_name = os.path.splitext(route_name)[0]
            self._route_name = route_name

            self._data.load(full_path_to_route)
            self._selected_ids = []
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
            self._on_event_selection()
            self._on_route_change()
            self._unsaved_changes = False

    @handle_exceptions
    def customize_innate_stats(self, new_dvs, new_ability, new_nature):
        self._data.change_current_innate_stats(new_dvs, new_ability, new_nature)
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
    def new_event(self, event_def:EventDefinition, insert_after:int=None, insert_before:int=None, dest_folder_name=const.ROOT_FOLDER_NAME, do_select=True):
        result = self._data.add_event_object(event_def=event_def, insert_after=insert_after, insert_before=insert_before, dest_folder_name=dest_folder_name)
        self._on_route_change()
        if do_select:
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

    @handle_exceptions
    def set_route_filter_types(self, filter_options):
        self._route_filter_types = filter_options
        self._on_route_change()
        self._on_event_selection()

    @handle_exceptions
    def set_route_search(self, search):
        self._route_search = search
        self._on_route_change()
        self._on_event_selection()
    
    @handle_exceptions
    def load_all_custom_versions(self):
        gen_factory._gen_factory.reload_all_custom_gens()
    
    @handle_exceptions
    def create_custom_version(self, base_version, custom_version):
        gen_factory._gen_factory.get_specific_version(base_version).create_new_custom_gen(custom_version)
    
    def send_message(self, message):
        self._on_info_message(message)

    def trigger_exception(self, exception_message):
        self._on_exception(exception_message)

    def set_current_route_name(self, new_name) -> str:
        self._route_name = new_name
        self._on_name_change()

    ######
    # Methods that do not induce a state change
    ######

    def get_raw_route(self) -> routing.router.Router:
        return self._data

    def get_current_route_name(self) -> str:
        return self._route_name

    def get_preview_event(self):
        return self._current_preview_event

    def get_event_by_id(self, event_id) -> EventGroup:
        return self._data.get_event_obj(event_id)
    
    def has_errors(self):
        return self._data.root_folder.has_errors()
    
    def get_version(self):
        return self._data.pkmn_version
    
    def get_state_after(self, previous_event_id=None):
        if previous_event_id is None:
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
    
    def get_ability(self):
        return self._data.init_route_state.solo_pkmn.ability
    
    def get_nature(self):
        return self._data.init_route_state.solo_pkmn.nature
    
    def get_defeated_trainers(self):
        return self._data.defeated_trainers
    
    def get_route_search_string(self) -> str:
        if not self._route_search:
            return None
        return self._route_search
    
    def get_route_filter_types(self) -> List[str]:
        if len(self._route_filter_types) == 0:
            return None
        return self._route_filter_types
    
    def is_empty(self):
        return len(self._data.root_folder.children) == 0
    
    def is_valid_levelup_move(self, move_name, level):
        return self._data.is_valid_levelup_move(move_name, level)

    def has_unsaved_changes(self) -> routing.router.Router:
        return self._unsaved_changes
    
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
    
    def get_single_selected_event_obj(self, allow_event_items=True) -> EventGroup:
        return self.get_event_by_id(
            self.get_single_selected_event_id(allow_event_items=allow_event_items)
        )
    
    def get_active_state(self):
        # The idea here is we want to get the current state to operate on
        # MOST of the time, this is just the final state of the selected event
        # (since we will insert after the selected event)
        result = self.get_single_selected_event_obj(allow_event_items=False)
        if result is not None:
            return result.final_state
        
        # If no event is selected, because we are looking at an empty route
        # then just get the initial route state
        if self.is_empty():
            return self._data.init_route_state
        
        # If no event is selected, but the route is non-empty
        # then we will insert after the final event
        return self.get_final_state()

    
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
        try:
            self._fire_pre_save_hooks()
            self._data.save(route_name)
            self.send_message(f"Successfully saved route: {route_name}")
            self._unsaved_changes = False
        except Exception as e:
            self.trigger_exception(f"Couldn't save route due to exception! {type(e)}: {e}")
    
    def export_notes(self, route_name):
        out_path = self._data.export_notes(route_name)
        self.send_message(f"Exported notes to: {out_path}")
    
    def take_screenshot(self, image_name, bbox):
        try:
            if self.is_empty():
                return
            full_dir = os.path.join(const.SAVED_IMAGES_DIR, self.get_current_route_name())
            if not os.path.exists(full_dir):
                os.makedirs(full_dir)
            
            out_path = io_utils.get_safe_path_no_collision(full_dir, image_name, ext=".png")
            ImageGrab.grab(bbox=bbox).save(out_path)
            self.send_message(f"Saved screenshot to: {out_path}")
        except Exception as e:
            self.trigger_exception(f"Couldn't save screenshot due to exception! {type(e)}: {e}")

    def is_record_mode_active(self):
        return self._is_record_mode_active
    
    def get_move_idx(self, move_name, state=None):
        if state is None:
            state = self.get_final_state()
        
        move_idx = None
        move_name = sanitize_string(move_name)
        for cur_idx, cur_move in enumerate(state.solo_pkmn.move_list):
            if sanitize_string(cur_move) == move_name:
                move_idx = cur_idx
                break
        
        return move_idx
    
    def _walk_events_helper(self, cur_folder:EventFolder, cur_event_id:int, cur_event_found:bool, enabled_only:bool, walk_forward=True) -> Tuple[bool, EventGroup]:
        if walk_forward:
            iterable = cur_folder.children
        else:
            iterable = reversed(cur_folder.children)

        for test_obj in iterable:
            if isinstance(test_obj, EventGroup):
                if cur_event_found and test_obj.is_enabled():
                    return cur_event_found, test_obj
                elif test_obj.group_id == cur_event_id:
                    cur_event_found = True
            elif isinstance(test_obj, EventFolder):
                cur_event_found, prev_result = self._walk_events_helper(test_obj, cur_event_id, cur_event_found, enabled_only, walk_forward=walk_forward)
                if cur_event_found and prev_result is not None:
                    return cur_event_found, prev_result
            else:
                logger.error(f"Encountered unexpected types walking events: {type(test_obj)}")
        
        return cur_event_found, None
            
    def get_next_event(self, cur_event_id=None, enabled_only=False) -> EventGroup:
        return self._walk_events_helper(
            self._data.root_folder,
            cur_event_id,
            cur_event_id == None,
            True
        )[1]

    def get_previous_event(self, cur_event_id=None, enabled_only=False) -> EventGroup:
        return self._walk_events_helper(
            self._data.root_folder,
            cur_event_id,
            cur_event_id == None,
            enabled_only,
            walk_forward=False
        )[1]
