from __future__ import annotations
import logging
from typing import List
from route_recording.game_recorders.gen_two.crystal_fsm import Machine

import route_recording.recorder
import route_recording.game_recorders.gen_two.crystal_states
from route_recording.game_recorders.gen_two.crystal_gamehook_constants import gh_gen_two_const, GameHookConstantConverter
from utils.constants import const

logger = logging.getLogger(__name__)


class CrystalRecorder(route_recording.recorder.RecorderGameHookClient):
    def __init__(self, controller:route_recording.recorder.RecorderGameHookClient, expected_names:List[str]):
        super().__init__(controller, expected_names)

        self._machine = Machine(controller, self, GameHookConstantConverter())
        """
        self._machine.register(route_recording.game_recorders.gen_two.crystal_states.WatchState(self._machine))
        """
        self._machine.register(route_recording.game_recorders.gen_two.crystal_states.UninitializedState(self._machine))
        self._machine.register(route_recording.game_recorders.gen_two.crystal_states.ResettingState(self._machine))
        self._machine.register(route_recording.game_recorders.gen_two.crystal_states.BattleState(self._machine))
        self._machine.register(route_recording.game_recorders.gen_two.crystal_states.InventoryChangeState(self._machine))
        self._machine.register(route_recording.game_recorders.gen_two.crystal_states.UseRareCandyState(self._machine))
        self._machine.register(route_recording.game_recorders.gen_two.crystal_states.UseTMState(self._machine))
        self._machine.register(route_recording.game_recorders.gen_two.crystal_states.MoveDeleteState(self._machine))
        self._machine.register(route_recording.game_recorders.gen_two.crystal_states.UseVitaminState(self._machine))
        self._machine.register(route_recording.game_recorders.gen_two.crystal_states.OverworldState(self._machine))
    
    def on_mapper_loaded(self):
        result = super().on_mapper_loaded()

        if self._controller.is_ready():
            gh_gen_two_const.use_new_mapper()
            invalid_props = self.validate_constants(gh_gen_two_const)
            if invalid_props:
                gh_gen_two_const.use_old_mapper()
                invalid_props = self.validate_constants(gh_gen_two_const)
                if invalid_props:
                    logger.error(f"Likely due to mismatching GameHook version, invalid GameHook properties: {list(invalid_props)}")
                    self._controller._controller.trigger_exception(f"Likely due to mismatching GameHook version, invalid GameHook properties: {list(invalid_props)}")

            for cur_key in gh_gen_two_const.ALL_KEYS_TO_REGISTER:
                self.get(cur_key).change(self._machine.handle_event)

            if not self._machine._active:
                self._machine.startup()

        return result
    
    def disconnect(self):
        result = super().disconnect()
        self._machine.shutdown()
        return result
