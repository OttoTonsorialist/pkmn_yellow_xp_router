from __future__ import annotations
import logging
from typing import List, Tuple

import controllers.main_controller
from route_recording.gamehook_client import GameHookClient
import routing.route_events
from utils.constants import const

logger = logging.getLogger(__name__)


def skip_if_inactive(controller_fn):
    # must wrap an instance method from the RecorderController class
    def wrapper(*args, **kwargs):
        obj:RecorderController = args[0]
        if obj._controller.is_record_mode_active():
            controller_fn(*args, **kwargs)
        else:
            logger.warning(f"Ignoring recorder function call due to recorder being inactive: {controller_fn} with args: {args} and kwargs: {kwargs}")
    
    return wrapper

class RecorderController:
    """
    Serves as a "translator" between the actual client reading 
    """
    def __init__(self, controller:controllers.main_controller.MainController):
        self._controller = controller
        self._status_events = []
        self._ready_events = []
        self._game_state_events = []
        self._status = None
        self._ready = None
        self._game_state = None

        # metadata for tracking/organizing events in the generated route
        self._potential_new_area_name = None
        self._potential_new_folder_name = None
        self._active_area_name = None
        self._active_folder_name = const.ROOT_FOLDER_NAME
    
    def register_recorder_status_change(self, tk_obj):
        new_event_name = const.EVENT_RECORDER_STATUS_CHANGE.format(len(self._status_events))
        self._status_events.append((tk_obj, new_event_name))
        return new_event_name
    
    def register_recorder_ready_change(self, tk_obj):
        new_event_name = const.EVENT_RECORDER_READY_CHANGE.format(len(self._ready_events))
        self._ready_events.append((tk_obj, new_event_name))
        return new_event_name
    
    def register_recorder_game_state_change(self, tk_obj):
        new_event_name = const.EVENT_RECORDER_GAME_STATE_CHANGE.format(len(self._game_state_events))
        self._game_state_events.append((tk_obj, new_event_name))
        return new_event_name
    
    def _on_status_change(self):
        for tk_obj, cur_event_name in self._status_events:
            tk_obj.event_generate(cur_event_name, when="tail")
    
    def _on_ready_change(self):
        for tk_obj, cur_event_name in self._ready_events:
            tk_obj.event_generate(cur_event_name, when="tail")
    
    def _on_game_state_change(self):
        for tk_obj, cur_event_name in self._game_state_events:
            tk_obj.event_generate(cur_event_name, when="tail")
    
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
    
    def set_game_state(self, new_val):
        self._game_state = new_val
        self._on_game_state_change()
    
    def get_game_state(self):
        return self._game_state
    
    def route_restarted(self):
        # this function is called when we detect that a new game-file has been started
        # silently allow this if we haven't actually recording any events
        # but otherwise, this is a problem. Complain, and abort
        if not self._controller.is_empty():
            # TODO: need to complain to the user somehow...
            self.set_ready(False)
    
    def _on_enable(self):
        self._potential_new_area_name = None
        self._potential_new_folder_name = None

        if not self._controller.is_empty():
            test_obj = self._controller.get_previous_event()
            self._active_folder_name = test_obj.parent.name
            self._active_area_name = self._extract_area_name_from_folder_name(self._active_folder_name)
        else:
            self._active_folder_name = const.ROOT_FOLDER_NAME
            self._active_area_name = None

    @skip_if_inactive
    def entered_new_area(self, new_area_name):
        self._potential_new_area_name = new_area_name
        folder_name = new_area_name
        counter = 1
        while folder_name in self._controller.get_all_folder_names():
            counter += 1
            folder_name = f"{new_area_name}: Trip {counter}"

        self._potential_new_folder_name = folder_name
    
    def _extract_area_name_from_folder_name(self, folder_name:str):
        test = folder_name.split(":")
        if len(test) == 2 and "Trip" in test[1]:
            return test[0]
        return folder_name

    @skip_if_inactive
    def game_reset(self):
        to_delete = []

        # find the save points
        test_obj:routing.route_events.EventGroup = self._controller.get_previous_event()
        while test_obj is not None and test_obj.event_definition.save is None:
            to_delete.append(test_obj.group_id)
            test_obj = self._controller.get_previous_event(test_obj.group_id)

        logger.info(f"Cleaning up {len(to_delete)} events for reset")
        self._controller.delete_events(to_delete)
        self._controller.purge_empty_folders()

        if test_obj is not None:
            self._active_folder_name = test_obj.parent.name
            self._active_area_name = self._extract_area_name_from_folder_name(self._active_folder_name)
        else:
            self._active_folder_name = const.ROOT_FOLDER_NAME
            self._active_area_name = None
        self._potential_new_area_name = None
        self._potential_new_folder_name = None

    def is_trainer_event(self, event_obj:routing.route_events.EventGroup, trainer_name:str):
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
            while not self.is_trainer_event(test_obj, trainer_name):
                if test_obj is None:
                    break
                test_obj = self._controller.get_previous_event(test_obj.group_id)
            
            if test_obj is None:
                msg = f"{const.RECORDING_ERROR_FRAGMENT} Could not find trainer event {trainer_name} to remove after losing to them"
                logger.error(msg)
                self._controller.new_event(routing.route_events.EventDefinition(notes=msg), dest_folder_name=self._active_folder_name)
            else:
                if test_obj != last_obj:
                    logger.error(f"{const.RECORDING_ERROR_FRAGMENT} When removing trainer event {trainer_name}, it was not the last event... odd")

                self._controller.delete_events([test_obj.group_id])

    @skip_if_inactive
    def add_event(self, event_def:routing.route_events.EventDefinition):
        if self._potential_new_area_name is not None:
            if self._active_area_name == self._potential_new_area_name:
                self._potential_new_area_name = None
                self._potential_new_folder_name = None
            else:
                self._active_area_name = self._potential_new_area_name
                self._active_folder_name = self._potential_new_folder_name
                self._potential_new_area_name = None
                self._potential_new_folder_name = None
                self._controller.finalize_new_folder(self._active_folder_name)
        
        if self._active_folder_name not in self._controller.get_all_folder_names():
            self._controller.finalize_new_folder(self._active_folder_name)

        if event_def.trainer_def is not None and event_def.trainer_def.trainer_name in self._controller.get_defeated_trainers():
            # log any errors for duplicate trainers being defeated
            msg = f"{const.RECORDING_ERROR_FRAGMENT} Tried to fight trainer that has already been defeated: {event_def.trainer_def.trainer_name}"
            logger.error(msg)
            self._controller.new_event(
                routing.route_events.EventDefinition(notes=msg),
                dest_folder_name=self._active_folder_name
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
                        routing.route_events.EventDefinition(notes=msg),
                        dest_folder_name=self._active_folder_name
                    )
                    return
                
                event_def.learn_move.destination = delete_idx
            if event_def.learn_move.source == const.MOVE_SOURCE_LEVELUP:
                self._controller.update_levelup_move(event_def.learn_move)
                return
        elif None is not event_def.item_event_def:
            last_event = self._controller.get_previous_event()
            if (
                last_event is not None and
                last_event.event_definition.item_event_def is not None and
                last_event.event_definition.item_event_def.item_name == event_def.item_event_def.item_name and
                last_event.event_definition.item_event_def.is_acquire == event_def.item_event_def.is_acquire and
                last_event.event_definition.item_event_def.with_money == event_def.item_event_def.with_money and
                last_event.parent.name == self._active_folder_name
            ):
                event_def.item_event_def.item_amount += last_event.event_definition.item_event_def.item_amount
                self._controller.update_existing_event(last_event.group_id, event_def)
                return
        elif None is not event_def.vitamin:
            last_event = self._controller.get_previous_event()
            if (
                last_event is not None and
                last_event.event_definition.vitamin is not None and
                last_event.event_definition.vitamin.vitamin == event_def.vitamin.vitamin and
                last_event.parent.name == self._active_folder_name
            ):
                event_def.vitamin.amount += last_event.event_definition.vitamin.amount
                self._controller.update_existing_event(last_event.group_id, event_def)
                return
        elif None is not event_def.rare_candy:
            last_event = self._controller.get_previous_event()
            if (
                last_event is not None and
                last_event.event_definition.rare_candy is not None and
                last_event.parent.name == self._active_folder_name
            ):
                event_def.rare_candy.amount += last_event.event_definition.rare_candy.amount
                self._controller.update_existing_event(last_event.group_id, event_def)
                return

        self._controller.new_event(event_def, dest_folder_name=self._active_folder_name)


