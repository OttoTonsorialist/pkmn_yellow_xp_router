import os
import json

from constants import const
import data_objects
import database
import pkmn_utils
import utils

event_id_counter = 0


class EventItem:
    def __init__(self, cur_solo_pkmn, is_rare_candy=False, vitamin=None, enemy_pkmn=None, trainer_name=None, is_final_pkmn=False):
        self.name = None

        self.trainer_name = trainer_name
        self.enemy_pkmn = enemy_pkmn
        self.is_rare_candy = is_rare_candy
        self.vitamin = vitamin
        self.is_final_pkmn = is_final_pkmn

        self.post_event_solo_pkmn = None
        self.apply(cur_solo_pkmn)
    
    def apply(self, cur_solo_pkmn: data_objects.SoloPokemon):
        if self.enemy_pkmn is not None:
            self.name = f"{self.trainer_name}: {self.enemy_pkmn}"
            self.post_event_solo_pkmn =  cur_solo_pkmn.defeat_pkmn(self.enemy_pkmn, trainer_name=self.trainer_name, is_final_pkmn=self.is_final_pkmn)
        elif self.is_rare_candy:
            self.name = "Rare Candy"
            self.post_event_solo_pkmn =  cur_solo_pkmn.rare_candy()
        elif self.vitamin is not None:
            self.name = f"Vitamin: {self.vitamin}"
            self.post_event_solo_pkmn =  cur_solo_pkmn.take_vitamin(self.vitamin)


class EventGroup:
    def __init__(self, cur_solo_pkmn, trainer_obj=None, is_rare_candy=False, vitamin=None):
        global event_id_counter
        self.group_id = event_id_counter
        event_id_counter += 1

        self.name = None
        self.event_items = []
        self.init_solo_pkmn = cur_solo_pkmn
        self.is_rare_candy = is_rare_candy
        self.vitamin = vitamin
        self.trainer_obj = trainer_obj
        self.pkmn_after_levelups = []

        self.apply(cur_solo_pkmn)
    
    def apply(self, cur_solo_pkmn):
        self.init_solo_pkmn = cur_solo_pkmn
        self.pkmn_after_levelups = []
        if self.trainer_obj is not None:
            self.name = f"Trainer: {self.trainer_obj.name} ({self.trainer_obj.location})"
            pkmn_counter = {}
            for pkmn_idx, trainer_pkmn in enumerate(self.trainer_obj.pkmn):
                self.event_items.append(
                    EventItem(
                        cur_solo_pkmn,
                        enemy_pkmn=trainer_pkmn,
                        trainer_name=self.trainer_obj.name,
                        is_final_pkmn=pkmn_idx==len(self.trainer_obj.pkmn)-1
                    )
                )
                cur_pkmn_name = self.trainer_obj.pkmn[pkmn_idx].name
                pkmn_counter[cur_pkmn_name] = pkmn_counter.get(cur_pkmn_name, 0) + 1
                
                next_solo_pkmn = self.event_items[-1].post_event_solo_pkmn
                if next_solo_pkmn.cur_level != cur_solo_pkmn.cur_level:
                    if pkmn_idx + 1 < len(self.trainer_obj.pkmn):
                        next_pkmn_name = self.trainer_obj.pkmn[pkmn_idx + 1].name
                        next_pkmn_count = pkmn_counter.get(next_pkmn_name, 0) + 1
                        self.pkmn_after_levelups.append(f"#{next_pkmn_count} {next_pkmn_name}")
                    else:
                        self.pkmn_after_levelups.append("after_final_pkmn")
                cur_solo_pkmn = next_solo_pkmn
                        
        elif self.is_rare_candy:
            self.event_items.append(EventItem(cur_solo_pkmn, is_rare_candy=True))
            self.name = self.event_items[0].name
        elif self.vitamin is not None:
            self.event_items.append(EventItem(cur_solo_pkmn, vitamin=self.vitamin))
            self.name = self.event_items[0].name
            
        if len(self.event_items) == 0:
            print(f"Something went wrong generating event group: {self.trainer_obj}")
        self.final_solo_pkmn = self.event_items[-1].post_event_solo_pkmn
    
    def get_pkmn_after_levelups(self):
        return ",".join(self.pkmn_after_levelups)

    def pkmn_level(self):
        return self.final_solo_pkmn.cur_level
    
    def xp_to_next_level(self):
        return self.final_solo_pkmn.xp_to_next_level

    def xp_gain(self):
        return self.final_solo_pkmn.cur_xp - self.init_solo_pkmn.cur_xp

    def total_xp(self):
        return self.final_solo_pkmn.cur_xp

    def to_dict(self):
        return {
            const.TASK_RARE_CANDY: self.event_items[0].is_rare_candy,
            const.TASK_VITAMIN: self.event_items[0].vitamin,
            const.TASK_TRAINER_BATTLE: self.event_items[0].trainer_name
        }

