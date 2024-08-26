
import argparse
import csv
import os

from controllers.main_controller import MainController
from pkmn.universal_data_objects import Nature
from utils.constants import const
from utils import setup, custom_logging
from pkmn import gen_factory


def calc_speed_tiers(route_file_path, controller:MainController):
    # step one, load the route file
    # step two, create a fake-mon
    # for each growth rate:
    #   for each valid nature (speed lowering, neutral, speed raising):
    #       for each speed from 5-100:
    #           load the fake-mon into the route file
    #           iterate over every event in the route
    #           save the speed at the start of every major fight
    #       generate a csv for the current growth rate/nature combo, of the speeds at each fight for each speed value

    controller.load_route(args.route_file)
    base_version = controller.get_version()
    result_dir = os.path.dirname(route_file_path)

    # TODO: no idea what changing the data for a mon in the db will do... Intentionally using a mon with no trainers to avoid wonkiness
    base_mon = gen_factory.current_gen_info().pkmn_db().get_pkmn("Mew")
    growth_rates = [
        const.GROWTH_RATE_FAST,
        const.GROWTH_RATE_MEDIUM_FAST,
        const.GROWTH_RATE_MEDIUM_SLOW,
        const.GROWTH_RATE_SLOW,
        const.GROWTH_RATE_ERRATIC,
        const.GROWTH_RATE_FLUCTUATING,
    ]

    for cur_growth_rate in growth_rates:
        base_mon.growth_rate = cur_growth_rate
        for cur_nature, cur_nature_name in [(Nature.HARDY, "neutral"), (Nature.BRAVE, "speed_lowering"), (Nature.TIMID, "speed_raising")]:
            header_line = ["base_speed"]
            result_data = [
                header_line
            ]
            for cur_base_speed in range(5, 105, 5):
                base_mon.stats.speed = cur_base_speed
                cur_data_line = [cur_base_speed]
                result_data.append(cur_data_line)
                controller.create_new_route(
                    base_mon.name,
                    route_file_path,
                    base_version,
                    custom_nature=cur_nature
                )

                cur_event = controller.get_next_event(enabled_only=True)
                while not (cur_event is None):
                    if cur_event.is_major_fight():
                        if cur_base_speed == 5:
                            header_line.append(cur_event.event_definition.get_first_trainer_obj().name)
                        cur_data_line.append(cur_event.init_state.solo_pkmn.cur_stats.speed)
                    cur_event = controller.get_next_event(cur_event_id=cur_event.group_id, enabled_only=True)

            out_path = os.path.join(result_dir, f"{cur_growth_rate}_{cur_nature_name}.csv")
            print(f"generating csv: {out_path}")
            with open(out_path, 'w') as f:
                cur_writer = csv.writer(f)
                for cur_row in result_data:
                    cur_writer.writerow(cur_row)





if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--route_file", required=True)
    args = parser.parse_args()

    custom_logging.config_logging(const.GLOBAL_CONFIG_DIR)
    setup.init_base_generations()
    controller = MainController()

    calc_speed_tiers(args.route_file, controller)

