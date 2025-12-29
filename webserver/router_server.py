import os
import signal

from flask import Flask, request

from utils.constants import const
from controllers.main_controller import MainController
from controllers.battle_summary_controller import BattleSummaryController
from route_recording.recorder import RecorderController
from routing.route_events import EventDefinition, LearnMoveEventDefinition
from webserver.server_utils import deseralize_json, parse_bool_int, parse_int, parse_int_list, parse_nature_int, parse_str, parse_str_list, simple_result, validate_raw_stat_block


_server = Flask(__name__)
_controller:MainController = None
_battle_controller:BattleSummaryController = None
_recorder_controller:RecorderController = None


def spawn_server(
    controller:MainController,
    battle_controller:BattleSummaryController,
    recorder_controller:RecorderController,
    port:int,
):
    global _controller
    _controller = controller

    global _battle_controller
    _battle_controller = battle_controller

    global _recorder_controller
    _recorder_controller = recorder_controller

    _server.run(port=port)


#####
# Helper endpoints
#####


@_server.route("/shutdown", methods=["POST"])
def shutdown():
    os.kill(os.getpid(), signal.SIGINT)
    return {}


#####
# Main controller endpoints
#####


@_server.route("/select_events", methods=["POST"])
def select_events():
    _controller.select_new_events(
        parse_int_list("event_ids"),
    )
    return {}


@_server.route("/set_preview_trainer", methods=["POST"])
def set_preview_trainer():
    _controller.set_preview_trainer(
        parse_str("trainer_name", optional=False),
    )
    return {}


@_server.route("/update_existing_event", methods=["POST"])
def update_existing_event():
    _controller.update_existing_event(
        parse_int("event_group_id", optional=False),
        deseralize_json(EventDefinition),
    )
    return {}


@_server.route("/update_levelup_move", methods=["POST"])
def update_levelup_move():
    _controller.update_levelup_move(
        deseralize_json(LearnMoveEventDefinition)
    )
    return {}


@_server.route("/add_area", methods=["POST"])
def add_area():
    _controller.update_levelup_move(
        parse_str("area_name", optional=False),
        parse_bool_int("include_rematches"),
        parse_int("insert_after_id", optional=False),
    )
    return {}


@_server.route("/update_levelup_move", methods=["POST"])
def create_new_route():
    _controller.update_levelup_move(
        parse_str("solo_mon", optional=False),
        parse_str("base_route_path", default=None),
        parse_str("pkmn_version", default=None),
        validate_raw_stat_block(request.json),
        parse_int("custom_ability_idx"),
        parse_nature_int("custom_nature"),
    )
    return {}


@_server.route("/load_route", methods=["POST"])
def load_route():
    _controller.load_route(
        parse_str("full_path_to_route", optional=False),
    )
    return {}


@_server.route("/customize_innate_stats", methods=["POST"])
def customize_innate_stats():
    _controller.customize_innate_stats(
        validate_raw_stat_block(request.json, optional=False),
        parse_int("new_ability", optional=False),
        parse_nature_int("new_nature", optional=False),
    )
    return {}


@_server.route("/move_groups_up", methods=["POST"])
def move_groups_up():
    _controller.move_groups_up(
        parse_int_list("event_ids"),
    )
    return {}


@_server.route("/move_groups_down", methods=["POST"])
def move_groups_down():
    _controller.move_groups_down(
        parse_int_list("event_ids"),
    )
    return {}


@_server.route("/delete_events", methods=["POST"])
def delete_events():
    _controller.delete_events(
        parse_int_list("event_ids"),
    )
    return {}


@_server.route("/purge_empty_folders", methods=["POST"])
def purge_empty_folders():
    _controller.purge_empty_folders()
    return {}


@_server.route("/transfer_to_folder", methods=["POST"])
def transfer_to_folder():
    _controller.transfer_to_folder()
    return {}


@_server.route("/new_event", methods=["POST"])
def new_event():
    _controller.new_event(
        deseralize_json(EventDefinition),
        insert_after=parse_int("insert_after"),
        insert_before=parse_int("insert_before"),
        dest_folder_name=parse_int("dest_folder_name", default=const.ROOT_FOLDER_NAME),
        do_select=parse_int("do_select", default=True),
    )
    return {}


@_server.route("/finalize_new_folder", methods=["POST"])
def finalize_new_folder():
    _controller.finalize_new_folder(
        parse_str("new_folder_name", optional=False),
        prev_folder_name=parse_str("prev_folder_name"),
        insert_after=parse_int("insert_after", default=None),
    )
    return {}