class Router:
    def __init__(self):
        self.solo_pkmn_base = None
        self.all_events = []
        self.defeated_trainers = set()
    
    def _reset_events(self):
        self.all_events = []
        self.defeated_trainers = set()
    
    def save(self, name):
        if not os.path.exists(const.SAVED_ROUTES_DIR):
            os.mkdir(const.SAVED_ROUTES_DIR)

        final_path = os.path.join(const.SAVED_ROUTES_DIR, f"{name}.json")
        utils.backup_file_if_exists(final_path)

        global event_id_counter

        with open(final_path, 'w') as f:
            json.dump({
                const.EVENT_ID_COUNTER: event_id_counter,
                const.NAME_KEY: self.solo_pkmn_base.name,
                const.EVENTS: [x.to_dict() for x in self.all_events]
            }, f)
    
    def refresh_existing_routes(self):
        result = []
        for fragment in os.listdir(const.SAVED_ROUTES_DIR):
            name, ext = os.path.splitext(fragment)
            if ext != ".json":
                continue
            result.append(name)
        
        return result
    
    def load(self, name):
        final_path = os.path.join(const.SAVED_ROUTES_DIR, f"{name}.json")

        with open(final_path, 'r') as f:
            result = json.load(f)
        
        global event_id_counter
        event_id_counter = result[const.EVENT_ID_COUNTER]
        self.set_solo_pkmn(result[const.NAME_KEY])
        for cur_event in result[const.EVENTS]:
            self.add_event(
                trainer_name=cur_event[const.TASK_TRAINER_BATTLE],
                vitamin=cur_event[const.TASK_VITAMIN],
                is_rare_candy=cur_event[const.TASK_RARE_CANDY],
            )
    
    def set_solo_pkmn(self, pkmn_name):
        pkmn_base = database.pkmn_db.data.get(pkmn_name)
        if pkmn_base is None:
            raise ValueError(f"Could not find base stats for Pokemon: {pkmn_name}")
        
        self.solo_pkmn_base = data_objects.SoloPokemon(pkmn_name, pkmn_base)
        self._reset_events()
    
    def add_event(self, is_rare_candy=False, vitamin=None, trainer_name=None, insert_before=None):
        if not self.solo_pkmn_base:
            raise ValueError("Cannot add an event when solo pokmn is not yet selected")
        if trainer_name:
            self.defeated_trainers.add(trainer_name)

        new_event = EventGroup(
            self.get_final_solo_pkmn(),
            is_rare_candy=is_rare_candy,
            vitamin=vitamin,
            trainer_obj=database.trainer_db.data.get(trainer_name)
        )

        if insert_before is None:
            self.all_events.append(new_event)
        else:
            insert_idx = self.get_event_group_info(insert_before)[1]
            self.all_events.insert(insert_idx, new_event)
            self._recalc_from(insert_idx)

    def get_event_group_info(self, event_group_id):
        for idx, cur_event in enumerate(self.all_events):
            if cur_event.group_id == event_group_id:
                return cur_event, idx
        
        return None, None
    
    def bulk_fight_trainers(self, trainer_name_list):
        self._reset_events()
        for trainer_name in trainer_name_list:
            self.add_event(trainer_name=trainer_name)
    
    def get_post_event_solo_pkmn(self, group_id):
        group_event = self.get_event_group_info(group_id)[0]
        if group_event is None:
            return None
        return group_event.final_solo_pkmn
    
    def get_final_solo_pkmn(self):
        if len(self.all_events):
            return self.all_events[-1].final_solo_pkmn
        return self.solo_pkmn_base
    
    def _recalc_from(self, start_idx):
        start_idx = 0
        for recalc_idx in range(start_idx, len(self.all_events)):
            if recalc_idx == 0:
                prev_pkmn = self.solo_pkmn_base
            else:
                prev_pkmn = self.all_events[recalc_idx - 1].final_solo_pkmn

            self.all_events[recalc_idx].apply(prev_pkmn)
    
    def remove_group(self, group_id):
        group_obj, group_idx = self.get_event_group_info(group_id)
        if group_obj.trainer_obj is not None:
            self.defeated_trainers.remove(group_obj.trainer_obj.name)
        del self.all_events[group_idx]
        self._recalc_from(group_idx)

    def move_group_up(self, group_id):
        group_obj, group_idx = self.get_event_group_info(group_id)
        self._move_group_to(group_obj, max(group_idx - 1, 0))
    
    def move_group_down(self, group_id):
        group_obj, group_idx = self.get_event_group_info(group_id)
        if group_obj is None:
            raise ValueError(f"No group found with group_id: {group_id}")
        self._move_group_to(group_obj, min(group_idx + 1, len(self.all_events) - 1))
    
    def _move_group_to(self, group_obj, insert_idx):
        self.all_events.remove(group_obj)
        self.all_events.insert(insert_idx, group_obj)
        self._recalc_from(insert_idx)
