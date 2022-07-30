import os
import configparser

import pkmn.pkmn_db as pkmn_db
from pkmn.router import Router
from pkmn.route_events import EventDefinition, EventFolder, EventGroup, EventItem, InventoryEventDefinition, WildPkmnEventDefinition
from utils.constants import const


def pkmn_name_to_route_one(name):
    result = name.replace(" ", "").replace("_", "").upper()
    if result == "MRMIME":
        return "MR.MIME"
    elif result == "FARFETCHD":
        return "FARFETCH'D"
    return result


def move_name_to_route_one(name):
    result = name.replace(" ", "").replace("_", "").upper()
    # TODO: any special cases with the moves?
    return result

def vitamin_to_route_one(vit):
    return vit.replace(" ", "").lower()


def generate_config_file(route: Router, config_path, route_path, out_path):
    ro_config = configparser.ConfigParser()
    ro_config.optionxform=str
    ro_config["game"] = {"game": "yellow"}
    ro_config["util"] = {
        "printxitems": True,
        "printrarecandies": True,
        "printstatboosters": True,
    }
    ro_config["files"] = {
        "routeFile": route_path,
        "outputFile": out_path,
    }

    solo_pkmn = route.init_route_state.solo_pkmn
    ro_config["poke"] = {
        "species": pkmn_name_to_route_one(solo_pkmn.name),
        "level": solo_pkmn.cur_level,
        "atkIV": solo_pkmn.dvs.attack,
        "defIV": solo_pkmn.dvs.defense,
        "spdIV": solo_pkmn.dvs.speed,
        "spcIV": solo_pkmn.dvs.special,
    }

    with open(config_path, 'w') as f:
        ro_config.write(f)


def _gen_learn_move_event(result:list, cur_event:EventDefinition, init_state):
    if cur_event.learn_move.destination is not None:
        # figure out the move being deleted. We might just be filling an unused slot, so be careful
        cur_move = init_state.solo_pkmn.move_list[cur_event.learn_move.destination]
        if cur_move:
            result.append(f"um {move_name_to_route_one(cur_move)}")
        result.append(f"lm {move_name_to_route_one(cur_event.learn_move.move_to_learn)}")
        result.append("")

def generate_route_file(route: Router, route_path):
    result = []

    for cur_folder in route.event_folders:
        for cur_group in cur_folder.event_groups:
            cur_event:EventDefinition = cur_group.event_definition
            if cur_event.trainer_name:
                result.append(f"// {cur_event.trainer_name}")
                trainer_out_line = cur_event.get_trainer_obj().route_one_offset
                if cur_event.trainer_name in const.MAJOR_FIGHTS:
                    trainer_out_line += " -v 2"
                result.append(trainer_out_line)
                result.append("")
            elif cur_event.wild_pkmn_info is not None:
                pkmn = cur_event.get_wild_pkmn()
                result.append(f"L{pkmn.level} {pkmn_name_to_route_one(pkmn.name)}")
                result.append("")
            elif cur_event.learn_move is not None:
                _gen_learn_move_event(result, cur_event, cur_group.init_state)
            elif cur_event.rare_candy is not None:
                for _ in range(cur_event.rare_candy.amount):
                    result.append(f"rc")
                result.append("")
            elif cur_event.vitamin is not None:
                for _ in range(cur_event.vitamin.amount):
                    result.append(f"{vitamin_to_route_one(cur_event.vitamin.vitamin)}")
                result.append("")

            for cur_item in cur_group.event_items:
                # make sure we handle the level up moves too
                item_event:EventDefinition = cur_item.event_definition
                if item_event != cur_event and item_event.learn_move is not None:
                    _gen_learn_move_event(result, item_event, cur_item.init_state)
    
    with open(route_path, 'w') as f:
        f.write("\n".join(result))


def export_to_route_one(route: Router, name):
    if not os.path.exists(const.ROUTE_ONE_OUTPUT_PATH):
        os.mkdir(const.ROUTE_ONE_OUTPUT_PATH)

    config_file_path = os.path.join(const.ROUTE_ONE_OUTPUT_PATH, f"{name}_config.ini")
    route_file_path = os.path.join(const.ROUTE_ONE_OUTPUT_PATH, f"{name}_route.txt")
    output_file_path = os.path.join(const.ROUTE_ONE_OUTPUT_PATH, f"{name}_out.txt")

    generate_config_file(route, config_file_path, route_file_path, output_file_path)
    generate_route_file(route, route_file_path)

    return config_file_path, route_file_path, output_file_path