@_server.route("/toggle_event_highlight", methods=["POST"])
def toggle_event_highlight():
    _controller.toggle_event_highlight(
        parse_int_list("event_ids"),
    )
    return {}


@_server.route("/set_record_mode", methods=["POST"])
def set_record_mode():
    _controller.set_record_mode(
        parse_bool_int("new_record_mode"),
    )
    return {}


@_server.route("/set_route_filter_types", methods=["POST"])
def set_route_filter_types():
    _controller.set_route_filter_types(
        [x.strip() for x in parse_str("filter_options", default="").split(",") if x.strip()],
    )
    return {}


@_server.route("/set_route_search", methods=["POST"])
def set_route_search():
    _controller.set_route_search(
        parse_str("search", optional=False),
    )
    return {}


@_server.route("/load_all_custom_versions", methods=["POST"])
def load_all_custom_versions():
    _controller.load_all_custom_versions()
    return {}


@_server.route("/create_custom_version", methods=["POST"])
def create_custom_version():
    _controller.create_custom_version(
        parse_str("base_version", optional=False),
        parse_str("custom_version", optional=False),
    )
    return {}


@_server.route("/send_message", methods=["POST"])
def send_message():
    _controller.send_message(
        parse_str("message", optional=False),
    )
    return {}


@_server.route("/trigger_exception", methods=["POST"])
def trigger_exception():
    _controller.trigger_exception(
        parse_str("exception_message", optional=False),
    )
    return {}


@_server.route("/set_current_route_name", methods=["POST"])
def set_current_route_name():
    _controller.set_current_route_name(
        parse_str("new_name", optional=False),
    )
    return {}


@_server.route("/save_route", methods=["POST"])
def save_route():
    _controller.save_route(
        parse_str("route_name", optional=False),
    )
    return {}


@_server.route("/export_notes", methods=["POST"])
def export_notes():
    _controller.export_notes(
        parse_str("route_name", optional=False),
    )
    return {}


@_server.route("/get_raw_route", methods=["GET"])
def get_raw_route():
    return _controller.get_raw_route().serialize_metadata(
        deep=parse_bool_int("deep")
    ), 200


@_server.route("/get_current_route_name", methods=["GET"])
def get_current_route_name():
    return simple_result(
        _controller.get_current_route_name()
    )


@_server.route("/get_preview_event", methods=["GET"])
def get_preview_event():
    result = _controller.get_preview_event()
    if result is None:
        return {}, 200

    return result.serialize(), 200


@_server.route("/get_event_by_id", methods=["GET"])
def get_event_by_id():
    return _controller.get_event_by_id(
        parse_int("event_id")
    ).serialize_metadata(
        deep=parse_bool_int("deep")
    ), 200


@_server.route("/has_errors", methods=["GET"])
def has_errors():
    return simple_result(_controller.has_errors())


@_server.route("/get_version", methods=["GET"])
def get_version():
    return simple_result(_controller.has_errors())


@_server.route("/get_state_after", methods=["GET"])
def get_state_after():
    return simple_result(
        _controller.get_state_after(
            previous_event_id=parse_int("previous_event_id"),
        ).serialize()
    )


@_server.route("/get_init_state", methods=["GET"])
def get_init_state():
    return simple_result(_controller.get_init_state().serialize())


@_server.route("/get_final_state", methods=["GET"])
def get_final_state():
    return simple_result(_controller.get_final_state().serialize())


@_server.route("/get_all_folder_names", methods=["GET"])
def get_all_folder_names():
    return simple_result(_controller.get_all_folder_names())


@_server.route("/get_invalid_folders", methods=["GET"])
def get_invalid_folders():
    return simple_result(
        _controller.get_invalid_folders(
            parse_int("event_id")
        )
    )


@_server.route("/get_dvs", methods=["GET"])
def get_dvs():
    return simple_result(_controller.get_dvs().serialize())


@_server.route("/get_ability_idx", methods=["GET"])
def get_ability_idx():
    return simple_result(_controller.get_ability_idx())


@_server.route("/get_ability", methods=["GET"])
def get_ability():
    return simple_result(_controller.get_ability())


@_server.route("/get_nature", methods=["GET"])
def get_nature():
    return simple_result(str(_controller.get_nature()))


@_server.route("/get_defeated_trainers", methods=["GET"])
def get_defeated_trainers():
    return simple_result(sorted(list(_controller.get_defeated_trainers())))


@_server.route("/get_route_search_string", methods=["GET"])
def get_route_search_string():
    return simple_result(_controller.get_route_search_string())


