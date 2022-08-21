import os
import time
import json

from utils.constants import const
from pkmn import data_objects
from pkmn import pkmn_db
from utils import io_utils
from pkmn import route_events
from pkmn import route_state_objects


class Router:
    def __init__(self):
        self.init_route_state = None
        self.pkmn_version = None
        self.root_folder = route_events.EventFolder(None, const.ROOT_FOLDER_NAME)
        self.folder_lookup = {const.ROOT_FOLDER_NAME: self.root_folder}
        self.event_lookup = {}
        self.event_item_lookup = {}

        self.level_up_move_defs = {}
        self.defeated_trainers = set()
    
    def _reset_events(self):
        self.root_folder = route_events.EventFolder(None, const.ROOT_FOLDER_NAME)
        self.folder_lookup = {const.ROOT_FOLDER_NAME: self.root_folder}
        self.event_lookup = {}
        self.event_item_lookup = {}

        self.defeated_trainers = set()
    
    def _change_version(self, new_version):
        self.pkmn_version = new_version
        pkmn_db.change_version(self.pkmn_version)
    
    def get_event_obj(self, event_id):
        return self.event_lookup.get(event_id, self.event_item_lookup.get(event_id))

    def get_final_state(self):
        if len(self.root_folder.children):
            return self.root_folder.final_state
        return self.init_route_state
    
    def set_solo_pkmn(self, pkmn_name, level_up_moves=None):
        pkmn_base = pkmn_db.pkmn_db.get_pkmn(pkmn_name)
        if pkmn_base is None:
            raise ValueError(f"Could not find base stats for Pokemon: {pkmn_name}")
        
        self.init_route_state = route_state_objects.RouteState(
            route_state_objects.SoloPokemon(pkmn_name, pkmn_base),
            data_objects.BadgeList(),
            route_state_objects.Inventory()
        )

        if level_up_moves is None:
            self.level_up_move_defs = {
                int(x[0]): route_events.LearnMoveEventDefinition(x[1], None, const.MOVE_SOURCE_LEVELUP, level=int(x[0]))
                for x in pkmn_base.levelup_moves
            }
        else:
            # TODO: should double check loaded moves against expected moves from DB, and complain if something doesn't match
            self.level_up_move_defs = {x.level: x for x in level_up_moves}

        self._recalc()
    
    def _recalc(self):
        self.event_item_lookup = {}

        # TODO: only recalc what's necessary, based on a passed-in index
        # TODO: wrapper for recursive function currently does nothing, may want to remove later
        self._recursive_recalc(self.root_folder, self.init_route_state)

    def _recursive_recalc(self, obj, cur_state):
        obj.init_state = cur_state

        if isinstance(obj, route_events.EventGroup):
            self._calc_single_event(obj, cur_state)
        else:
            obj.child_errors = False
            for inner_obj in obj.children:
                self._recursive_recalc(inner_obj, cur_state)
                cur_state = inner_obj.final_state
                if inner_obj.has_errors():
                    obj.child_errors = True
            obj.final_state = cur_state

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
        
        for cur_item in event_group.event_items:
            self.event_item_lookup[cur_item.group_id] = cur_item
    
    def add_area(self, area_name, insert_before=None, dest_folder_name=const.ROOT_FOLDER_NAME):
        trainers_to_add = pkmn_db.trainer_db.get_valid_trainers(trainer_loc=area_name, defeated_trainers=self.defeated_trainers)
        if len(trainers_to_add) == 0:
            return

        folder_name = area_name
        count = 1
        while folder_name in self.folder_lookup:
            count += 1
            folder_name = f"{area_name} Trip:{count}"
        
        # once we have a valid folder name to create, go ahead and create the folder
        self.add_event_object(new_folder_name=folder_name, insert_before=insert_before, dest_folder_name=dest_folder_name, recalc=False)
        # then just create all the trainer events in that area
        for cur_trainer in trainers_to_add:
            self.add_event_object(
                event_def=route_events.EventDefinition(trainer_def=route_events.TrainerEventDefinition(cur_trainer)),
                dest_folder_name=folder_name,
                recalc=False
            )
        
        self._recalc()
    
    def add_event_object(self, event_def:route_events.EventDefinition=None, new_folder_name=None, insert_before=None, dest_folder_name=const.ROOT_FOLDER_NAME, recalc=True):
        if not self.init_route_state:
            raise ValueError("Cannot add an event when solo pokmn is not yet selected")
        if event_def is None and new_folder_name is None:
            raise ValueError("Must define either folder name or event definition")
        elif event_def is not None and new_folder_name is not None:
            raise ValueError("Cannot define both folder name and event definition")
        
        if insert_before is not None:
            insert_before_obj = self.get_event_obj(insert_before)
            if isinstance(insert_before_obj, route_events.EventItem):
                raise ValueError("Cannot insert an object into the middle of a group")

            parent_obj = insert_before_obj.parent
        else:
            try:
                parent_obj = self.folder_lookup[dest_folder_name]
            except Exception as e:
                raise ValueError(f"Cannot find folder with name: {dest_folder_name}")

        if event_def is not None:
            if event_def.trainer_def:
                self.defeated_trainers.add(event_def.trainer_def.trainer_name)
            new_obj = route_events.EventGroup(parent_obj, event_def)

        elif new_folder_name is not None:
            new_obj = route_events.EventFolder(parent_obj, new_folder_name)
            self.folder_lookup[new_folder_name] = new_obj
        
        self.event_lookup[new_obj.group_id] = new_obj
        parent_obj.insert_child_before(new_obj, before_obj=self.get_event_obj(insert_before))
        if recalc:
            self._recalc()
    
    def remove_event_object(self, event_id):
        cur_event = self.event_lookup.get(event_id)
        if cur_event is None:
            raise ValueError(f"Cannot remove event for unknown id: {event_id}")
        elif isinstance(cur_event, route_events.EventItem):
            raise ValueError(f"Cannot remove EventItem objects: {cur_event.name}")
        
        if isinstance(cur_event, route_events.EventGroup) and cur_event.event_definition.trainer_def is not None:
            self.defeated_trainers.remove(cur_event.event_definition.trainer_def.trainer_name)
        
        cur_event.parent.remove_child(cur_event)
        del self.event_lookup[cur_event.group_id]

        # once we've successfully removed the event, forget the lookup if it was a folder
        if isinstance(cur_event, route_events.EventFolder):
            del self.folder_lookup[cur_event.name]
        
        self._recalc()

    def move_event_object(self, event_id, move_up_flag):
        # NOTE: can only move within a folder. To change folders, need to call a separate function
        try:
            obj_to_move = self.get_event_obj(event_id)
            obj_to_move.parent.move_child(obj_to_move, move_up_flag)
            self._recalc()
        except Exception as e:
            raise ValueError(f"Failed to find event object with id: {event_id}")
    
    def transfer_event_object(self, event_id, dest_folder_name):
        cur_event = self.event_lookup.get(event_id)
        if cur_event is None:
            raise ValueError(f"Cannot find group for id: {event_id}")
        
        dest_folder = self.folder_lookup.get(dest_folder_name)
        if dest_folder is None:
            raise ValueError(f"Cannot find destination folder named: {dest_folder_name}")
        
        if dest_folder == cur_event:
            raise ValueError(f"Cannot transfer a folder into itself")
        
        cur_event.parent.remove_child(cur_event)
        dest_folder.insert_child_before(cur_event, before_obj=None)
        self._recalc()
    
    def replace_event_group(self, event_group_id, new_event_def:route_events.EventDefinition):
        event_group_obj = self.get_event_obj(event_group_id)
        if event_group_obj is None:
            raise ValueError(f"Cannot find any event with id: {event_group_id}")

        if isinstance(event_group_obj, route_events.EventFolder):
            raise ValueError(f"Cannot update EventFolder")
        
        # TODO: kinda gross, we allow updating some items (just levelup learn moves)
        # TODO: so we need this one extra processing hook here to handle when the "group"
        # TODO: being replaced is actually an item, not a group
        if isinstance(event_group_obj, route_events.EventItem):
            if event_group_obj.event_definition.get_event_type() != const.TASK_LEARN_MOVE_LEVELUP:
                raise ValueError(f"Can only update event items for level up moves, currentlty")
            
            # just replace the lookup definition
            self.level_up_move_defs[new_event_def.learn_move.level] = new_event_def.learn_move
        else:
            if event_group_obj.event_definition.trainer_def is not None:
                self.defeated_trainers.remove(event_group_obj.event_definition.trainer_def.trainer_name)
            
            if new_event_def.trainer_def is not None:
                self.defeated_trainers.add(new_event_def.trainer_def.trainer_name)
            
            event_group_obj.event_definition = new_event_def

        self._recalc()

    def rename_event_folder(self, cur_name, new_name):
        folder_obj = self.folder_lookup[cur_name]
        folder_obj.name = new_name
        del self.folder_lookup[cur_name]
        self.folder_lookup[new_name] = folder_obj
    
    def save(self, name):
        if not os.path.exists(const.SAVED_ROUTES_DIR):
            os.mkdir(const.SAVED_ROUTES_DIR)

        final_path = os.path.join(const.SAVED_ROUTES_DIR, f"{name}.json")
        io_utils.backup_file_if_exists(final_path)

        with open(final_path, 'w') as f:
            json.dump({
                const.NAME_KEY: self.init_route_state.solo_pkmn.name,
                const.PKMN_VERSION_KEY: self.pkmn_version,
                const.TASK_LEARN_MOVE_LEVELUP: [x.serialize() for x in self.level_up_move_defs.values()],
                const.EVENTS: [self.root_folder.serialize()]
            }, f, indent=4)
    
    def new_route(self, solo_mon, min_battles_name=None, pkmn_version=const.YELLOW_VERSION):
        self.set_solo_pkmn(solo_mon)
        self._change_version(pkmn_version)

        if min_battles_name is None:
            self._reset_events()
        else:
            self.load(min_battles_name, min_battles=True, min_battles_version=pkmn_version)
    
    def load(self, name, min_battles=False, min_battles_version=const.YELLOW_VERSION):
        if min_battles:
            final_path = os.path.join(pkmn_db.get_min_battles_dir(min_battles_version), f"{name}.json")
        else:
            final_path = os.path.join(const.SAVED_ROUTES_DIR, f"{name}.json")

        with open(final_path, 'r') as f:
            result = json.load(f)
        
        self._reset_events()

        if min_battles:
            # min battles means we're starting a new route, which means we're relying on another function to set version
            self.set_solo_pkmn(self.init_route_state.solo_pkmn.name)
        else:
            self._change_version(result.get(const.PKMN_VERSION_KEY, const.YELLOW_VERSION))
            raw_level_up_moves = result.get(const.TASK_LEARN_MOVE_LEVELUP)
            if raw_level_up_moves is not None:
                level_up_moves = [route_events.LearnMoveEventDefinition.deserialize(x) for x in raw_level_up_moves]
            else:
                level_up_moves = None
            self.set_solo_pkmn(result[const.NAME_KEY], level_up_moves=level_up_moves)
        
        if len(result[const.EVENTS]) > 0:
            # check contents of first event to check for legacy loading
            if result[const.EVENTS][0][const.EVENT_FOLDER_NAME] == const.ROOT_FOLDER_NAME:
                # standard loading
                self._load_events_recursive(self.root_folder, result[const.EVENTS][0])
            else:
                # legacy loading
                for cur_event in result[const.EVENTS]:
                    temp = route_events.EventDefinition.deserialize(cur_event)
                    if temp.original_folder_name not in self.folder_lookup:
                        self.add_event_object(new_folder_name=temp.original_folder_name, dest_folder_name=const.ROOT_FOLDER_NAME, recalc=False)
                    self.add_event_object(event_def=temp, dest_folder_name=temp.original_folder_name, recalc=False)

        self._recalc()
    
    def _load_events_recursive(self, parent_folder:route_events.EventFolder, json_obj):
        for event_json in json_obj[const.EVENTS]:
            if const.EVENT_FOLDER_NAME in event_json:
                self.add_event_object(new_folder_name=event_json[const.EVENT_FOLDER_NAME], dest_folder_name=parent_folder.name, recalc=False)
                inner_parent = self.folder_lookup[event_json[const.EVENT_FOLDER_NAME]]
                self._load_events_recursive(inner_parent, event_json)
            else:
                self.add_event_object(
                    event_def=route_events.EventDefinition.deserialize(event_json),
                    dest_folder_name=parent_folder.name,
                    recalc=False
                )
    
    def export_notes(self, name):
        dest_path = os.path.join(const.SAVED_ROUTES_DIR, f"{name}_notes.txt")

        output = []
        self._export_recursive(self.root_folder, 0, output)

        with open(dest_path, 'w') as f:
            f.write("\n".join(output))
        
        return dest_path
                
    def _recalc(self):
        self.event_item_lookup = {}

        # TODO: only recalc what's necessary, based on a passed-in index
        # TODO: wrapper for recursive function currently does nothing, may want to remove later
        self._recursive_recalc(self.root_folder, self.init_route_state)

    def _export_single_entry(self, obj, depth:int, output:list):
        indent = "\t" * depth
        if isinstance(obj, route_events.EventFolder):
            output.append(f"{indent}Folder: {obj.name}")
        elif isinstance(obj, route_events.EventDefinition):
            output.append(f"{indent}{obj}")
            if obj.notes:
                notes_val = indent + obj.notes.replace('\n', '\n' + indent)
                output.append(notes_val)
        output.append(indent)

    def _export_recursive(self, cur_folder:route_events.EventFolder, depth, output:list):
        for cur_obj in cur_folder.children:
            if not cur_obj.enabled:
                continue
            if isinstance(cur_obj, route_events.EventFolder):
                self._export_single_entry(cur_obj, depth, output)
                self._export_recursive(cur_obj, depth + 1, output)
            else:
                self._export_single_entry(cur_obj.event_definition, depth, output)

                for cur_item in cur_obj.event_items:
                    item_event:route_events.EventDefinition = cur_item.event_definition
                    if item_event != cur_obj.event_definition and item_event.learn_move is not None:
                        self._export_single_entry(item_event, depth, output)
