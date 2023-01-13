import logging

import tkinter as tk
from controllers.main_controller import MainController

from gui import custom_components
from route_recording.recorder import RecorderController, RecorderGameHookClient
from utils.constants import const
from pkmn.gen_factory import current_gen_info

logger = logging.getLogger(__name__)


class RecorderStatus(tk.Frame):
    def __init__(self, main_controller:MainController, recorder_controller:RecorderController, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._main_controller = main_controller
        self._recorder_controller = recorder_controller
        self._gamehook_client:RecorderGameHookClient = None
        self._gamehook_translator = None

        self.client_status_label = tk.Label(self, text="Client Status: None", justify=tk.LEFT)
        self.client_status_label.pack()

        self.recorder_ready_label = tk.Label(self, text="Recording Status: Inactive", justify=tk.LEFT)
        self.recorder_ready_label.pack()

        self.game_state_label = tk.Label(self, text="Game State: None", justify=tk.LEFT)
        self.game_state_label.pack()

        self.connection_retry_button = custom_components.SimpleButton(self, text="Reconnect to GameHook", justify=tk.LEFT, command=self.reconnect_button_pressed)
        self.connection_retry_button.disable()
        self.connection_retry_button.pack()

        self.bind(self._main_controller.register_record_mode_change(self), self.on_recording_mode_changed)
        self.bind(self._recorder_controller.register_recorder_status_change(self), self.on_recording_status_changed)
        self.bind(self._recorder_controller.register_recorder_ready_change(self), self.on_recording_ready_changed)
        self.bind(self._recorder_controller.register_recorder_game_state_change(self), self.on_recording_game_state_changed)
    
    def on_recording_mode_changed(self, *args, **kwargs):
        if self._main_controller.is_record_mode_active():
            if self._gamehook_client is not None:
                logger.warning("Recording mode set to active, but gamehook client was already active")
                return
            
            self.client_status_label.configure(text="Client Status: Connecting...")
            try:
                self._gamehook_client = current_gen_info().get_recorder_client(self._recorder_controller)
                self._gamehook_client.connect()
            except NotImplementedError as e:
                self.client_status_label.configure(text="No recorder has been created yet for the current version")
                self.connection_retry_button.disable()
            except Exception as e:
                logger.error("General exception trying to create and connect gamehook client")
                logger.exception(e)
                self.client_status_label.configure(text=f"Exception encountered trying to connect to gamehook: {type(e)}. Check logs for more details")
        else:
            if self._gamehook_client is not None:
                self._gamehook_client.disconnect()
                self._gamehook_client = None
    
    def on_recording_status_changed(self, *args, **kwargs):
        self.client_status_label.configure(text=f"Client Status: {self._recorder_controller.get_status()}")
        if self._recorder_controller.get_status() == const.RECORDING_STATUS_DISCONNECTED:
            self.connection_retry_button.enable()

    def on_recording_game_state_changed(self, *args, **kwargs):
        self.game_state_label.configure(text=f"Game State: {self._recorder_controller.get_game_state()}")
    
    def on_recording_ready_changed(self, *args, **kwargs):
        if self._recorder_controller.is_ready():
            self.recorder_ready_label.configure(text=f"Recording Status: Active")
            self.connection_retry_button.disable()
        else:
            self.recorder_ready_label.configure(text=f"Recording Status: Inactive")
            self.connection_retry_button.enable()
    
    def reconnect_button_pressed(self, *args, **kwargs):
        if self._gamehook_client is not None:
            self._gamehook_client.connect()
    