@_server.route("/get_route_filter_types", methods=["GET"])
def get_route_filter_types():
    return simple_result(_controller.get_route_filter_types())


@_server.route("/is_empty", methods=["GET"])
def is_empty():
    return simple_result(_controller.is_empty())


@_server.route("/is_valid_levelup_move", methods=["GET"])
def is_valid_levelup_move():
    return simple_result(
        _controller.is_valid_levelup_move(
            deseralize_json(LearnMoveEventDefinition)
        )
    )


@_server.route("/can_evolve_into", methods=["GET"])
def can_evolve_into():
    return simple_result(
        _controller.can_evolve_into(
            parse_str("species_name", optional=False),
        )
    )


@_server.route("/has_unsaved_changes", methods=["GET"])
def has_unsaved_changes():
    return simple_result(_controller.has_unsaved_changes())


@_server.route("/get_all_selected_ids", methods=["GET"])
def get_all_selected_ids():
    return simple_result(
        _controller.get_all_selected_ids(
            allow_event_items=parse_bool_int("allow_event_items", default=True)
        )
    )


@_server.route("/get_single_selected_event_id", methods=["GET"])
def get_single_selected_event_id():
    return simple_result(
        _controller.get_single_selected_event_id(
            allow_event_items=parse_bool_int("allow_event_items", default=True)
        )
    )


@_server.route("/get_single_selected_event_obj", methods=["GET"])
def get_single_selected_event_obj():
    result = _controller.get_single_selected_event_obj(
        allow_event_items=parse_bool_int("allow_event_items", default=True)
    )

    if not result:
        return {}, 200

    return result.serialize_metadata(deep=parse_bool_int("deep")), 200


@_server.route("/get_active_state", methods=["GET"])
def get_active_state():
    return _controller.get_active_state().serialize(), 200


@_server.route("/can_insert_after_current_selection", methods=["GET"])
def can_insert_after_current_selection():
    return simple_result(_controller.can_insert_after_current_selection())


@_server.route("/is_record_mode_active", methods=["GET"])
def is_record_mode_active():
    return simple_result(_controller.is_record_mode_active())


@_server.route("/get_move_idx", methods=["GET"])
def get_move_idx():
    return simple_result(
        _controller.get_move_idx(
            parse_str("move_name", optional=False)
        )
    )


@_server.route("/get_next_event", methods=["GET"])
def get_next_event():
    return _controller.get_next_event(
        cur_event_id=parse_int("cur_event_id"),
        enabled_only=parse_int("enabled_only", default=False),
    ).serialize(), 200


@_server.route("/get_previous_event", methods=["GET"])
def get_previous_event():
    return _controller.get_previous_event(
        cur_event_id=parse_int("cur_event_id"),
        enabled_only=parse_int("enabled_only", default=False),
    ).serialize(), 200


#####
# Battle controller endpoints
#####

@_server.route("/battle_load", methods=["POST"])
def battle_load():
    full_event = _controller.get_event_by_id(parse_int("event_id"))

    if full_event is None:
        _battle_controller.load_empty()
    else:
        _battle_controller.load_from_event(full_event)

    return {}


@_server.route("/battle_update_mimic_selection", methods=["POST"])
def battle_update_mimic_selection():
    _battle_controller.update_mimic_selection(parse_str("new_value", optional=False))
    return {}


@_server.route("/battle_update_custom_move_data", methods=["POST"])
def battle_update_custom_move_data():
    _battle_controller.update_custom_move_data(
        parse_int("pkmn_idx", optional=False),
        parse_int("move_idx", optional=False),
        parse_bool_int("is_player_mon", optional=False),
        parse_str("ne_value", optional=False),
    )
    return {}


@_server.route("/battle_update_weather", methods=["POST"])
def battle_update_weather():
    _battle_controller.update_weather(
        parse_str("new_weather", optional=False),
    )
    return {}


@_server.route("/battle_update_enemy_setup_moves", methods=["POST"])
def battle_update_enemy_setup_moves():
    _battle_controller.update_enemy_setup_moves(
        parse_str_list("new_setup_moves", optional=False),
    )
    return {}


@_server.route("/battle_update_player_setup_moves", methods=["POST"])
def battle_update_player_setup_moves():
    _battle_controller.update_player_setup_moves(
        parse_str_list("new_setup_moves", optional=False),
    )
    return {}


@_server.route("/battle_update_enemy_field_moves", methods=["POST"])
def battle_update_enemy_field_moves():
    _battle_controller.update_enemy_field_moves(
        parse_str_list("new_field_moves", optional=False),
    )
    return {}