class RecorderGameHookClient(GameHookClient):
    def __init__(self, controller:RecorderController, expected_names:List[str]):
        # TODO: use a config value for gamehook url so that users can configure if needed
        super().__init__(clear_callbacks_on_load=True)
        self._controller = controller
        self._expected_names = expected_names
    
    def on_mapper_loaded(self):
        game_name = self.meta.get("gameName")

        correct_mapper_loaded = False
        for test in self._expected_names:
            if test in game_name:
                correct_mapper_loaded = True
                break

        logger.info(f"Successfully loaded mapper. Got gameName: {game_name}, to be validated against: {self._expected_names} (result: {correct_mapper_loaded})")
        if correct_mapper_loaded:
            self._controller.set_ready(True)
            self._controller.set_status(const.RECORDING_STATUS_READY)
        else:
            self._controller.set_ready(False)
            self._controller.set_status(const.RECORDING_STATUS_WRONG_MAPPER)
    
    def validate_constants(self, constants):
        real_vals = [x for x in self.properties.keys()]
        lower_vals = [x.lower() for x in real_vals]

        invalid_props = set()
        for cur_attr in dir(constants):
            if 'KEY' not in cur_attr:
                continue

            cur_val = getattr(constants, cur_attr)
            if isinstance(cur_val, str):
                if cur_val in self.properties:
                    continue
                if cur_val.lower() in lower_vals:
                    setattr(constants, cur_attr, real_vals[lower_vals.index(cur_val.lower())])
                    continue
                invalid_props.add(cur_val)
            elif isinstance(cur_val, list):
                for inner_idx, inner_val in enumerate(cur_val):
                    if not isinstance(inner_val, str):
                        continue
                    if inner_val in self.properties:
                        continue
                    if inner_val.lower() in lower_vals:
                        cur_val[inner_idx] = real_vals[lower_vals.index(inner_val.lower())]
                        continue
                    invalid_props.add(inner_val)
            elif isinstance(cur_val, set):
                replacement_val = set()
                is_replacement_needed = False
                for inner_val in cur_val:
                    if not isinstance(inner_val, str):
                        replacement_val.add(inner_val)
                        continue
                    if inner_val in self.properties:
                        replacement_val.add(inner_val)
                        continue
                    if inner_val.lower() in lower_vals:
                        replacement_val.add(real_vals[lower_vals.index(inner_val.lower())])
                        is_replacement_needed = True
                        continue
                    invalid_props.add(inner_val)
                
                if is_replacement_needed:
                    setattr(constants, cur_attr, replacement_val)
        
        if invalid_props:
            return list(invalid_props)

        logger.info("Validated GameHook constants successfully")
        return []


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
