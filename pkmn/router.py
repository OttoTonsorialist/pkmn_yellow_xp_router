import os
import json
from typing import Tuple

from utils.constants import const
from pkmn import data_objects
from pkmn import pkmn_db
from utils import io_utils
from pkmn import route_events
from pkmn import route_state_objects


class Router:
    def __init__(self):
        self.init_route_state = None
        self.all_events = []
        self.defeated_trainers = set()
    
    def _reset_events(self):
        self.all_events = []
        self.defeated_trainers = set()

    def _get_event_group_info(self, event_group_id) -> Tuple[route_events.EventGroup, int]:
        for idx, cur_event in enumerate(self.all_events):
            if cur_event.group_id == event_group_id:
                return cur_event, idx
        
        return None, None
    
    def get_post_event_state(self, group_id):
        group_event = self._get_event_group_info(group_id)[0]
        if group_event is None:
            return None
        return group_event.final_state
    
    def get_final_state(self):
        if len(self.all_events):
            return self.all_events[-1].final_state
        return self.init_route_state
    
    def set_solo_pkmn(self, pkmn_name):
        pkmn_base = pkmn_db.pkmn_db.data.get(pkmn_name)
        if pkmn_base is None:
            raise ValueError(f"Could not find base stats for Pokemon: {pkmn_name}")
        
        self.init_route_state = route_state_objects.RouteState(
            route_state_objects.SoloPokemon(pkmn_name, pkmn_base),
            route_state_objects.BadgeList(),
            route_state_objects.Inventory()
        )
        self._reset_events()

    def _recalc_from(self, start_idx):
        # dumb, but it's ultimately easier to just forcibly recalc the entire list
        # instead of worrying about only starting from the exact right place
        # TODO: only recalc what's necessary
        start_idx = 0
        for recalc_idx in range(start_idx, len(self.all_events)):
            if recalc_idx == 0:
                prev_state = self.init_route_state
            else:
                prev_state = self.all_events[recalc_idx - 1].final_state

            self.all_events[recalc_idx].apply(prev_state)
    
    def refresh_existing_routes(self):
        result = []
        if os.path.exists(const.SAVED_ROUTES_DIR):
            for fragment in os.listdir(const.SAVED_ROUTES_DIR):
                name, ext = os.path.splitext(fragment)
                if ext != ".json":
                    continue
                result.append(name)
        
        return result
    
    def add_event(self, event_def, insert_before=None):
        if not self.init_route_state:
            raise ValueError("Cannot add an event when solo pokmn is not yet selected")
        if event_def.trainer_name:
            self.defeated_trainers.add(event_def.trainer_name)

        if insert_before is None:
            init_pkmn = self.get_final_state()
            insert_idx = None
        else:
            insert_idx = self._get_event_group_info(insert_before)[1]
            if insert_idx == 0:
                init_pkmn = self.init_route_state
            else:
                init_pkmn = self.all_events[insert_idx-1].final_state

        new_event = route_events.EventGroup(init_pkmn, event_def)

        if insert_before is None:
            self.all_events.append(new_event)
        else:
            self.all_events.insert(insert_idx, new_event)
            self._recalc_from(max(insert_idx - 1, 0))
    
    def bulk_fight_trainers(self, trainer_name_list):
        self._reset_events()
        for trainer_name in trainer_name_list:
            self.add_event(route_events.EventDefinition(trainer_name=trainer_name))
    
    def remove_group(self, group_id):
        group_obj, group_idx = self._get_event_group_info(group_id)
        if group_obj.event_definition.trainer_name is not None:
            self.defeated_trainers.remove(group_obj.event_definition.trainer_name)
        del self.all_events[group_idx]
        self._recalc_from(group_idx)

    def move_group(self, group_id, move_up):
        group_obj, group_idx = self._get_event_group_info(group_id)
        if group_obj is None:
            raise ValueError(f"No group found with group_id: {group_id}")

        if move_up:
            insert_idx = max(group_idx - 1, 0)
        else:
            insert_idx = min(group_idx + 1, len(self.all_events) - 1)
        
        self.all_events.remove(group_obj)
        self.all_events.insert(insert_idx, group_obj)
        self._recalc_from(insert_idx)

    def save(self, name):
        if not os.path.exists(const.SAVED_ROUTES_DIR):
            os.mkdir(const.SAVED_ROUTES_DIR)

        final_path = os.path.join(const.SAVED_ROUTES_DIR, f"{name}.json")
        io_utils.backup_file_if_exists(final_path)

        with open(final_path, 'w') as f:
            json.dump({
                const.EVENT_ID_COUNTER: route_events.event_id_counter,
                const.NAME_KEY: self.init_route_state.solo_pkmn.name,
                const.EVENTS: [x.to_dict() for x in self.all_events]
            }, f, indent=4)
    
    def load_min_battle(self, name):
        final_path = os.path.join(const.MIN_BATTLES_DIR, f"{name}.json")

        with open(final_path, 'r') as f:
            result = json.load(f)
        
        route_events.event_id_counter = result[const.EVENT_ID_COUNTER]
        # kinda weird, but just reset to same mon to trigger cleanup in helper function
        self.set_solo_pkmn(self.init_route_state.solo_pkmn.name)
        for cur_event in result[const.EVENTS]:
            self.add_event(route_events.EventDefinition.deserialize(cur_event))
    
    def load(self, name):
        final_path = os.path.join(const.SAVED_ROUTES_DIR, f"{name}.json")

        with open(final_path, 'r') as f:
            result = json.load(f)
        
        route_events.event_id_counter = result[const.EVENT_ID_COUNTER]
        self.set_solo_pkmn(result[const.NAME_KEY])
        for cur_event in result[const.EVENTS]:
            self.add_event(route_events.EventDefinition.deserialize(cur_event))