@_server.route("/battle_update_player_field_moves", methods=["POST"])
def battle_update_player_field_moves():
    _battle_controller.update_player_field_moves(
        parse_str_list("new_field_moves", optional=False),
    )
    return {}


@_server.route("/battle_update_player_transform", methods=["POST"])
def battle_update_player_transform():
    _battle_controller.update_player_transform(
        parse_bool_int("is_transformed", optional=False),
    )
    return {}


@_server.route("/battle_update_prefight_candies", methods=["POST"])
def battle_update_prefight_candies():
    _battle_controller.update_prefight_candies(
        parse_int("num_candies", optional=False),
    )
    return {}


@_server.route("/battle_update_player_strategy", methods=["POST"])
def battle_update_player_strategy():
    _battle_controller.update_player_strategy(
        parse_str("strat", optional=False),
    )
    return {}


@_server.route("/battle_update_enemy_strategy", methods=["POST"])
def battle_update_enemy_strategy():
    _battle_controller.update_enemy_strategy(
        parse_str("strat", optional=False),
    )
    return {}


@_server.route("/battle_update_consistent_threshold", methods=["POST"])
def battle_update_consistent_threshold():
    _battle_controller.update_consistent_threshold(
        parse_int("threshold", optional=False),
    )
    return {}


@_server.route("/battle_get_partial_trainer_definition", methods=["GET"])
def battle_get_partial_trainer_definition():
    return _battle_controller.get_partial_trainer_definition().serialize(), 200


def _get_full_mon(pkmn_idx, is_player_mon):
    result = _battle_controller.get_pkmn_info(pkmn_idx, is_player_mon)
    if result is None:
        return {}

    result = result.serialize()
    result["move_info"] = [
        _battle_controller.get_move_info(
            pkmn_idx,
            move_idx,
            is_player_mon
        ).serialize() for move_idx in range(4)
    ]

    return result


@_server.route("/battle_get_pkmn_info", methods=["GET"])
def battle_get_pkmn_info():
    return _get_full_mon(
        parse_int("pkmn_idx", optional=False),
        parse_bool_int("is_player_mon", optional=False),
    ), 200


@_server.route("/battle_get_move_info", methods=["GET"])
def battle_get_move_info():
    result = _battle_controller.get_move_info(
        parse_int("pkmn_idx", optional=False),
        parse_int("move_idx", optional=False),
        parse_bool_int("is_player_mon", optional=False),
    )

    if result is None:
        return {}, 200

    return result.serialize(), 200

@_server.route("/battle_get_full_summary", methods=["GET"])
def battle_get_full_summary():
    return {
        "player_pkmn": [_get_full_mon(x, True) for x in range(6)],
        "enemy_pkmn": [_get_full_mon(x, False) for x in range(6)],
    }, 200


@_server.route("/battle_get_weather", methods=["GET"])
def battle_get_weather():
    return simple_result(_battle_controller.get_weather())


@_server.route("/battle_get_player_setup_moves", methods=["GET"])
def battle_get_player_setup_moves():
    return simple_result(_battle_controller.get_player_setup_moves())


@_server.route("/battle_get_enemy_setup_moves", methods=["GET"])
def battle_get_enemy_setup_moves():
    return simple_result(_battle_controller.get_enemy_setup_moves())


@_server.route("/battle_get_player_field_moves", methods=["GET"])
def battle_get_player_field_moves():
    return simple_result(_battle_controller.get_player_field_moves())


@_server.route("/battle_get_enemy_field_moves", methods=["GET"])
def battle_get_enemy_field_moves():
    return simple_result(_battle_controller.get_enemy_field_moves())


@_server.route("/battle_is_double_battle", methods=["GET"])
def battle_is_double_battle():
    return simple_result(_battle_controller.is_double_battle())


@_server.route("/battle_is_player_transformed", methods=["GET"])
def battle_is_player_transformed():
    return simple_result(_battle_controller.is_player_transformed())


@_server.route("/battle_get_prefight_candy_count", methods=["GET"])
def battle_get_prefight_candy_count():
    return simple_result(_battle_controller.get_prefight_candy_count())


#####
# Recorder controller endpoints
#####


@_server.route("/recorder_get_status", methods=["GET"])
def recorder_get_status():
    return simple_result(_recorder_controller.get_status())


@_server.route("/recorder_is_ready", methods=["GET"])
def recorder_is_ready():
    return simple_result(_recorder_controller.is_ready())


@_server.route("/recorder_get_game_state", methods=["GET"])
def recorder_get_game_state():
    return simple_result(_recorder_controller.is_ready())
