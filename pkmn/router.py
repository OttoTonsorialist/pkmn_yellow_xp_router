import os
import json
from tokenize import group
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
        self.event_folders = []
        self.folder_idx_lookup = {}
        self.level_up_move_defs = {}
        self.defeated_trainers = set()
    
    def _reset_events(self):
        self.event_folders = []
        self.folder_idx_lookup = {}
        self.defeated_trainers = set()
    
    def get_event_obj(self, event_id):
        for cur_folder in self.event_folders:
            if cur_folder.group_id == event_id:
                return cur_folder
            for cur_group in cur_folder.event_groups:
                if cur_group.group_id == event_id:
                    return cur_group
                for cur_item in cur_group.event_items:
                    if cur_item.group_id == event_id:
                        return cur_item
        
        return None

    def get_folder_name_for_event(self, event_id):
        for cur_folder in self.event_folders:
            if cur_folder.group_id == event_id:
                return cur_folder.name
            for cur_group in cur_folder.event_groups:
                if cur_group.group_id == event_id:
                    return cur_folder.name
                for cur_item in cur_group.event_items:
                    if cur_item.group_id == event_id:
                        return cur_folder.name
        
        return None
        
    def _get_event_folder_info(self, event_group_id) -> Tuple[route_events.EventFolder, int]:
        for fdx, cur_folder in enumerate(self.event_folders):
            if cur_folder.group_id == event_group_id:
                return cur_folder, fdx
        
        return None, None

    def _get_event_group_info(self, event_group_id) -> Tuple[route_events.EventGroup, int, int]:
        for fdx, cur_folder in enumerate(self.event_folders):
            for idx, cur_event in enumerate(cur_folder.event_groups):
                if cur_event.group_id == event_group_id:
                    return cur_event, fdx, idx
        
        return None, None, None
    
    def get_post_event_state(self, group_id):
        group_event = self._get_event_group_info(group_id)[0]
        if group_event is None:
            return None
        return group_event.final_state
    
    def get_final_state(self):
        if len(self.event_folders):
            return self.event_folders[-1].final_state
        return self.init_route_state
    
    def set_solo_pkmn(self, pkmn_name, level_up_moves=None):
        pkmn_base = pkmn_db.pkmn_db.get_pkmn(pkmn_name)
        if pkmn_base is None:
            raise ValueError(f"Could not find base stats for Pokemon: {pkmn_name}")
        
        self.init_route_state = route_state_objects.RouteState(
            route_state_objects.SoloPokemon(pkmn_name, pkmn_base),
            route_state_objects.BadgeList(),
            route_state_objects.Inventory()
        )

        if level_up_moves is None:
            self.level_up_move_defs = {
                int(x[0]): route_events.LearnMoveEventDefinition(x[1], None, const.MOVE_SOURCE_LEVELUP, level=int(x[0]))
                for x in pkmn_base.levelup_moves
            }
        else:
            self.level_up_move_defs = {x.level: x for x in level_up_moves}

        self._recalc()
    
    def _recalc(self):
        # dumb, but it's ultimately easier to just forcibly recalc the entire list
        # instead of worrying about only starting from the exact right place
        # TODO: only recalc what's necessary, based on a passed-in index
        cur_state = self.init_route_state
        for cur_folder in self.event_folders:
            cur_folder.child_errors = False
            cur_folder.init_state = cur_state
            for cur_group in cur_folder.event_groups:
                self._calc_single_event(cur_group, cur_state)
                if cur_group.error_messages:
                    cur_folder.child_errors = True
                cur_state = cur_group.final_state
            cur_folder.final_state = cur_state

    def _calc_single_event(self, event_group, prev_state):
        # kind of ugly, we're going to double-calculate some events this way
        # but basically, need to run once, and see if a particular event causes a level up that results in a new move
        event_group.apply(prev_state)
        post_state = event_group.final_state

        # to make sure we catch the edge case where we learn a move while leveling up multiple times in battle
        # start by enumerating all "new" levels
        new_levels = [x for x in range(prev_state.solo_pkmn.cur_level + 1, post_state.solo_pkmn.cur_level + 1)]

        to_learn = []
        for cur_new_level in new_levels:
            if cur_new_level in self.level_up_move_defs:
                to_learn.append(self.level_up_move_defs[cur_new_level])
        
        if to_learn:
            event_group.apply(prev_state, level_up_learn_event_defs=to_learn)
    
    def refresh_existing_routes(self):
        result = []
        if os.path.exists(const.SAVED_ROUTES_DIR):
            for fragment in os.listdir(const.SAVED_ROUTES_DIR):
                name, ext = os.path.splitext(fragment)
                if ext != ".json":
                    continue
                result.append(name)
        
        return result
    
    def add_event(self, event_def, insert_before=None, folder_name=None):
        if not self.init_route_state:
            raise ValueError("Cannot add an event when solo pokmn is not yet selected")
        if event_def.trainer_name:
            self.defeated_trainers.add(event_def.trainer_name)
        if folder_name is None and event_def.original_folder_name is not None:
            folder_name = event_def.original_folder_name

        new_event = route_events.EventGroup(event_def)

        if insert_before is None:
            if folder_name is None:
                raise ValueError("No group or folder defined to figure out where to add event")
            cur_folder = self.event_folders[self.folder_idx_lookup[folder_name]]
            self._calc_single_event(new_event, cur_folder.final_state)
            cur_folder.event_groups.append(new_event)
            if new_event.error_messages:
                cur_folder.child_errors = True
            cur_folder.final_state = new_event.final_state
        else:
            _, folder_idx, group_idx = self._get_event_group_info(insert_before)
            self.event_folders[folder_idx].event_groups.insert(group_idx, new_event)
            self._recalc()
    
    def remove_group(self, group_id):
        group_obj, folder_idx, group_idx = self._get_event_group_info(group_id)
        if group_obj.event_definition.trainer_name is not None:
            self.defeated_trainers.remove(group_obj.event_definition.trainer_name)
        del self.event_folders[folder_idx].event_groups[group_idx]
        self._recalc()

    def replace_group(self, group_id, new_event_def):
        group_obj, folder_idx, group_idx = self._get_event_group_info(group_id)

        if group_obj is None:
            # TODO: kinda gross, we allow updating some items (just levelup learn moves)
            # TODO: so we need this one extra processing hook here to handle when the "group"
            # TODO: being replaced is actually an item, not a group
            item_obj = self.get_event_obj(group_id)
            if item_obj is None:
                raise ValueError(f"Cannot find any event with id: {group_id}")

            if isinstance(item_obj, route_events.EventFolder):
                raise ValueError(f"Cannot update EventFolder")
            
            if item_obj.event_definition.get_event_type() != const.TASK_LEARN_MOVE_LEVELUP:
                raise ValueError(f"Can only update event items for level up moves, currentlty")
            
            # just replace the lookup definition, and then recalculate everything
            self.level_up_move_defs[new_event_def.learn_move.level] = new_event_def.learn_move
            self._recalc()
        else:
            if group_obj.event_definition.trainer_name is not None:
                self.defeated_trainers.remove(group_obj.event_definition.trainer_name)
            
            self.event_folders[folder_idx].event_groups[group_idx].event_definition = new_event_def
            self._recalc()

    def move_group(self, group_id, move_up):
        # NOTE: can only move within a folder. To change folders, need to call a separate function
        group_obj, folder_idx, group_idx = self._get_event_group_info(group_id)
        if group_obj is None:
            raise ValueError(f"No group found with group_id: {group_id}")

        if move_up:
            insert_idx = max(group_idx - 1, 0)
        else:
            insert_idx = min(group_idx + 1, len(self.event_folders[folder_idx].event_groups) - 1)
        
        self.event_folders[folder_idx].event_groups.remove(group_obj)
        self.event_folders[folder_idx].event_groups.insert(insert_idx, group_obj)
        self._recalc()

    def transfer_group(self, group_id, dest_folder_name):
        cur_group, cur_folder_idx, cur_group_idx = self._get_event_group_info(group_id)
        if cur_group is None:
            raise ValueError(f"Cannot find group for id: {group_id}")
        
        dest_folder_idx = self.folder_idx_lookup.get(dest_folder_name)
        if dest_folder_idx is None:
            raise ValueError(f"Cannot find folder named: {dest_folder_name}")
        
        self.event_folders[cur_folder_idx].event_groups.remove(cur_group)
        self.event_folders[dest_folder_idx].event_groups.append(cur_group)
        self._recalc()
    
    def _reindex_folders(self):
        self.folder_idx_lookup = {x.name: idx for idx, x in enumerate(self.event_folders)}

    def add_folder(self, folder_name, insert_before=None):
        new_folder = route_events.EventFolder(folder_name)
        if insert_before is None:
            self.event_folders.append(new_folder)
        else:
            _, folder_idx = self._get_event_folder_info(insert_before)
            self.event_folders.insert(folder_idx, new_folder)

        self._reindex_folders()
        self._recalc()

    def rename_folder(self, cur_name, new_name):
        self.event_folders[self.folder_idx_lookup[cur_name]].name = new_name
        self.folder_idx_lookup[new_name] = self.folder_idx_lookup[cur_name]
        del self.folder_idx_lookup[cur_name]

    def move_folder(self, group_id, move_up):
        # NOTE: can only move within a folder. To change folders, need to call a separate function
        folder_obj, folder_idx = self._get_event_folder_info(group_id)
        if folder_obj is None:
            raise ValueError(f"No folder found with group_id: {group_id}")

        if move_up:
            insert_idx = max(folder_idx - 1, 0)
        else:
            insert_idx = min(folder_idx + 1, len(self.event_folders) - 1)
        
        self.event_folders.remove(folder_obj)
        self.event_folders.insert(insert_idx, folder_obj)
        self._reindex_folders()
        self._recalc()
    
    def delete_folder(self, group_id):
        folder_obj, folder_idx = self._get_event_folder_info(group_id)
        if folder_obj is None:
            raise ValueError(f"No folder found with group_id: {group_id}")
        
        if len(folder_obj.event_groups) != 0:
            raise ValueError(f"Refusing to delete non-empty folder: {folder_obj.name}")
        
        del self.event_folders[folder_idx]
        del self.folder_idx_lookup[folder_obj.name]
        # should never be necessary since the folder is empty, but recalc just for safety
        self._recalc()

    def save(self, name):
        if not os.path.exists(const.SAVED_ROUTES_DIR):
            os.mkdir(const.SAVED_ROUTES_DIR)

        final_path = os.path.join(const.SAVED_ROUTES_DIR, f"{name}.json")
        io_utils.backup_file_if_exists(final_path)

        flat_event_list = []
        for cur_folder in self.event_folders:
            flat_event_list.extend(cur_folder.serialize())

        with open(final_path, 'w') as f:
            json.dump({
                const.NAME_KEY: self.init_route_state.solo_pkmn.name,
                const.TASK_LEARN_MOVE_LEVELUP: [x.serialize() for x in self.level_up_move_defs.values()],
                const.EVENTS: flat_event_list
            }, f, indent=4)
    
    def load_min_battle(self, name):
        final_path = os.path.join(const.MIN_BATTLES_DIR, f"{name}.json")

        with open(final_path, 'r') as f:
            result = json.load(f)
        
        # kinda weird, but just reset to same mon to trigger cleanup in helper function
        self._reset_events()
        self.set_solo_pkmn(self.init_route_state.solo_pkmn.name)
        for cur_event in result[const.EVENTS]:
            temp = route_events.EventDefinition.deserialize(cur_event)
            if temp.original_folder_name not in self.folder_idx_lookup:
                self.add_folder(temp.original_folder_name)
            self.add_event(temp)
    
    def load(self, name):
        final_path = os.path.join(const.SAVED_ROUTES_DIR, f"{name}.json")

        with open(final_path, 'r') as f:
            result = json.load(f)
        
        raw_level_up_moves = result.get(const.TASK_LEARN_MOVE_LEVELUP)
        if raw_level_up_moves is not None:
            level_up_moves = [route_events.LearnMoveEventDefinition.deserialize(x) for x in raw_level_up_moves]
        else:
            level_up_moves = None
        
        self._reset_events()
        self.set_solo_pkmn(result[const.NAME_KEY], level_up_moves=level_up_moves)
        for cur_event in result[const.EVENTS]:
            temp = route_events.EventDefinition.deserialize(cur_event)
            if temp.original_folder_name not in self.folder_idx_lookup:
                self.add_folder(temp.original_folder_name)
            self.add_event(temp)
