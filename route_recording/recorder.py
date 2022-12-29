from __future__ import annotations
import logging
from typing import List, Tuple

import controllers.main_controller
from route_recording.gamehook_client import GameHookClient
from routing.route_events import BlackoutEventDefinition, EventDefinition, EventGroup, InventoryEventDefinition, LearnMoveEventDefinition, RareCandyEventDefinition, TrainerEventDefinition, VitaminEventDefinition, WildPkmnEventDefinition
from utils.constants import const

logger = logging.getLogger(__name__)


def skip_if_inactive(controller_fn):
    # must wrap an instance method from the RecorderController class
    def wrapper(*args, **kwargs):
        obj:RecorderController = args[0]
        if obj._controller.is_record_mode_active():
            controller_fn(*args, **kwargs)
        else:
            logger.warning(f"Ignoring translator function call due to recorder being inactive: {controller_fn} with args: {args} and kwargs: {kwargs}")
    
    return wrapper

class RecorderController:
    """
    Serves as a "translator" between the actual client reading 
    """
    def __init__(self, controller:controllers.main_controller.MainController):
        self._controller = controller
        self._status_callbacks = []
        self._ready_callbacks = []
        self._status = None
        self._ready = None

        # metadata for tracking/organizing events in the generated route
        self._potential_new_area_name = None
        self._potential_new_folder_name = None
        self._active_area_name = None
        self._active_folder_name = const.ROOT_FOLDER_NAME
        self._last_save_point_id = None
        self._last_save_folder_name = const.ROOT_FOLDER_NAME
        self._last_save_area_name = None
    
    def register_recorder_status_change(self, callback_fn):
        self._status_callbacks.append(callback_fn)
    
    def register_recorder_ready_change(self, callback_fn):
        self._ready_callbacks.append(callback_fn)
    
    def _on_status_change(self):
        for cur_callback in self._status_callbacks:
            try:
                cur_callback()
            except Exception as e:
                logger.error(f"Exception encountered during record status callbacks")
                logger.exception(e)
    
    def _on_ready_change(self):
        for cur_callback in self._ready_callbacks:
            try:
                cur_callback()
            except Exception as e:
                logger.error(f"Exception encountered during record ready callbacks")
                logger.exception(e)
    
    def set_status(self, new_val):
        self._status = new_val
        self._on_status_change()
    
    def get_status(self):
        return self._status
    
    def set_ready(self, new_val):
        self._ready = new_val
        self._on_ready_change()
    
    def is_ready(self):
        return self._ready
    
    def route_restarted(self):
        # this function is called when we detect that a new game-file has been started
        # silently allow this if we haven't actually recording any events
        # but otherwise, this is a problem. Complain, and abort
        if not self._controller.is_empty():
            # TODO: need to complain to the user somehow...
            self.set_ready(False)
    
    def _on_enable(self):
        # For now, when translator gets re-enabled, we're just going to default back to writing to the root folder initially
        self._active_area_name = None
        self._active_folder_name = const.ROOT_FOLDER_NAME

        self._last_save_point_id = None
        self._last_save_folder_name = const.ROOT_FOLDER_NAME
        self._last_save_area_name = None

        if not self._controller.is_empty():
            last_obj = test_obj = self._controller.get_previous_event()
            while test_obj.event_definition.save is None:
                if test_obj is None:
                    break
                test_obj = self._controller.get_previous_event(test_obj.group_id)
            
            if test_obj is not None:
                self._last_save_point_id = test_obj.group_id
                self._last_save_folder_name = test_obj.parent.name
                # TODO: can we do anything about this..?
                self._last_save_area_name = None

    @skip_if_inactive
    def entered_new_area(self, new_area_name):
        self._potential_new_area_name = new_area_name
        folder_name = new_area_name
        counter = 1
        while folder_name in self._controller.get_all_folder_names():
            counter += 1
            folder_name = f"{new_area_name}: Trip {counter}"

        self._potential_new_folder_name = folder_name

    @skip_if_inactive
    def game_reset(self):
        if self._last_save_point_id is None:
            # just double check, look for save point if possible
            test_obj:EventGroup = self._controller.get_previous_event()
            while test_obj is not None and test_obj.event_definition.save is None:
                test_obj = self._controller.get_previous_event(test_obj.group_id)
            
            if test_obj is not None:
                self._last_save_point_id = test_obj.group_id

        if self._last_save_point_id is None:
            # if no last save point is defined, just nuking everything
            to_delete = [x.group_id for x in self._controller.get_raw_route().root_folder.children]
        else:
            # Delete every event after the last save point
            # and then bubble up one level in the folders, to delete all the subsequent folders/events
            # Do this until we get to the top
            to_delete = []
            cur_split_point = self._controller.get_event_by_id(self._last_save_point_id)
            parent_obj = cur_split_point.parent
            while True:
                if parent_obj is None:
                    break
                if parent_obj.children[0] != cur_split_point:
                    past_split_point = False
                    for other_child in parent_obj.children:
                        if past_split_point:
                            to_delete.append(other_child.group_id)
                        elif other_child == cur_split_point:
                            past_split_point = True

                cur_split_point = parent_obj
                parent_obj = cur_split_point.parent
        
        self._controller.delete_events(to_delete)
        self._active_folder_name = self._last_save_folder_name
        self._active_area_name = self._last_save_area_name
        self._potential_new_area_name = None
        self._potential_new_folder_name = None

    def _is_trainer_event(self, event_obj:EventGroup, trainer_name:str):
        return (
            event_obj is not None and
            event_obj.event_definition.trainer_def is not None and
            event_obj.event_definition.trainer_def.trainer_name == trainer_name
        )

    @skip_if_inactive
    def lost_trainer_battle(self, trainer_name):
        # If we initiate a trainer battle, lose to that trainer, and _don't_ reset
        # Need to remove the event representing that trainer fight
        if trainer_name not in self._controller.get_defeated_trainers():
            logger.error(f"{const.RECORDING_ERROR_FRAGMENT} Lost trainer battle to trainer {trainer_name}, but no matching trainer event was found to remove")
        else:
            last_obj = test_obj = self._controller.get_previous_event()
            while not self._is_trainer_event(test_obj, trainer_name):
                if test_obj is None:
                    break
                test_obj = self._controller.get_previous_event(test_obj.group_id)
            
            if test_obj is None:
                msg = f"{const.RECORDING_ERROR_FRAGMENT} Could not find trainer event {trainer_name} to remove after losing to them"
                logger.error(msg)
                self._controller.new_event(EventDefinition(notes=msg), dest_folder_name=self._active_folder_name)
            else:
                if test_obj != last_obj:
                    logger.error(f"{const.RECORDING_ERROR_FRAGMENT} When removing trainer event {trainer_name}, it was not the last event... odd")

                self._controller.delete_events([test_obj.group_id])

    @skip_if_inactive
    def add_event(self, event_def:EventDefinition):
        logger.info("adding event from recorder")
        if self._potential_new_area_name is not None:
            if self._active_area_name == self._potential_new_area_name:
                self._potential_new_area_name = None
                self._potential_new_folder_name = None
            else:
                self._active_area_name = self._potential_new_area_name
                self._active_folder_name = self._potential_new_folder_name
                self._potential_new_area_name = None
                self._potential_new_folder_name = None
                logger.info("adding new folder")
                self._controller.finalize_new_folder(self._active_folder_name)
                logger.info("new folder added")

        logger.info("Folders updated")
        if event_def.trainer_def is not None and event_def.trainer_def.trainer_name in self._controller.get_defeated_trainers():
            # log any errors for duplicate trainers being defeated
            msg = f"{const.RECORDING_ERROR_FRAGMENT} Tried to fight trainer that has already been defeated: {event_def.trainer_def.trainer_name}"
            logger.error(msg)
            self._controller.new_event(
                EventDefinition(notes=msg),
                dest_folder_name=self._active_folder_name,
                auto_select=True
            )
            return
        elif None is not event_def.learn_move:
            # if we are updating a levelup move, will need to extract the override (when appropriate) and then do an update, instead of new event
            if event_def.learn_move.destination is not None:
                delete_idx = self._controller.get_move_idx(event_def.learn_move.destination)
                if delete_idx is None:
                    msg = f"{const.RECORDING_ERROR_FRAGMENT} When teaching level-up move {event_def} over {event_def.learn_move.destination}, Mon didn't have {event_def.learn_move.destination}"
                    logger.error(msg)
                    self._controller.new_event(
                        EventDefinition(notes=msg),
                        dest_folder_name=self._active_folder_name,
                        auto_select=True
                    )
                    return
                
                event_def.learn_move.destination = delete_idx
            if event_def.learn_move.source == const.MOVE_SOURCE_LEVELUP:
                self._controller.update_levelup_move(event_def.learn_move)
                return
        elif event_def.save is not None:
            self._last_save_folder_name = self._active_folder_name
            self._last_save_area_name = self._active_area_name

        logger.info(f"Event validation finished, adding event {event_def} to folder {self._active_folder_name}")
        new_event_id = self._controller.new_event(event_def, dest_folder_name=self._active_folder_name, auto_select=True)
        logger.info(f"Event added")

        if event_def.save is not None:
            self._last_save_point_id = new_event_id


