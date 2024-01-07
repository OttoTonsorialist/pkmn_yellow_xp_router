import os
import json
import logging
from typing import Dict, Tuple

from utils.constants import const
from pkmn import universal_data_objects
from pkmn.gen_factory import current_gen_info, change_version
from pkmn.pkmn_db import sanitize_string
from utils import io_utils
from routing import route_events
from routing import full_route_state

logger = logging.getLogger(__name__)


class Router:
    def __init__(self):
        self.init_route_state = None
        self.pkmn_version = None
        self.root_folder = route_events.EventFolder(None, const.ROOT_FOLDER_NAME)
        self.folder_lookup = {const.ROOT_FOLDER_NAME: self.root_folder}
        self.event_lookup = {}
        self.event_item_lookup = {}

        self.level_up_move_defs:Dict[Tuple[str, int], route_events.LearnMoveEventDefinition] = {}
        self.defeated_trainers = set()
    
    def _reset_events(self):
        self.root_folder = route_events.EventFolder(None, const.ROOT_FOLDER_NAME)
        self.folder_lookup = {const.ROOT_FOLDER_NAME: self.root_folder}
        self.event_lookup = {}
        self.event_item_lookup = {}

        self.defeated_trainers = set()
    
    def _change_version(self, new_version):
        self.pkmn_version = new_version
        change_version(self.pkmn_version)
    
    def get_event_obj(self, event_id):
        return self.event_lookup.get(event_id, self.event_item_lookup.get(event_id))

    def get_final_state(self):
        if len(self.root_folder.children):
            return self.root_folder.final_state
        return self.init_route_state
    
    def set_solo_pkmn(self, pkmn_name, level_up_moves=None, custom_dvs=None, custom_ability=None, custom_nature=None):
        pkmn_base = current_gen_info().pkmn_db().get_pkmn(pkmn_name)
        if pkmn_base is None:
            raise ValueError(f"Could not find base stats for Pokemon: {pkmn_name}")
        
        if custom_ability is None:
            custom_ability = pkmn_base.abilitiies[0]
        
        if custom_nature is None:
            custom_nature = universal_data_objects.Nature.HARDY
        elif not isinstance(custom_nature, universal_data_objects.Nature):
            custom_nature = universal_data_objects.Nature(custom_nature)
        
        if custom_dvs is not None:
            # when setting custom DVs, should expect a dict of all values
            # Convert that to a StatBlock here when appropriate
            if not isinstance(custom_dvs, universal_data_objects.StatBlock):
                try:
                    custom_dvs = current_gen_info().make_stat_block(
                        custom_dvs[const.HP],
                        custom_dvs[const.ATTACK],
                        custom_dvs[const.DEFENSE],
                        custom_dvs[const.SPECIAL_ATTACK],
                        custom_dvs[const.SPECIAL_DEFENSE],
                        custom_dvs[const.SPEED]
                    )
                except Exception:
                    custom_dvs = current_gen_info().make_stat_block(
                        custom_dvs[const.HP],
                        custom_dvs[const.ATK],
                        custom_dvs[const.DEF],
                        custom_dvs[const.SPC],
                        custom_dvs[const.SPC],
                        custom_dvs[const.SPD]
                    )
        else:
            if current_gen_info().get_generation() <= 2:
                custom_dvs = current_gen_info().make_stat_block(15, 15, 15, 15, 15, 15)
            else:
                custom_dvs = current_gen_info().make_stat_block(31, 31, 31, 31, 31, 31)
        
        new_badge_list = current_gen_info().make_badge_list()
        self.init_route_state = full_route_state.RouteState(
            full_route_state.SoloPokemon(
                pkmn_name,
                pkmn_base,
                custom_dvs,
                new_badge_list,
                current_gen_info().make_stat_block(0, 0, 0, 0, 0, 0, is_stat_xp=True),
                custom_ability,
                custom_nature,
            ),
            new_badge_list,
            current_gen_info().make_inventory()
        )

        if level_up_moves is None:
            self.level_up_move_defs = {
                (sanitize_string(x[1]), int(x[0])): route_events.LearnMoveEventDefinition(x[1], None, const.MOVE_SOURCE_LEVELUP, level=int(x[0]))
                for x in pkmn_base.levelup_moves
            }
        else:
            # TODO: should double check loaded moves against expected moves from DB, and complain if something doesn't match
            self.level_up_move_defs = {(sanitize_string(x.move_to_learn), x.level): x for x in level_up_moves}

        self._recalc()
    
    def change_current_innate_stats(self, new_dvs:universal_data_objects.StatBlock, new_ability:str, new_nature:universal_data_objects.Nature):
        cur_mon = self.init_route_state.solo_pkmn
        self.init_route_state = full_route_state.RouteState(
            full_route_state.SoloPokemon(
                cur_mon.name,
                cur_mon.species_def,
                new_dvs,
                self.init_route_state.badges,
                current_gen_info().make_stat_block(0, 0, 0, 0, 0, 0, is_stat_xp=True),
                new_ability,
                new_nature,
            ),
            self.init_route_state.badges,
            self.init_route_state.inventory
        )
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
            for test_key in self.level_up_move_defs:
                if test_key[1] == cur_new_level:
                    to_learn.append(self.level_up_move_defs[test_key])
        
        if to_learn:
            event_group.apply(prev_state, level_up_learn_event_defs=to_learn)
        
        for cur_item in event_group.event_items:
            self.event_item_lookup[cur_item.group_id] = cur_item
    
    def add_area(self, area_name, insert_after=None, dest_folder_name=const.ROOT_FOLDER_NAME, include_rematches=False):
        trainers_to_add = current_gen_info().trainer_db().get_valid_trainers(trainer_loc=area_name, defeated_trainers=self.defeated_trainers, show_rematches=include_rematches)
        if len(trainers_to_add) == 0:
            return

        folder_name = area_name
        count = 1
        while folder_name in self.folder_lookup:
            count += 1
            folder_name = f"{area_name} Trip:{count}"
        
        # once we have a valid folder name to create, go ahead and create the folder
        self.add_event_object(new_folder_name=folder_name, insert_after=insert_after, dest_folder_name=dest_folder_name, recalc=False)
        # then just create all the trainer events in that area
        for cur_trainer in trainers_to_add:
            self.add_event_object(
                event_def=route_events.EventDefinition(trainer_def=route_events.TrainerEventDefinition(cur_trainer)),
                dest_folder_name=folder_name,
                recalc=False
            )
        
        self._recalc()
    
    def add_event_object(
        self,
        event_def:route_events.EventDefinition=None,
        new_folder_name=None,
        insert_before=None,
        insert_after=None,
        dest_folder_name=const.ROOT_FOLDER_NAME,
        recalc=True,
        folder_expanded=True,
        folder_enabled=True
    ):
        if not self.init_route_state:
            raise ValueError("Cannot add an event when solo pokmn is not yet selected")
        if event_def is None and new_folder_name is None:
            raise ValueError("Must define either folder name or event definition")
        
        if insert_after is not None:
            insert_after_obj = self.get_event_obj(insert_after)
            if isinstance(insert_after_obj, route_events.EventItem):
                raise ValueError("Cannot insert an object into the middle of a group")

            parent_obj = insert_after_obj.parent
        elif insert_before is not None:
            insert_before_obj = self.get_event_obj(insert_before)
            if isinstance(insert_before_obj, route_events.EventItem):
                raise ValueError("Cannot insert an object into the middle of a group")

            parent_obj = insert_before_obj.parent
        else:
            try:
                parent_obj = self.folder_lookup[dest_folder_name]
            except Exception as e:
                logger.error(f"Failed to lookup folder with name {dest_folder_name}:")
                logger.exception(e)
                raise ValueError(f"Cannot find folder with name: {dest_folder_name}")

        if new_folder_name is not None:
            new_obj = route_events.EventFolder(
                parent_obj,
                new_folder_name,
                expanded=folder_expanded,
                event_definition=event_def,
                enabled=folder_enabled
            )
            self.folder_lookup[new_folder_name] = new_obj

        elif event_def is not None:
            if event_def.trainer_def and not current_gen_info().trainer_db().get_trainer(event_def.trainer_def.trainer_name).refightable:
                self.defeated_trainers.add(event_def.trainer_def.trainer_name)
                if event_def.trainer_def.second_trainer_name and not current_gen_info().trainer_db().get_trainer(event_def.trainer_def.trainer_name).refightable:
                    self.defeated_trainers.add(event_def.trainer_def.second_trainer_name)
            new_obj = route_events.EventGroup(parent_obj, event_def)
        
        self.event_lookup[new_obj.group_id] = new_obj
        parent_obj.insert_child_after(new_obj, after_obj=self.get_event_obj(insert_after), before_obj=self.get_event_obj(insert_before))
        if recalc:
            self._recalc()
        
        return new_obj.group_id
    
    def batch_remove_events(self, event_id_list):
        for cur_event in event_id_list:
            self.remove_event_object(cur_event, recalc=False)
        
        self._recalc()
    
    def remove_event_object(self, event_id, recalc=True):
        cur_event = self.event_lookup.get(event_id)
        if cur_event is None:
            raise ValueError(f"Cannot remove event for unknown id: {event_id}")
        elif isinstance(cur_event, route_events.EventItem):
            raise ValueError(f"Cannot remove EventItem objects: {cur_event.name}")
        
        if isinstance(cur_event, route_events.EventGroup) and cur_event.event_definition.trainer_def is not None:
            if cur_event.event_definition.trainer_def.trainer_name in self.defeated_trainers:
                self.defeated_trainers.remove(cur_event.event_definition.trainer_def.trainer_name)
            if cur_event.event_definition.trainer_def.second_trainer_name in self.defeated_trainers:
                self.defeated_trainers.remove(cur_event.event_definition.trainer_def.second_trainer_name)
        
        cur_event.parent.remove_child(cur_event)
        del self.event_lookup[cur_event.group_id]

        # once we've successfully removed the event, forget the lookup if it was a folder
        if isinstance(cur_event, route_events.EventFolder):
            del self.folder_lookup[cur_event.name]
            # also recursively remove event objects so that defeated trainers get updated properly
            self.batch_remove_events([x.group_id for x in cur_event.children])
        
        if recalc:
            self._recalc()

    def move_event_object(self, event_id, move_up_flag):
        # NOTE: can only move within a folder. To change folders, need to call a separate function
        try:
            obj_to_move = self.get_event_obj(event_id)
            obj_to_move.parent.move_child(obj_to_move, move_up_flag)
            self._recalc()
        except Exception as e:
            logger.error(f"Failed to move event object: {event_id}")
            logger.exception(e)
            raise ValueError(f"Failed to find event object with id: {event_id}")

    def toggle_event_highlight(self, event_id):
        # NOTE: can only move within a folder. To change folders, need to call a separate function
        try:
            obj_to_highlight = self.get_event_obj(event_id)
            if isinstance(obj_to_highlight, route_events.EventGroup):
                obj_to_highlight.event_definition.toggle_highlight()
        except Exception as e:
            logger.error(f"Failed to toggle highlight for event: {event_id}")
            logger.exception(e)
            raise ValueError(f"Failed to find event object with id: {event_id}")
    
    def get_invalid_folder_transfers(self, event_id):
        # NOTE: EventGroup objects will always have an empty result list
        # this is intentional, EventGroups can be transferred anywhere
        result = []
        self._get_child_folder_names_recursive(self.event_lookup.get(event_id), result)
        return result
    
    def _get_child_folder_names_recursive(self, cur_obj, result):
        if isinstance(cur_obj, route_events.EventFolder):
            result.append(cur_obj.name)
            for child in cur_obj.children:
                self._get_child_folder_names_recursive(child, result)
    
    def transfer_events(self, event_id_list, dest_folder_name):
        # figure out the destination folder first.
        # If transferring to a destination folder that does not exist, create it just before the first event
        dest_folder = self.folder_lookup.get(dest_folder_name)
        if dest_folder is None:
            self.add_event_object(new_folder_name=dest_folder_name)

        # goofy-looking, but intentional. Do all error checking before any modification
        # This way, if any errors occur, the route isn't left in a half-valid state
        for cur_event_id in event_id_list:
            cur_event = self.event_lookup.get(cur_event_id)
            if cur_event is None:
                raise ValueError(f"Cannot find group for id: {cur_event_id}")
            
            dest_folder = self.folder_lookup.get(dest_folder_name)
            if dest_folder_name in self.get_invalid_folder_transfers(cur_event_id):
                raise ValueError(f"Cannot transfer a folder into itself or a child folder")

        # now that we know everything is valid, actualy make the updates
        for cur_event_id in event_id_list:
            cur_event = self.event_lookup.get(cur_event_id)
            dest_folder = self.folder_lookup.get(dest_folder_name)
            cur_event.parent.remove_child(cur_event)
            dest_folder.insert_child_after(cur_event, after_obj=None)

        self._recalc()
    
    def replace_event_group(self, event_group_id, new_event_def:route_events.EventDefinition):
        event_group_obj = self.get_event_obj(event_group_id)
        if event_group_obj is None:
            raise ValueError(f"Cannot find any event with id: {event_group_id}")

        if isinstance(event_group_obj, route_events.EventFolder):
            if new_event_def.get_event_type() != const.TASK_NOTES_ONLY:
                raise ValueError(f"Can only assign notes to EventFolders")
            event_group_obj.event_definition = new_event_def

        elif isinstance(event_group_obj, route_events.EventItem):
            # TODO: kinda gross, we allow updating some items (just levelup learn moves)
            # TODO: so we need this one extra processing hook here to handle when the "group"
            # TODO: being replaced is actually an item, not a group
            if event_group_obj.event_definition.get_event_type() != const.TASK_LEARN_MOVE_LEVELUP:
                raise ValueError(f"Can only update event items for level up moves, currentlty")
            
            # just replace the lookup definition
            self.level_up_move_defs[(new_event_def.learn_move.move_to_learn, new_event_def.learn_move.level)] = new_event_def.learn_move

        else:
            if event_group_obj.event_definition.trainer_def is not None:
                if event_group_obj.event_definition.trainer_def.trainer_name in self.defeated_trainers:
                    self.defeated_trainers.remove(event_group_obj.event_definition.trainer_def.trainer_name)
            
            if new_event_def.trainer_def is not None and not current_gen_info().trainer_db().get_trainer(new_event_def.trainer_def.trainer_name).refightable:
                self.defeated_trainers.add(new_event_def.trainer_def.trainer_name)
            
            event_group_obj.event_definition = new_event_def

        self._recalc()
    
    def replace_levelup_move_event(self, new_event_def:route_events.LearnMoveEventDefinition):
        self.level_up_move_defs[(sanitize_string(new_event_def.move_to_learn), new_event_def.level)] = new_event_def
        self._recalc()
    
    def is_valid_levelup_move(self, move_to_learn:str, level:int):
        return (sanitize_string(move_to_learn), level) in self.level_up_move_defs
    
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

        out_obj = {
            const.NAME_KEY: self.init_route_state.solo_pkmn.name,
            const.DVS_KEY: self.init_route_state.solo_pkmn.dvs.serialize(current_gen_info().get_generation()),
            const.ABILITY_KEY: self.init_route_state.solo_pkmn.ability,
            const.NATURE_KEY: self.init_route_state.solo_pkmn.nature.value,
            const.PKMN_VERSION_KEY: self.pkmn_version,
            const.TASK_LEARN_MOVE_LEVELUP: [x.serialize() for x in self.level_up_move_defs.values()],
            const.EVENTS: [self.root_folder.serialize()]
        }

        with open(final_path, 'w') as f:
            json.dump(out_obj, f, indent=4)
    
    def new_route(self, solo_mon, base_route_path=None, pkmn_version=const.YELLOW_VERSION, custom_dvs=None, custom_ability=None, custom_nature=None):
        self._change_version(pkmn_version)
        self._reset_events()
        self.set_solo_pkmn(solo_mon, custom_dvs=custom_dvs, custom_ability=custom_ability, custom_nature=custom_nature)

        if base_route_path is not None:
            self.load(base_route_path, load_events_only=True)
    
    def load(self, route_path, load_events_only=False):
        # if we're using a template, we're going to path the full path in
        # otherwise, the name should exist in one of the two save dirs
        with open(route_path, 'r') as f:
            result = json.load(f)
        
        self._reset_events()

        if not load_events_only:
            self._change_version(result.get(const.PKMN_VERSION_KEY, const.YELLOW_VERSION))
            raw_level_up_moves = result.get(const.TASK_LEARN_MOVE_LEVELUP)
            if raw_level_up_moves is not None:
                level_up_moves = [route_events.LearnMoveEventDefinition.deserialize(x) for x in raw_level_up_moves]
            else:
                level_up_moves = None
            
            self.set_solo_pkmn(
                result[const.NAME_KEY],
                level_up_moves=level_up_moves,
                custom_dvs=result.get(const.DVS_KEY),
                custom_ability=result.get(const.ABILITY_KEY),
                custom_nature=result.get(const.NATURE_KEY),
            )
        
        if len(result[const.EVENTS]) > 0:
            self._load_events_recursive(self.root_folder, result[const.EVENTS][0])

        self._recalc()
    
    def _load_events_recursive(self, parent_folder:route_events.EventFolder, json_obj):
        for event_json in json_obj[const.EVENTS]:
            if const.EVENT_FOLDER_NAME in event_json:
                self.add_event_object(
                    event_def=route_events.EventDefinition.deserialize(event_json),
                    new_folder_name=event_json[const.EVENT_FOLDER_NAME],
                    dest_folder_name=parent_folder.name,
                    recalc=False,
                    folder_expanded=event_json.get(const.EXPANDED_KEY, True),
                    folder_enabled=event_json.get(const.ENABLED_KEY, True),
                )
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
            if obj.event_definition.notes:
                notes_val = indent + obj.event_definition.notes.replace('\n', '\n' + indent)
                output.append(notes_val)
        elif isinstance(obj, route_events.EventDefinition):
            if obj.get_event_type() == const.TASK_NOTES_ONLY:
                output.append(f"{indent}Notes:")
            else:
                output.append(f"{indent}{obj}")
                if obj.get_event_type() == const.TASK_TRAINER_BATTLE and obj.trainer_def.setup_moves:
                    output.append(f"{indent}Setup Moves: {obj.trainer_def.setup_moves}")
                if obj.get_event_type() == const.TASK_TRAINER_BATTLE and obj.trainer_def.mimic_selection:
                    output.append(f"{indent}Mimic: {obj.trainer_def.mimic_selection}")
            if obj.notes:
                notes_val = indent + obj.notes.replace('\n', '\n' + indent)
                output.append(notes_val)
        output.append(indent)

    def _export_recursive(self, cur_folder:route_events.EventFolder, depth, output:list):
        for cur_obj in cur_folder.children:
            if not cur_obj.is_enabled():
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
