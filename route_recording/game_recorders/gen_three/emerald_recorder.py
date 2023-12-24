from __future__ import annotations
import logging
from typing import List
from route_recording.game_recorders.gen_three.emerald_fsm import Machine

import route_recording.recorder
from route_recording.game_recorders.gen_three import emerald_states
from route_recording.game_recorders.gen_three.emerald_gamehook_constants import gh_gen_three_const, GameHookConstantConverter
from utils.constants import const

logger = logging.getLogger(__name__)


class EmeraldRecorder(route_recording.recorder.RecorderGameHookClient):
    def __init__(self, controller:route_recording.recorder.RecorderGameHookClient, expected_names:List[str]):
        super().__init__(controller, expected_names)

        self._machine = Machine(controller, self, GameHookConstantConverter())

        """
        self._machine.register(emerald_states.WatchState(self._machine))

        """
        self._machine.register(emerald_states.UninitializedState(self._machine))
        self._machine.register(emerald_states.ResettingState(self._machine))
        self._machine.register(emerald_states.BattleState(self._machine))
        self._machine.register(emerald_states.InventoryChangeState(self._machine))
        self._machine.register(emerald_states.UseRareCandyState(self._machine))
        self._machine.register(emerald_states.UseTMState(self._machine))
        self._machine.register(emerald_states.MoveDeleteState(self._machine))
        self._machine.register(emerald_states.UseVitaminState(self._machine))
        self._machine.register(emerald_states.OverworldState(self._machine))
    
    def on_mapper_loaded(self):
        result = super().on_mapper_loaded()

        if self._controller.is_ready():
            self.validate_constants(gh_gen_three_const)
            for cur_key in gh_gen_three_const.ALL_KEYS_TO_REGISTER:
                self.get(cur_key).change(self._machine.handle_event)

            if not self._machine._active:
                self._machine.startup()

        return result
    
    def disconnect(self):
        result = super().disconnect()
        self._machine.shutdown()
        return result