class RecorderGameHookClient(GameHookClient):
    def __init__(self, controller:RecorderController, expected_name:str):
        # TODO: use a config value for gamehook url so that users can configure if needed
        super().__init__(clear_callbacks_on_load=True)
        self._controller = controller
        self._expected_name = expected_name
    
    def on_mapper_loaded(self):
        game_name = self.meta.get("gameName")
        logger.info(f"Successfully loaded mapper. Got gameName: {game_name}, to be validated against: {self._expected_name} (result: {game_name == self._expected_name})")
        if game_name == self._expected_name:
            self._controller.set_ready(True)
            self._controller.set_status(const.RECORDING_STATUS_READY)
        else:
            self._controller.set_ready(False)
            self._controller.set_status(const.RECORDING_STATUS_WRONG_MAPPER)

    def on_mapper_load_error(self, err):
        self._controller.set_ready(False)
        self._controller.set_status(const.RECORDING_STATUS_NO_MAPPER)
    
    def on_disconnected(self):
        self._controller.set_ready(False)
        self._controller.set_status(const.RECORDING_STATUS_DISCONNECTED)
    
    def on_connected(self):
        self._controller.set_ready(False)
        self._controller.set_status(const.RECORDING_STATUS_CONNECTED)
    
    def on_connection_error(self):
        self._controller.set_ready(False)
        self._controller.set_status(const.RECORDING_STATUS_FAILED_CONNECTION)
