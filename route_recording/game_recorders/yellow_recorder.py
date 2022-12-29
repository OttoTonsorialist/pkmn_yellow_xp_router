from __future__ import annotations
import logging
from route_recording.game_recorders.yellow_fsm import Machine

import route_recording.recorder
import route_recording.game_recorders.yellow_states
from route_recording.game_recorders.yellow_gamehook_constants import gh_gen_one_const, gh_converter
from utils.constants import const

logger = logging.getLogger(__name__)


class YellowRecorder(route_recording.recorder.RecorderGameHookClient):
    def __init__(self, controller:route_recording.recorder.RecorderGameHookClient, expected_name:str):
        super().__init__(controller, expected_name)

        self._machine = Machine(controller, self)
        self._machine.register(route_recording.game_recorders.yellow_states.UninitializedState(self._machine))
        self._machine.register(route_recording.game_recorders.yellow_states.ResettingState(self._machine))
        self._machine.register(route_recording.game_recorders.yellow_states.BattleState(self._machine))
        self._machine.register(route_recording.game_recorders.yellow_states.ItemGainState(self._machine))
        self._machine.register(route_recording.game_recorders.yellow_states.ItemLoseState(self._machine))
        self._machine.register(route_recording.game_recorders.yellow_states.UseRareCandyState(self._machine))
        self._machine.register(route_recording.game_recorders.yellow_states.UseTMState(self._machine))
        self._machine.register(route_recording.game_recorders.yellow_states.UseVitaminState(self._machine))
        self._machine.register(route_recording.game_recorders.yellow_states.OverworldState(self._machine))
    
    def on_mapper_loaded(self):
        result = super().on_mapper_loaded()

        for cur_key in gh_gen_one_const.ALL_KEYS_TO_REGISTER:
            self.get(cur_key).change(self._machine.handle_event)

        if not self._machine._active:
            self._machine.startup()

        return result
    
    def disconnect(self):
        result = super().disconnect()
        self._machine.shutdown()
        return result
